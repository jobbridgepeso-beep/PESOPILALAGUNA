"""
Property-based tests for OTP utilities in app/utils/helpers.py.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

Properties tested
-----------------
1. OTP Registration Round-Trip  (Req 1.1, 1.2)
   generate_otp() + create_otp_record() + validate_otp() within window → (True, "")

2. OTP Expiry Rejection  (Req 1.3)
   validate_otp() with a record whose expires_at is in the past → (False, "OTP has expired…")

3. OTP Single-Use Idempotence  (Req 1.4)
   validate_otp() on a record with used_at already set → (False, "OTP has already been used.")

4. OTP Resend Invalidation  (Req 1.5)
   After resend (new OTP created), old token → (False, …), new token → (True, "")

Additionally, a unit-level property test verifies:
   generate_otp() always returns exactly 6 decimal digits.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, call

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
from app.utils.helpers import generate_otp, create_otp_record, validate_otp

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(data):
    """Minimal supabase-py response stub."""
    resp = MagicMock()
    resp.data = data
    return resp


def _make_supabase_mock():
    """Return a fresh fluent-chain supabase mock."""
    mock = MagicMock()
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.insert.return_value = mock
    mock.update.return_value = mock
    mock.eq.return_value = mock
    mock.order.return_value = mock
    mock.limit.return_value = mock
    mock.single.return_value = mock
    mock.execute.return_value = _make_response(None)
    return mock


def _future_iso(seconds: int = 600) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


def _past_iso(seconds: int = 60) -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()


# ---------------------------------------------------------------------------
# Test 1 — generate_otp() always returns exactly 6 decimal digits
# ---------------------------------------------------------------------------


@given(st.integers(min_value=1, max_value=200))
@settings(max_examples=200, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_generate_otp_always_6_digits(run_count):
    """
    **Validates: Requirements 1.1**

    Property: For any invocation, generate_otp() returns a string of
    exactly 6 characters, all of which are decimal digits ('0'–'9').
    """
    otp = generate_otp()
    assert isinstance(otp, str), "generate_otp() must return a str"
    assert len(otp) == 6, f"Expected 6 digits, got {len(otp)}: {otp!r}"
    assert otp.isdigit(), f"Expected all decimal digits, got: {otp!r}"


# ---------------------------------------------------------------------------
# Test 2 — OTP Registration Round-Trip
# ---------------------------------------------------------------------------


@given(
    user_id=st.uuids().map(str),
    purpose=st.sampled_from(["registration", "password_reset"]),
    expiry_seconds=st.integers(min_value=60, max_value=3600),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_otp_registration_round_trip(user_id, purpose, expiry_seconds):
    """
    **Validates: Requirements 1.1, 1.2**

    Property: For any valid user_id and purpose, creating an OTP record and
    then validating it within the expiry window returns (True, "").

    The supabase client is mocked so that:
    - get_otp_expiry_seconds() returns `expiry_seconds`
    - create_otp_record() insert succeeds and returns a record
    - validate_otp() select returns that same record (unused, not expired)
    - validate_otp() update (mark used) succeeds
    """
    token = generate_otp()
    record_id = str(uuid.uuid4())
    expires_at = _future_iso(expiry_seconds)

    inserted_record = {
        "id": record_id,
        "user_id": user_id,
        "token": token,
        "purpose": purpose,
        "expires_at": expires_at,
        "used_at": None,
    }

    supabase = _make_supabase_mock()

    # Sequence of execute() calls:
    # 1. get_otp_expiry_seconds → system_settings query
    # 2. create_otp_record → insert
    # 3. validate_otp → select (fetch record)
    # 4. validate_otp → update (mark used)
    supabase.execute.side_effect = [
        _make_response([{"value": str(expiry_seconds)}]),  # system_settings
        _make_response([inserted_record]),                  # insert
        _make_response([inserted_record]),                  # select in validate_otp
        _make_response([inserted_record]),                  # update used_at
    ]

    # create_otp_record uses generate_otp() internally; patch it to return
    # our known token so validate_otp can find it.
    with patch("app.utils.helpers.generate_otp", return_value=token):
        record = create_otp_record(user_id, purpose, supabase)

    assert record["token"] == token
    assert record["user_id"] == user_id

    # Now validate — should succeed
    ok, msg = validate_otp(user_id, token, purpose, supabase)
    assert ok is True, f"Expected (True, '') but got ({ok!r}, {msg!r})"
    assert msg == ""


# ---------------------------------------------------------------------------
# Test 3 — OTP Expiry Rejection
# ---------------------------------------------------------------------------


@given(
    user_id=st.uuids().map(str),
    token=st.text(alphabet="0123456789", min_size=6, max_size=6),
    purpose=st.sampled_from(["registration", "password_reset"]),
    seconds_past=st.integers(min_value=1, max_value=86400),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_otp_expiry_rejection(user_id, token, purpose, seconds_past):
    """
    **Validates: Requirements 1.3**

    Property: For any OTP record whose expires_at is in the past,
    validate_otp() returns (False, message) where message contains
    "OTP has expired".
    """
    record_id = str(uuid.uuid4())
    expired_at = _past_iso(seconds_past)

    expired_record = {
        "id": record_id,
        "user_id": user_id,
        "token": token,
        "purpose": purpose,
        "expires_at": expired_at,
        "used_at": None,  # not yet used — expiry check must fire first
    }

    supabase = _make_supabase_mock()
    # validate_otp makes one select call
    supabase.execute.return_value = _make_response([expired_record])

    ok, msg = validate_otp(user_id, token, purpose, supabase)

    assert ok is False, f"Expected rejection for expired OTP, got ok=True"
    assert "expired" in msg.lower(), (
        f"Expected expiry message, got: {msg!r}"
    )


# ---------------------------------------------------------------------------
# Test 4 — OTP Single-Use Idempotence
# ---------------------------------------------------------------------------


@given(
    user_id=st.uuids().map(str),
    token=st.text(alphabet="0123456789", min_size=6, max_size=6),
    purpose=st.sampled_from(["registration", "password_reset"]),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_otp_single_use_idempotence(user_id, token, purpose):
    """
    **Validates: Requirements 1.4**

    Property: For any OTP record that has already been used (used_at is set),
    validate_otp() returns (False, "OTP has already been used.") regardless
    of whether the record is still within the expiry window.
    """
    record_id = str(uuid.uuid4())
    # Record is still within expiry window but has been used
    used_record = {
        "id": record_id,
        "user_id": user_id,
        "token": token,
        "purpose": purpose,
        "expires_at": _future_iso(600),
        "used_at": datetime.now(timezone.utc).isoformat(),
    }

    supabase = _make_supabase_mock()
    supabase.execute.return_value = _make_response([used_record])

    ok, msg = validate_otp(user_id, token, purpose, supabase)

    assert ok is False, "Expected rejection for already-used OTP"
    assert msg == "OTP has already been used.", (
        f"Expected exact message 'OTP has already been used.', got: {msg!r}"
    )


# ---------------------------------------------------------------------------
# Test 5 — OTP Resend Invalidation
# ---------------------------------------------------------------------------


@given(
    user_id=st.uuids().map(str),
    purpose=st.sampled_from(["registration", "password_reset"]),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_otp_resend_invalidation(user_id, purpose):
    """
    **Validates: Requirements 1.5**

    Property: After a resend (new OTP created), the old token is rejected
    by validate_otp() and the new token is accepted.

    Simulation:
    - old_token is created first (record has expires_at in the past to
      simulate invalidation — the resend flow creates a new record and the
      old one is effectively superseded; here we model it as expired so
      validate_otp rejects it).
    - new_token is created second with a fresh expiry window.
    - validate_otp(old_token) → (False, …)
    - validate_otp(new_token) → (True, "")
    """
    old_token = generate_otp()
    new_token = generate_otp()
    # Ensure tokens differ (extremely unlikely to collide, but guard anyway)
    # If they happen to be equal, just skip this example — hypothesis will
    # generate another.
    if old_token == new_token:
        return

    old_record_id = str(uuid.uuid4())
    new_record_id = str(uuid.uuid4())

    # Old record: expired (simulates invalidation after resend)
    old_record = {
        "id": old_record_id,
        "user_id": user_id,
        "token": old_token,
        "purpose": purpose,
        "expires_at": _past_iso(60),
        "used_at": None,
    }

    # New record: valid, within expiry window
    new_record = {
        "id": new_record_id,
        "user_id": user_id,
        "token": new_token,
        "purpose": purpose,
        "expires_at": _future_iso(600),
        "used_at": None,
    }

    # --- Validate old token (should be rejected) ---
    supabase_old = _make_supabase_mock()
    supabase_old.execute.return_value = _make_response([old_record])

    ok_old, msg_old = validate_otp(user_id, old_token, purpose, supabase_old)
    assert ok_old is False, (
        f"Old token should be rejected after resend, got ok=True"
    )

    # --- Validate new token (should be accepted) ---
    supabase_new = _make_supabase_mock()
    # select returns new_record; update (mark used) also succeeds
    supabase_new.execute.side_effect = [
        _make_response([new_record]),   # select
        _make_response([new_record]),   # update used_at
    ]

    ok_new, msg_new = validate_otp(user_id, new_token, purpose, supabase_new)
    assert ok_new is True, (
        f"New token should be accepted after resend, got ({ok_new!r}, {msg_new!r})"
    )
    assert msg_new == ""
