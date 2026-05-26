"""Shared Supabase lookup helpers."""

from __future__ import annotations

from app.extensions import get_supabase


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
