"""
Pytest fixtures for JobBridge backend tests.

Provides reusable mock objects and helpers for unit/property tests
that cannot connect to a real Supabase instance.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Supabase client mock factory
# ---------------------------------------------------------------------------


def _make_response(data):
    """Return a minimal supabase-py response mock with a .data attribute."""
    resp = MagicMock()
    resp.data = data
    return resp


def make_supabase_mock():
    """Return a MagicMock that mimics the supabase-py fluent query builder.

    The mock supports the chained call pattern used in helpers.py:
        client.table(...).select(...).eq(...).order(...).limit(...).execute()
        client.table(...).insert(...).execute()
        client.table(...).update(...).eq(...).execute()
        client.table(...).select(...).eq(...).single().execute()
    """
    mock = MagicMock()

    # Make every chained attribute return the same mock so that arbitrary
    # chains like .table().select().eq().order().limit().execute() work.
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.insert.return_value = mock
    mock.update.return_value = mock
    mock.delete.return_value = mock
    mock.eq.return_value = mock
    mock.order.return_value = mock
    mock.limit.return_value = mock
    mock.single.return_value = mock

    # Default execute() returns empty data; individual tests override this.
    mock.execute.return_value = _make_response(None)

    return mock


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def supabase_mock():
    """Provide a fresh supabase client mock for each test."""
    return make_supabase_mock()


@pytest.fixture
def sample_user_id():
    """Return a deterministic UUID string for use as a user_id in tests."""
    return str(uuid.uuid4())


@pytest.fixture
def future_expires_at():
    """Return an ISO-8601 string 10 minutes in the future (UTC)."""
    return (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()


@pytest.fixture
def past_expires_at():
    """Return an ISO-8601 string 1 minute in the past (UTC)."""
    return (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
