"""
OTP, token, and password helper utilities for the JobBridge application.

Provides:
  - generate_otp()           — random 6-digit string (zero-padded)
  - get_otp_expiry_seconds() — reads otp_expiry from system_settings, defaults to 600
  - create_otp_record()      — inserts a new OTP record into otp_tokens via supabase-py
  - validate_otp()           — checks existence, expiry, and used_at; marks used on success
  - hash_password()          — bcrypt hash with cost factor 12
  - verify_password()        — bcrypt.checkpw comparison
"""

from __future__ import annotations

import random
import string
from datetime import datetime, timezone, timedelta
from typing import Any

import bcrypt

# ---------------------------------------------------------------------------
# OTP generation
# ---------------------------------------------------------------------------


def generate_otp() -> str:
    """Return a random 6-digit string, zero-padded (e.g. '042817').

    Uses ``random.SystemRandom`` which is backed by the OS CSPRNG so the
    output is suitable for security-sensitive one-time passwords.
    """
    rng = random.SystemRandom()
    return "".join(rng.choices(string.digits, k=6))


# ---------------------------------------------------------------------------
# System settings helper
# ---------------------------------------------------------------------------


def get_otp_expiry_seconds(supabase_client) -> int:
    """Read the ``otp_expiry`` key from the ``system_settings`` table.

    Returns the integer value stored there, or 600 (10 minutes) if the key
    is absent or the query fails.

    Args:
        supabase_client: An initialised ``supabase.Client`` instance.

    Returns:
        OTP lifetime in seconds.
    """
    try:
        response = (
            supabase_client.table("system_settings")
            .select("value")
            .eq("key", "otp_expiry")
            .single()
            .execute()
        )
        if response.data and response.data.get("value"):
            return int(response.data["value"])
    except Exception:
        pass
    return 600


# ---------------------------------------------------------------------------
# OTP record management
# ---------------------------------------------------------------------------


def create_otp_record(user_id: str, purpose: str, supabase_client) -> dict[str, Any]:
    """Insert a new OTP record into the ``otp_tokens`` table.

    Generates a fresh 6-digit OTP, computes the expiry timestamp using the
    ``otp_expiry`` system setting, and inserts the record.

    Args:
        user_id:         UUID string of the user this OTP belongs to.
        purpose:         One of ``'registration'`` or ``'password_reset'``.
        supabase_client: An initialised ``supabase.Client`` instance.

    Returns:
        The inserted row as a dict (as returned by supabase-py).

    Raises:
        RuntimeError: If the insert fails.
    """
    token = generate_otp()
    expiry_seconds = get_otp_expiry_seconds(supabase_client)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds)

    payload = {
        "user_id": user_id,
        "token": token,
        "purpose": purpose,
        "expires_at": expires_at.isoformat(),
        # used_at is intentionally omitted — defaults to NULL in the DB
    }

    response = (
        supabase_client.table("otp_tokens")
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            f"Failed to create OTP record for user_id={user_id}: no data returned."
        )

    return response.data[0]


def validate_otp(
    user_id: str,
    token: str,
    purpose: str,
    supabase_client,
) -> tuple[bool, str]:
    """Validate an OTP submission and mark it as used on success.

    Checks (in order):
      1. A matching, unused record exists for the given user_id, token, and purpose.
      2. The record has not expired (``expires_at > now()``).
      3. The record has not already been used (``used_at IS NULL``).

    If all checks pass the record's ``used_at`` is set to the current UTC
    timestamp so the OTP cannot be reused.

    Args:
        user_id:         UUID string of the user submitting the OTP.
        token:           The 6-digit OTP string submitted by the user.
        purpose:         Expected purpose (``'registration'`` or ``'password_reset'``).
        supabase_client: An initialised ``supabase.Client`` instance.

    Returns:
        ``(True, "")`` on success.
        ``(False, error_message)`` on any failure.
    """
    # ------------------------------------------------------------------
    # 1. Fetch the most recent matching record
    # ------------------------------------------------------------------
    try:
        response = (
            supabase_client.table("otp_tokens")
            .select("id, expires_at, used_at")
            .eq("user_id", user_id)
            .eq("token", token)
            .eq("purpose", purpose)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        return False, f"OTP lookup failed: {exc}"

    if not response.data:
        return False, "Invalid OTP. Please check the code and try again."

    record = response.data[0]
    record_id: str = record["id"]

    # ------------------------------------------------------------------
    # 2. Check used_at (single-use enforcement)
    # ------------------------------------------------------------------
    if record.get("used_at") is not None:
        return False, "OTP has already been used."

    # ------------------------------------------------------------------
    # 3. Check expiry
    # ------------------------------------------------------------------
    expires_at_raw: str = record["expires_at"]
    # supabase-py returns ISO-8601 strings; parse to an aware datetime.
    try:
        # Handle both "+00:00" and "Z" suffixes
        expires_at_str = expires_at_raw.replace("Z", "+00:00")
        expires_at = datetime.fromisoformat(expires_at_str)
    except ValueError:
        return False, "OTP record has an invalid expiry timestamp."

    now = datetime.now(timezone.utc)
    if now > expires_at:
        return False, "OTP has expired. Please request a new one."

    # ------------------------------------------------------------------
    # 4. Mark as used
    # ------------------------------------------------------------------
    try:
        supabase_client.table("otp_tokens").update(
            {"used_at": now.isoformat()}
        ).eq("id", record_id).execute()
    except Exception as exc:
        return False, f"Failed to mark OTP as used: {exc}"

    return True, ""


# ---------------------------------------------------------------------------
# Password hashing  (Task 3.3 — Requirement 2.6)
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain* using cost factor 12.

    Args:
        plain: The plaintext password string.

    Returns:
        A bcrypt hash string (e.g. ``'$2b$12$...'``).
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the bcrypt *hashed* value.

    Args:
        plain:  The plaintext password to check.
        hashed: The stored bcrypt hash string.

    Returns:
        ``True`` if the password matches, ``False`` otherwise.
    """
    if not hashed or not hashed.startswith("$2"):
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False
