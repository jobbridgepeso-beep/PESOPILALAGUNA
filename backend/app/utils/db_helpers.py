"""Shared Supabase lookup helpers."""

from __future__ import annotations

from typing import Any

from app.extensions import get_supabase


def safe_single(query) -> dict | None:
    """Return the first row from a Supabase query or None if missing.

    Avoids the PGRST116 'Cannot coerce the result to a single JSON object'
    error that ``.single()`` raises when zero rows match. Pass the builder
    *before* ``.single().execute()``; this helper handles ``.limit(1)`` and
    ``.execute()`` for you.

    Example::

        row = safe_single(
            supabase.table("users").select("id").eq("email", "x@example.com")
        )
    """
    try:
        resp = query.limit(1).execute()
    except Exception:
        return None
    data = getattr(resp, "data", None) or []
    return data[0] if data else None


def get_jobseeker_profile(user_id: str) -> dict | None:
    supabase = get_supabase()
    resp = (
        supabase.table("jobseeker_profiles")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def get_employer_profile(user_id: str) -> dict | None:
    supabase = get_supabase()
    resp = (
        supabase.table("employer_profiles")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def get_user(user_id: str) -> dict | None:
    supabase = get_supabase()
    resp = (
        supabase.table("users")
        .select("id, email, role, is_active, is_verified, first_login, created_at")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def get_user_by_email(email: str, columns: str = "*") -> dict | None:
    """Lookup user by email without .single() (avoids PGRST116 on missing rows)."""
    supabase = get_supabase()
    resp = (
        supabase.table("users")
        .select(columns)
        .eq("email", email.strip().lower())
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None
