"""
Audit Trail Service for the JobBridge application.

Provides:
  - log() — append-only insert into the ``audit_trail`` table via supabase-py

The ``audit_trail`` table has no UPDATE or DELETE permissions granted at the
database level (enforced via RLS policies), so this service only ever inserts.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.extensions import get_supabase

logger = logging.getLogger(__name__)


def log(
    actor_id: Optional[str],
    actor_role: str,
    action_type: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Append a new entry to the ``audit_trail`` table.

    This function is intentionally fire-and-forget: any database error is
    logged but never re-raised so that a logging failure never breaks the
    primary request flow.

    Args:
        actor_id:      UUID string of the user performing the action, or
                       ``None`` for unauthenticated actions (e.g. failed login).
        actor_role:    Role of the actor (``'jobseeker'``, ``'employer'``,
                       ``'staff'``, ``'admin'``, or ``'anonymous'``).
        action_type:   Descriptive action label, e.g. ``'login'``,
                       ``'vacancy_approved'``, ``'profile_updated'``.
        resource_type: The type of resource affected, e.g. ``'job_vacancy'``,
                       ``'user'``, ``'program_application'``. Optional.
        resource_id:   UUID string of the specific resource. Optional.
        ip_address:    Client IP address string. Optional.
        metadata:      Arbitrary JSON-serialisable dict of extra context.
                       Optional.

    Returns:
        None. Errors are swallowed and logged.
    """
    payload: dict[str, Any] = {
        "actor_role": actor_role,
        "action_type": action_type,
    }

    if actor_id is not None:
        payload["actor_id"] = actor_id
    if resource_type is not None:
        payload["resource_type"] = resource_type
    if resource_id is not None:
        payload["resource_id"] = resource_id
    if ip_address is not None:
        payload["ip_address"] = ip_address
    if metadata is not None:
        payload["metadata"] = metadata

    try:
        supabase = get_supabase()
        supabase.table("audit_trail").insert(payload).execute()
        logger.debug(
            "Audit log written: actor_id=%s action_type=%s resource_type=%s",
            actor_id,
            action_type,
            resource_type,
        )
    except Exception as exc:
        logger.error(
            "Failed to write audit log: actor_id=%s action_type=%s error=%s",
            actor_id,
            action_type,
            exc,
            exc_info=True,
        )
