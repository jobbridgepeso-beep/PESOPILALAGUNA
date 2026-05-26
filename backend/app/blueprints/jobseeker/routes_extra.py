"""Additional jobseeker routes."""

from datetime import datetime, timezone

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.blueprints.jobseeker import jobseeker_bp
from app.extensions import get_supabase
from app.services.qr_service import generate_qr_with_token
from app.utils.db_helpers import get_jobseeker_profile
from app.utils.decorators import role_required
from app.utils.responses import api_err, api_ok
from app.utils.storage import upload_file


PROGRAM_TYPES = ("spes", "dilp", "owwa", "mst")


@jobseeker_bp.route("/employment", methods=["GET"])
@role_required("jobseeker")
def employment_history():
    profile = get_jobseeker_profile(get_jwt_identity())
    if not profile:
        return api_ok([])
    supabase = get_supabase()
    resp = (
        supabase.table("employment_records")
        .select("*, employer_profiles(company_name)")
        .eq("jobseeker_id", profile["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@jobseeker_bp.route("/interviews", methods=["GET"])
@role_required("jobseeker")
def interviews():
    profile = get_jobseeker_profile(get_jwt_identity())
    if not profile:
        return api_ok([])
    supabase = get_supabase()
    apps = (
        supabase.table("job_applications")
        .select("id")
        .eq("jobseeker_id", profile["id"])
        .execute()
    )
    app_ids = [a["id"] for a in (apps.data or [])]
    if not app_ids:
        return api_ok([])
    resp = (
        supabase.table("interviews")
        .select("*, job_applications(vacancy_id, job_vacancies(title))")
        .in_("application_id", app_ids)
        .order("scheduled_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@jobseeker_bp.route("/job-fairs", methods=["GET"])
@role_required("jobseeker")
def job_fairs():
    supabase = get_supabase()
    fairs = (
        supabase.table("job_fairs")
        .select("*")
        .in_("status", ["upcoming", "ongoing"])
        .order("event_date", desc=False)
        .execute()
    )
    profile = get_jobseeker_profile(get_jwt_identity())
    registrations = []
    if profile:
        reg = (
            supabase.table("job_fair_registrations")
            .select("job_fair_id, qr_url")
            .eq("jobseeker_id", profile["id"])
            .execute()
        )
        registrations = reg.data or []
    reg_map = {r["job_fair_id"]: r for r in registrations}
    result = []
    for fair in fairs.data or []:
        result.append({**fair, "registered": fair["id"] in reg_map, "registration": reg_map.get(fair["id"])})
    return api_ok(result)


@jobseeker_bp.route("/job-fairs/<fair_id>/register", methods=["POST"])
@role_required("jobseeker")
def register_job_fair(fair_id: str):
    user_id = get_jwt_identity()
    profile = get_jobseeker_profile(user_id)
    if not profile:
        return api_err("Profile not found.", 404)
    supabase = get_supabase()
    existing = (
        supabase.table("job_fair_registrations")
        .select("id")
        .eq("job_fair_id", fair_id)
        .eq("jobseeker_id", profile["id"])
        .execute()
    )
    if existing.data:
        return api_err("Already registered for this job fair.", 409)
    token, png_bytes = generate_qr_with_token(profile["id"], fair_id)
    qr_url = None
    try:
        qr_url = upload_file(
            "qr-codes",
            f"{fair_id}/{profile['id']}.png",
            png_bytes,
            "image/png",
        )
    except Exception:
        qr_url = None
    payload = {
        "job_fair_id": fair_id,
        "jobseeker_id": profile["id"],
        "qr_token": token,
        "qr_url": qr_url,
    }
    resp = supabase.table("job_fair_registrations").insert(payload).execute()
    return api_ok(resp.data[0], "Registered for job fair.", 201)


@jobseeker_bp.route("/programs", methods=["GET"])
@role_required("jobseeker")
def list_programs():
    profile = get_jobseeker_profile(get_jwt_identity())
    if not profile:
        return api_ok([])
    supabase = get_supabase()
    resp = (
        supabase.table("program_applications")
        .select("*")
        .eq("jobseeker_id", profile["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@jobseeker_bp.route("/programs/<program_type>/apply", methods=["POST"])
@role_required("jobseeker")
def apply_program(program_type: str):
    if program_type not in PROGRAM_TYPES:
        return api_err("Invalid program type.", 422)
    profile = get_jobseeker_profile(get_jwt_identity())
    if not profile:
        return api_err("Profile not found.", 404)
    supabase = get_supabase()
    dup = (
        supabase.table("program_applications")
        .select("id")
        .eq("jobseeker_id", profile["id"])
        .eq("program_type", program_type)
        .in_("status", ["pending", "approved"])
        .execute()
    )
    if dup.data:
        return api_err("You already have an active application for this program.", 409)
    resp = (
        supabase.table("program_applications")
        .insert(
            {
                "jobseeker_id": profile["id"],
                "program_type": program_type,
                "status": "pending",
            }
        )
        .execute()
    )
    return api_ok(resp.data[0], "Program application submitted.", 201)


@jobseeker_bp.route("/notifications", methods=["GET"])
@role_required("jobseeker")
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


@jobseeker_bp.route("/notifications/<notification_id>/read", methods=["PATCH"])
@role_required("jobseeker")
def mark_notification_read(notification_id: str):
    user_id = get_jwt_identity()
    supabase = get_supabase()
    supabase.table("notifications").update({"is_read": True}).eq("id", notification_id).eq(
        "user_id", user_id
    ).execute()
    return api_ok(None, "Notification marked as read.")


@jobseeker_bp.route("/settings", methods=["GET"])
@role_required("jobseeker")
def settings():
    supabase = get_supabase()
    resp = supabase.table("system_settings").select("key, value, description").execute()
    return api_ok(resp.data or [])
