"""Additional employer routes."""

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.blueprints.employer import employer_bp
from app.extensions import get_supabase
from app.utils.db_helpers import get_employer_profile, get_user
from app.utils.decorators import role_required
from app.utils.responses import api_err, api_ok


@employer_bp.route("/account", methods=["GET"])
@role_required("employer")
def account():
    return api_ok(get_user(get_jwt_identity()))


@employer_bp.route("/applications", methods=["GET"])
@role_required("employer")
def all_applications():
    profile = get_employer_profile(get_jwt_identity())
    if not profile:
        return api_ok([])
    supabase = get_supabase()
    vacs = (
        supabase.table("job_vacancies")
        .select("id")
        .eq("employer_id", profile["id"])
        .execute()
    )
    vac_ids = [v["id"] for v in (vacs.data or [])]
    if not vac_ids:
        return api_ok([])
    resp = (
        supabase.table("job_applications")
        .select("*, job_vacancies(title), jobseeker_profiles(first_name, last_name, phone)")
        .in_("vacancy_id", vac_ids)
        .order("applied_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@employer_bp.route("/interviews", methods=["GET", "POST"])
@role_required("employer")
def interviews():
    profile = get_employer_profile(get_jwt_identity())
    if not profile:
        return api_err("Profile not found.", 404)
    supabase = get_supabase()

    if request.method == "GET":
        vacs = (
            supabase.table("job_vacancies")
            .select("id")
            .eq("employer_id", profile["id"])
            .execute()
        )
        vac_ids = [v["id"] for v in (vacs.data or [])]
        if not vac_ids:
            return api_ok([])
        apps = (
            supabase.table("job_applications")
            .select("id")
            .in_("vacancy_id", vac_ids)
            .execute()
        )
        app_ids = [a["id"] for a in (apps.data or [])]
        if not app_ids:
            return api_ok([])
        resp = (
            supabase.table("interviews")
            .select("*, job_applications(jobseeker_profiles(first_name, last_name))")
            .in_("application_id", app_ids)
            .order("scheduled_at", desc=True)
            .execute()
        )
        return api_ok(resp.data or [])

    body = request.get_json(silent=True) or {}
    app_id = body.get("application_id")
    scheduled_at = body.get("scheduled_at")
    if not app_id or not scheduled_at:
        return api_err("application_id and scheduled_at are required.", 422)

    resp = (
        supabase.table("interviews")
        .insert(
            {
                "application_id": app_id,
                "scheduled_at": scheduled_at,
                "location": body.get("location"),
                "meeting_link": body.get("meeting_link"),
                "notes": body.get("notes"),
                "status": "scheduled",
            }
        )
        .execute()
    )
    return api_ok(resp.data[0], "Interview scheduled.", 201)


@employer_bp.route("/job-fairs", methods=["GET"])
@role_required("employer")
def job_fairs():
    supabase = get_supabase()
    resp = (
        supabase.table("job_fairs")
        .select("*")
        .in_("status", ["upcoming", "ongoing"])
        .order("event_date", desc=False)
        .execute()
    )
    return api_ok(resp.data or [])


@employer_bp.route("/employment", methods=["GET"])
@role_required("employer")
def employment():
    profile = get_employer_profile(get_jwt_identity())
    if not profile:
        return api_ok([])
    supabase = get_supabase()
    resp = (
        supabase.table("employment_records")
        .select("*, jobseeker_profiles(first_name, last_name), job_vacancies(title)")
        .eq("employer_id", profile["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@employer_bp.route("/notifications", methods=["GET"])
@role_required("employer")
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


@employer_bp.route("/notifications/<notification_id>/read", methods=["PATCH"])
@role_required("employer")
def mark_notification_read(notification_id: str):
    user_id = get_jwt_identity()
    supabase = get_supabase()
    supabase.table("notifications").update({"is_read": True}).eq("id", notification_id).eq(
        "user_id", user_id
    ).execute()
    return api_ok(None, "Notification marked as read.")


@employer_bp.route("/settings", methods=["GET"])
@role_required("employer")
def settings():
    supabase = get_supabase()
    resp = supabase.table("system_settings").select("key, value, description").execute()
    return api_ok(resp.data or [])
