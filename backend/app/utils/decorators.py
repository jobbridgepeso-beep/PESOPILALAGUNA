"""
Custom Flask decorators for the JobBridge application.

Provides:
  - role_required(*roles)              — JWT role-based access control
  - audit_action(action_type, ...)     — append audit trail entry after route execution
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any

from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# role_required
# ---------------------------------------------------------------------------

def role_required(*roles: str):
    """Decorator that restricts a route to users whose JWT role claim is in *roles*.

    Usage::

        @app.route("/api/staff/dashboard")
        @role_required("staff", "admin")
        def staff_dashboard():
            ...

    Returns HTTP 403 with a standard ``{success, data, message}`` body if the
    authenticated user's role is not in the allowed set.

    Requirements: 3.1, 3.2
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Ensure a valid JWT is present (raises 401 if missing/invalid)
            verify_jwt_in_request()

            claims = get_jwt()
            user_role: str = claims.get("role", "")

            if user_role not in roles:
                return (
                    jsonify(
                        {
                            "success": False,
                            "data": None,
                            "message": "Access denied for your role.",
                        }
                    ),
                    403,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# audit_action
# ---------------------------------------------------------------------------

def audit_action(action_type: str, resource_type: str | None = None):
    """Decorator that appends an audit trail entry after a successful route execution.

    The entry is written only when the wrapped function returns a 2xx response.
    Failures (4xx / 5xx) are not audited by this decorator — they may be
    audited separately inside the route handler if needed.

    Usage::

        @app.route("/api/auth/login", methods=["POST"])
        @audit_action("login", "user")
        def login():
            ...

    The decorator reads the actor identity and role from the current JWT
    (if present). For unauthenticated routes (e.g. login) the actor_id will
    be ``None`` and actor_role will be ``"anonymous"``.

    Requirements: 17.1, 17.2
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)

            # Determine HTTP status code from the return value
            status_code: int = 200
            if isinstance(result, tuple) and len(result) >= 2:
                status_code = result[1]

            # Only audit successful responses
            if 200 <= status_code < 300:
                _write_audit_entry(action_type, resource_type)

            return result

        return wrapper

    return decorator


def _write_audit_entry(action_type: str, resource_type: str | None) -> None:
    """Write a single audit trail entry via the audit service.

    Silently swallows any exception so that audit failures never break the
    primary request flow.
    """
    try:
        # Import here to avoid circular imports at module load time
        from app.services.audit_service import log as audit_log
        from flask_jwt_extended import get_jwt, get_jwt_identity

        try:
            verify_jwt_in_request(optional=True)
            claims: dict[str, Any] = get_jwt() or {}
            actor_id: str | None = get_jwt_identity()
            actor_role: str = claims.get("role", "anonymous")
        except Exception:
            actor_id = None
            actor_role = "anonymous"

        ip_address: str = (
            request.headers.get("X-Forwarded-For", request.remote_addr) or ""
        ).split(",")[0].strip()

        audit_log(
            actor_id=actor_id,
            actor_role=actor_role,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=None,
            ip_address=ip_address or None,
            metadata=None,
        )
    except Exception as exc:
        logger.warning("audit_action decorator failed to write entry: %s", exc)
