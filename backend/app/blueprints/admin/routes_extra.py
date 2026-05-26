"""Additional admin routes."""

import secrets
import string

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.blueprints.admin import admin_bp
from app.extensions import get_supabase
from app.services.audit_service import log as audit_log
from app.utils.decorators import role_required
from app.utils.helpers import hash_password
from app.services.notification_service import send_inapp
from app.utils.responses import api_err, api_ok

PROGRAM_TYPES = ("spes", "dilp", "owwa", "mst")


def _temp_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$"
    return "".join(secrets.choice(alphabet) for _ in range(length))


@admin_bp.route("/users", methods=["GET"])
@role_required("admin")
def users_overview():
    supabase = get_supabase()
    resp = (
        supabase.table("users")
        .select("id, email, role, is_active, is_verified, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/staff", methods=["GET", "POST"])
@role_required("admin")
def staff_accounts():
    supabase = get_supabase()

    if request.method == "GET":
        resp = (
            supabase.table("users")
            .select("id, email, is_active, is_verified, first_login, created_at")
            .eq("role", "staff")
            .order("created_at", desc=True)
            .execute()
        )
        return api_ok(resp.data or [])

    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    if not email:
        return api_err("email is required.", 422)

    existing = supabase.table("users").select("id").eq("email", email).execute()
    if existing.data:
        return api_err("Email already registered.", 409)

    temp_pw = _temp_password()
    user_resp = (
        supabase.table("users")
        .insert(
            {
                "email": email,
                "password_hash": hash_password(temp_pw),
                "role": "staff",
                "is_active": True,
                "is_verified": True,
                "first_login": True,
            }
        )
        .execute()
    )
    audit_log(
        actor_id=get_jwt_identity(),
        actor_role="admin",
        action_type="staff_created",
        resource_type="user",
        resource_id=user_resp.data[0]["id"] if user_resp.data else None,
        ip_address=request.remote_addr,
    )
    return api_ok(
        {"user": user_resp.data[0], "temporary_password": temp_pw},
        "Staff account created. Share the temporary password securely.",
        201,
    )


@admin_bp.route("/staff/<staff_id>/activate", methods=["PATCH"])
@role_required("admin")
def toggle_staff(staff_id: str):
    body = request.get_json(silent=True) or {}
    is_active = body.get("is_active", True)
    supabase = get_supabase()
    supabase.table("users").update({"is_active": is_active}).eq("id", staff_id).eq(
        "role", "staff"
    ).execute()
    return api_ok({"is_active": is_active}, "Staff account updated.")


@admin_bp.route("/jobseekers", methods=["GET"])
@role_required("admin")
def list_jobseekers():
    supabase = get_supabase()
    resp = (
        supabase.table("jobseeker_profiles")
        .select("*, users(email, is_active)")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/employers", methods=["GET"])
@role_required("admin")
def list_employers():
    supabase = get_supabase()
    resp = (
        supabase.table("employer_profiles")
        .select("*, users(email, is_active)")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/vacancies", methods=["GET"])
@role_required("admin")
def list_vacancies():
    supabase = get_supabase()
    resp = (
        supabase.table("job_vacancies")
        .select("*, employer_profiles(company_name)")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/interviews", methods=["GET"])
@role_required("admin")
def interviews():
    supabase = get_supabase()
    resp = (
        supabase.table("interviews")
        .select("*, job_applications(job_vacancies(title))")
        .order("scheduled_at", desc=True)
        .limit(100)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/employment", methods=["GET"])
@role_required("admin")
def employment():
    supabase = get_supabase()
    resp = (
        supabase.table("employment_records")
        .select("*, jobseeker_profiles(first_name, last_name), employer_profiles(company_name)")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/job-fairs", methods=["GET"])
@role_required("admin")
def job_fairs():
    supabase = get_supabase()
    resp = supabase.table("job_fairs").select("*").order("event_date", desc=True).execute()
    return api_ok(resp.data or [])


@admin_bp.route("/programs/<program_type>", methods=["GET"])
@role_required("admin")
def programs(program_type: str):
    if program_type not in PROGRAM_TYPES:
        return api_err("Invalid program type.", 422)
    supabase = get_supabase()
    resp = (
        supabase.table("program_applications")
        .select("*, jobseeker_profiles(first_name, last_name)")
        .eq("program_type", program_type)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/lmi-reports", methods=["GET"])
@role_required("admin")
def lmi_reports():
    supabase = get_supabase()
    resp = supabase.table("lmi_reports").select("*").order("generated_at", desc=True).execute()
    return api_ok(resp.data or [])


@admin_bp.route("/announcements", methods=["POST"])
@role_required("admin")
def announcements():
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    message = (body.get("body") or "").strip()
    audience = body.get("audience", "jobseeker")
    if not title or not message:
        return api_err("title and body are required.", 422)

    supabase = get_supabase()
    role_filter = audience if audience in ("jobseeker", "employer") else "jobseeker"
    users = (
        supabase.table("users")
        .select("id")
        .eq("role", role_filter)
        .eq("is_active", True)
        .execute()
    )
    count = 0
    for u in users.data or []:
        send_inapp(
            u["id"],
            "announcement",
            {"title": title, "body": message},
        )
        count += 1
    return api_ok({"sent": count}, f"Announcement sent to {count} users.")


@admin_bp.route("/audit-trail", methods=["GET"])
@role_required("admin")
def audit_trail():
    supabase = get_supabase()
    resp = (
        supabase.table("audit_trail")
        .select("*")
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )
    return api_ok(resp.data or [])


@admin_bp.route("/notifications", methods=["GET"])
@role_required("admin")
def notifications():
    user_id = get_jwt_identity()
    supabase = get_supabase()
    resp = (
        supabase.table("notifications")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    unread = sum(1 for n in (resp.data or []) if not n.get("is_read"))
    return api_ok({"items": resp.data or [], "unread_count": unread})


@admin_bp.route("/settings", methods=["GET", "PUT"])
@role_required("admin")
def settings():
    supabase = get_supabase()
    if request.method == "GET":
        resp = supabase.table("system_settings").select("*").execute()
        return api_ok(resp.data or [])

    body = request.get_json(silent=True) or {}
    settings_list = body.get("settings") or []
    admin_id = get_jwt_identity()
    for item in settings_list:
        key = item.get("key")
        value = item.get("value")
        if key and value is not None:
            supabase.table("system_settings").update(
                {"value": str(value), "updated_by": admin_id}
            ).eq("key", key).execute()
    audit_log(
        actor_id=admin_id,
        actor_role="admin",
        action_type="settings_updated",
        resource_type="system_settings",
        ip_address=request.remote_addr,
    )
    return api_ok(None, "Settings updated.")
