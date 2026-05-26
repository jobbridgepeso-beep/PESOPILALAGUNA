"""
Auth blueprint route handlers — /api/auth

Endpoints:
  POST /register          — Jobseeker/Employer self-registration + OTP email
  POST /verify-otp        — OTP verification + account activation
  POST /resend-otp        — Invalidate old OTP, issue new one
  POST /login             — Issue JWT access token + refresh cookie
  POST /refresh           — Rotate access token using refresh cookie
  POST /logout            — Invalidate refresh token + clear cookie
  POST /forgot-password   — Send password-reset OTP
  POST /reset-password    — Validate OTP + update password hash

Requirements: 1.1–1.6, 2.1–2.6, 21.1–21.4
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone, timedelta

from flask import jsonify, request, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_refresh_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request,
)
from postgrest.exceptions import APIError

from app.utils.db_helpers import get_user_by_email

from app.blueprints.auth import auth_bp
from app.extensions import get_supabase
from app.services.audit_service import log as audit_log
from app.services.notification_service import send_otp_email
from app.utils.helpers import (
    create_otp_record,
    hash_password,
    validate_otp,
    verify_password,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate-limit helpers (Redis-backed, with graceful degradation)
# ---------------------------------------------------------------------------
#
# A circuit breaker keeps the app quiet when Redis isn't running locally:
# the first failure logs a single INFO line, subsequent calls short-circuit
# for ``_REDIS_RETRY_AFTER`` seconds before we try again. Rate-limiting and
# token blacklisting both fail open — they are hardening features, not
# correctness requirements, so the app keeps serving requests.
# ---------------------------------------------------------------------------

import time

_REDIS_RETRY_AFTER = 60.0  # seconds between connection attempts when down
_redis_client = None  # cached client across requests
_redis_disabled_until: float = 0.0  # epoch seconds; 0 means "try now"
_redis_warned = False  # log the "unavailable" warning only once


def _get_redis():
    """Return a cached Redis client, or ``None`` when unreachable.

    Suppresses repeated connection errors by caching a "disabled until"
    timestamp; callers should treat ``None`` as "Redis is unavailable" and
    fall back to fail-open behaviour. Honours the ``DISABLE_REDIS`` flag
    in app config to skip the connection attempt entirely.
    """
    global _redis_client, _redis_disabled_until, _redis_warned

    from flask import current_app

    if current_app.config.get("DISABLE_REDIS"):
        return None

    if _redis_disabled_until and time.monotonic() < _redis_disabled_until:
        return None

    if _redis_client is not None:
        return _redis_client

    try:
        import redis as redis_lib

        client = redis_lib.from_url(
            current_app.config["REDIS_URL"],
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        client.ping()
    except Exception as exc:
        _redis_disabled_until = time.monotonic() + _REDIS_RETRY_AFTER
        if not _redis_warned:
            logger.info(
                "Redis unavailable (%s) — rate limiting and token "
                "blacklisting will be skipped for %ss.",
                exc.__class__.__name__,
                int(_REDIS_RETRY_AFTER),
            )
            _redis_warned = True
        return None

    _redis_client = client
    _redis_disabled_until = 0.0
    return client


def _check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    """Return True if the action is allowed, False if rate-limited."""
    r = _get_redis()
    if r is None:
        return True  # fail open
    try:
        current = r.get(key)
        if current and int(current) >= limit:
            return False
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        pipe.execute()
        return True
    except Exception:
        return True


def _is_ip_locked(ip: str) -> bool:
    """Return True if the IP has exceeded the login failure threshold."""
    r = _get_redis()
    if r is None:
        return False
    try:
        count = r.get(f"login_fail:{ip}")
        return count is not None and int(count) >= 5
    except Exception:
        return False


def _record_login_failure(ip: str) -> None:
    r = _get_redis()
    if r is None:
        return
    try:
        key = f"login_fail:{ip}"
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 900)  # 15-minute window
        pipe.execute()
    except Exception:
        pass


def _clear_login_failures(ip: str) -> None:
    r = _get_redis()
    if r is None:
        return
    try:
        r.delete(f"login_fail:{ip}")
    except Exception:
        pass


def _blacklist_refresh_token(jti: str) -> None:
    r = _get_redis()
    if r is None:
        return
    try:
        r.setex(f"blacklist:{jti}", 60 * 60 * 24 * 30, "1")  # 30 days
    except Exception:
        pass


def _is_token_blacklisted(jti: str) -> bool:
    r = _get_redis()
    if r is None:
        return False
    try:
        return r.exists(f"blacklist:{jti}") == 1
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Helper: standard JSON response
# ---------------------------------------------------------------------------

def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data, "message": message}), status


def _err(message="Error", status=400, data=None):
    return jsonify({"success": False, "data": data, "message": message}), status


def _get_ip() -> str:
    return (
        request.headers.get("X-Forwarded-For", request.remote_addr) or ""
    ).split(",")[0].strip()


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new Jobseeker or Employer account.

    Requirements: 1.1, 1.6
    """
    ip = _get_ip()

    # Rate limit: 10 registrations per IP per hour
    if not _check_rate_limit(f"register:{ip}", limit=10, window_seconds=3600):
        return _err("Too many registration attempts. Please try again later.", 429)

    data = request.get_json(silent=True) or {}
    email: str = (data.get("email") or "").strip().lower()
    password: str = data.get("password") or ""
    role: str = (data.get("role") or "").strip().lower()

    # Validate required fields
    if not email or not password or not role:
        return _err("email, password, and role are required.", 422)

    if role not in ("jobseeker", "employer"):
        return _err("role must be 'jobseeker' or 'employer'.", 422)

    if len(password) < 8:
        return _err("Password must be at least 8 characters.", 422)

    supabase = get_supabase()

    # Check for existing account
    existing = (
        supabase.table("users").select("id").eq("email", email).execute()
    )
    if existing.data:
        return _err("An account with this email already exists.", 409)

    # Create user record (pending / unverified)
    password_hash = hash_password(password)
    user_payload = {
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "is_active": False,
        "is_verified": False,
        "first_login": True,
    }
    user_resp = supabase.table("users").insert(user_payload).execute()
    if not user_resp.data:
        return _err("Failed to create account. Please try again.", 500)

    user = user_resp.data[0]
    user_id: str = user["id"]

    # Create role-specific profile record
    if role == "jobseeker":
        supabase.table("jobseeker_profiles").insert({"user_id": user_id}).execute()
    elif role == "employer":
        supabase.table("employer_profiles").insert({"user_id": user_id}).execute()

    # Generate OTP and send email
    try:
        otp_record = create_otp_record(user_id, "registration", supabase)
        send_otp_email(email, otp_record["token"], "registration")
    except Exception as exc:
        logger.error("Failed to send OTP email to %s: %s", email, exc)
        # Don't fail registration — user can resend OTP

    audit_log(
        actor_id=user_id,
        actor_role=role,
        action_type="account_created",
        resource_type="user",
        resource_id=user_id,
        ip_address=ip,
    )

    return _ok(
        data={"user_id": user_id, "email": email, "role": role},
        message="Account created. Please check your email for the verification code.",
        status=201,
    )


# ---------------------------------------------------------------------------
# POST /api/auth/verify-otp
# ---------------------------------------------------------------------------

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """Verify OTP and activate the account.

    Requirements: 1.2, 1.3, 1.4
    """
    data = request.get_json(silent=True) or {}
    email: str = (data.get("email") or "").strip().lower()
    token: str = (data.get("otp") or "").strip()

    if not email or not token:
        return _err("email and otp are required.", 422)

    user = get_user_by_email(email, "id, role, is_verified")
    if not user:
        return _err("No account found with this email.", 404)

    supabase = get_supabase()
    user_id: str = user["id"]

    if user["is_verified"]:
        return _err("Account is already verified.", 409)

    valid, error_msg = validate_otp(user_id, token, "registration", supabase)
    if not valid:
        return _err(error_msg, 422)

    # Activate account
    supabase.table("users").update(
        {"is_active": True, "is_verified": True}
    ).eq("id", user_id).execute()

    audit_log(
        actor_id=user_id,
        actor_role=user["role"],
        action_type="account_verified",
        resource_type="user",
        resource_id=user_id,
        ip_address=_get_ip(),
    )

    role_dashboard = f"/{user['role']}/dashboard"
    return _ok(
        data={"redirect": role_dashboard},
        message="Account verified successfully. You can now log in.",
    )


# ---------------------------------------------------------------------------
# POST /api/auth/resend-otp
# ---------------------------------------------------------------------------

@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    """Invalidate existing OTPs and issue a fresh one.

    Requirements: 1.5
    """
    data = request.get_json(silent=True) or {}
    email: str = (data.get("email") or "").strip().lower()
    purpose: str = (data.get("purpose") or "registration").strip()

    if not email:
        return _err("email is required.", 422)

    if purpose not in ("registration", "password_reset"):
        return _err("purpose must be 'registration' or 'password_reset'.", 422)

    user = get_user_by_email(email, "id, role")
    if not user:
        # Return success to avoid email enumeration
        return _ok(message="If an account exists, a new code has been sent.")

    supabase = get_supabase()
    user_id: str = user["id"]

    # Invalidate all existing unused OTPs for this user + purpose
    now_iso = datetime.now(timezone.utc).isoformat()
    supabase.table("otp_tokens").update({"used_at": now_iso}).eq(
        "user_id", user_id
    ).eq("purpose", purpose).is_("used_at", "null").execute()

    # Issue new OTP
    try:
        otp_record = create_otp_record(user_id, purpose, supabase)
        send_otp_email(email, otp_record["token"], purpose)
    except Exception as exc:
        logger.error("Failed to resend OTP to %s: %s", email, exc)
        return _err("Failed to send verification code. Please try again.", 500)

    return _ok(message="A new verification code has been sent to your email.")


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and issue JWT + refresh cookie.

    Requirements: 2.1, 2.3
    """
    ip = _get_ip()

    # Brute-force protection
    if _is_ip_locked(ip):
        return _err(
            "Too many failed login attempts. Please try again in 15 minutes.", 429
        )

    data = request.get_json(silent=True) or {}
    email: str = (data.get("email") or "").strip().lower()
    password: str = data.get("password") or ""

    if not email or not password:
        return _err("email and password are required.", 422)

    try:
        user = get_user_by_email(
            email,
            "id, email, password_hash, role, is_active, is_verified, first_login",
        )
    except APIError as exc:
        logger.error("Login user lookup failed: %s", exc)
        return _err("Unable to sign in right now. Please try again.", 500)

    if not user:
        _record_login_failure(ip)
        return _err("Invalid email or password.", 401)

    if not verify_password(password, user["password_hash"]):
        _record_login_failure(ip)
        return _err("Invalid email or password.", 401)

    if not user["is_verified"]:
        return _err("Please verify your email before logging in.", 403)

    if not user["is_active"]:
        return _err("Your account has been deactivated. Please contact PESO Staff.", 403)

    _clear_login_failures(ip)

    # Build JWT claims
    additional_claims = {
        "role": user["role"],
        "email": user["email"],
        "first_login": user["first_login"],
    }
    access_token = create_access_token(
        identity=user["id"], additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=user["id"], additional_claims=additional_claims
    )

    audit_log(
        actor_id=user["id"],
        actor_role=user["role"],
        action_type="login",
        resource_type="user",
        resource_id=user["id"],
        ip_address=ip,
    )

    response = make_response(
        jsonify(
            {
                "success": True,
                "data": {
                    "access_token": access_token,
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "role": user["role"],
                        "first_login": user["first_login"],
                    },
                },
                "message": "Login successful.",
            }
        ),
        200,
    )
    set_refresh_cookies(response, refresh_token)
    return response


# ---------------------------------------------------------------------------
# POST /api/auth/refresh
# ---------------------------------------------------------------------------

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Rotate access token using the httpOnly refresh cookie.

    Requirements: 2.2
    """
    claims = get_jwt()
    jti: str = claims.get("jti", "")

    if _is_token_blacklisted(jti):
        return _err("Refresh token has been revoked.", 401)

    identity = get_jwt_identity()
    additional_claims = {
        "role": claims.get("role"),
        "email": claims.get("email"),
        "first_login": claims.get("first_login", False),
    }
    new_access_token = create_access_token(
        identity=identity, additional_claims=additional_claims
    )

    return _ok(
        data={"access_token": new_access_token},
        message="Token refreshed.",
    )


# ---------------------------------------------------------------------------
# POST /api/auth/logout
# ---------------------------------------------------------------------------

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Invalidate refresh token (if present) and clear auth cookies.

    Does not require a valid refresh JWT — clears cookies even when only
    the access token was sent (fixes 422 on sign-out from the UI).

    Requirements: 2.5
    """
    response = make_response(
        jsonify({"success": True, "data": None, "message": "Logged out successfully."})
    )
    unset_jwt_cookies(response)

    try:
        verify_jwt_in_request(refresh=True, locations=["cookies"])
        claims = get_jwt()
        jti: str = claims.get("jti", "")
        identity = get_jwt_identity()
        role = claims.get("role", "unknown")
        if jti:
            _blacklist_refresh_token(jti)
        if identity:
            audit_log(
                actor_id=identity,
                actor_role=role,
                action_type="logout",
                resource_type="user",
                resource_id=identity,
                ip_address=_get_ip(),
            )
    except Exception:
        pass

    return response


# ---------------------------------------------------------------------------
# POST /api/auth/forgot-password
# ---------------------------------------------------------------------------

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Send a password-reset OTP to the user's email.

    Requirements: 21.1
    """
    data = request.get_json(silent=True) or {}
    email: str = (data.get("email") or "").strip().lower()

    if not email:
        return _err("email is required.", 422)

    user = get_user_by_email(email, "id, role")

    # Always return success to prevent email enumeration
    if not user:
        return _ok(
            message="If an account with that email exists, a reset code has been sent."
        )

    supabase = get_supabase()
    user_id: str = user["id"]

    # Invalidate existing password_reset OTPs
    now_iso = datetime.now(timezone.utc).isoformat()
    supabase.table("otp_tokens").update({"used_at": now_iso}).eq(
        "user_id", user_id
    ).eq("purpose", "password_reset").is_("used_at", "null").execute()

    try:
        otp_record = create_otp_record(user_id, "password_reset", supabase)
        send_otp_email(email, otp_record["token"], "password_reset")
    except Exception as exc:
        logger.error("Failed to send password reset OTP to %s: %s", email, exc)
        return _err("Failed to send reset code. Please try again.", 500)

    return _ok(
        message="If an account with that email exists, a reset code has been sent."
    )


# ---------------------------------------------------------------------------
# POST /api/auth/reset-password
# ---------------------------------------------------------------------------

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Validate OTP and update the user's password hash.

    Requirements: 21.2, 21.3, 21.4
    """
    data = request.get_json(silent=True) or {}
    email: str = (data.get("email") or "").strip().lower()
    token: str = (data.get("otp") or "").strip()
    new_password: str = data.get("password") or ""

    if not email or not token or not new_password:
        return _err("email, otp, and password are required.", 422)

    if len(new_password) < 8:
        return _err("Password must be at least 8 characters.", 422)

    user = get_user_by_email(email, "id, role")
    if not user:
        return _err("No account found with this email.", 404)

    supabase = get_supabase()
    user_id: str = user["id"]

    valid, error_msg = validate_otp(user_id, token, "password_reset", supabase)
    if not valid:
        return _err(error_msg, 422)

    # Update password hash
    new_hash = hash_password(new_password)
    supabase.table("users").update({"password_hash": new_hash}).eq(
        "id", user_id
    ).execute()

    # Invalidate all active refresh tokens for this user by blacklisting
    # (We can't enumerate all JTIs, so we rely on the short access token
    # lifetime + the user needing to log in again with the new password.)

    audit_log(
        actor_id=user_id,
        actor_role=user["role"],
        action_type="password_reset",
        resource_type="user",
        resource_id=user_id,
        ip_address=_get_ip(),
    )

    return _ok(message="Password reset successfully. Please log in with your new password.")
