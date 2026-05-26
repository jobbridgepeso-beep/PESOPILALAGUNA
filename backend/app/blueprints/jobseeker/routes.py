"""Jobseeker API routes — /api/jobseeker"""

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.blueprints.jobseeker import jobseeker_bp
from app.extensions import get_supabase
from app.services.ai_matcher import compute_match_score, rank_vacancies
from app.services.audit_service import log as audit_log
from app.services.notification_service import send_inapp
from app.utils.decorators import role_required
from app.utils.responses import api_err, api_ok


def _get_jobseeker(supabase, user_id: str):
    resp = (
        supabase.table("jobseeker_profiles")
        .select("*")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return resp.data


@jobseeker_bp.route("/dashboard", methods=["GET"])
@role_required("jobseeker")
def dashboard():
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_jobseeker(supabase, user_id)
    jobseeker_id = profile["id"] if profile else None

    applications = {"total": 0, "pending": 0}
    if jobseeker_id:
        apps = (
            supabase.table("job_applications")
            .select("status")
            .eq("jobseeker_id", jobseeker_id)
            .execute()
        )
        rows = apps.data or []
        applications["total"] = len(rows)
        applications["pending"] = sum(1 for a in rows if a.get("status") == "pending")

    vacancies = (
        supabase.table("job_vacancies").select("id").eq("status", "active").execute()
    )

    return api_ok(
        {
            "applications": applications,
            "interviews": 0,
            "active_jobs": len(vacancies.data or []),
        }
    )


@jobseeker_bp.route("/profile", methods=["GET", "PUT"])
@role_required("jobseeker")
def profile():
    user_id = get_jwt_identity()
    supabase = get_supabase()

    if request.method == "GET":
        data = _get_jobseeker(supabase, user_id)
        if not data:
            return api_err("Profile not found.", 404)
        return api_ok(data)

    body = request.get_json(silent=True) or {}
    allowed = {
        "first_name",
        "last_name",
        "middle_name",
        "birthdate",
        "gender",
        "civil_status",
        "address",
        "phone",
        "education",
        "experience",
        "skills",
    }
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        return api_err("No valid fields to update.", 422)

    resp = (
        supabase.table("jobseeker_profiles")
        .update(updates)
        .eq("user_id", user_id)
        .execute()
    )
    audit_log(
        actor_id=user_id,
        actor_role="jobseeker",
        action_type="profile_updated",
        resource_type="jobseeker_profile",
        resource_id=resp.data[0]["id"] if resp.data else None,
        ip_address=request.remote_addr,
    )
    return api_ok(resp.data[0] if resp.data else updates, "Profile updated.")


@jobseeker_bp.route("/jobs", methods=["GET"])
@role_required("jobseeker")
def list_jobs():
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_jobseeker(supabase, user_id)
    if not profile:
        return api_err("Complete your profile first.", 404)

    resp = (
        supabase.table("job_vacancies")
        .select("*, employer_profiles(company_name, industry)")
        .eq("status", "active")
        .execute()
    )
    vacancies = resp.data or []
    ranked = rank_vacancies(profile, vacancies)
    return api_ok(ranked)


@jobseeker_bp.route("/jobs/<vacancy_id>/apply", methods=["POST"])
@role_required("jobseeker")
def apply_to_job(vacancy_id: str):
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_jobseeker(supabase, user_id)
    if not profile:
        return api_err("Profile not found.", 404)

    jobseeker_id = profile["id"]
    vac = (
        supabase.table("job_vacancies")
        .select("*")
        .eq("id", vacancy_id)
        .eq("status", "active")
        .single()
        .execute()
    )
    if not vac.data:
        return api_err("Vacancy not found or not active.", 404)

    existing = (
        supabase.table("job_applications")
        .select("id")
        .eq("vacancy_id", vacancy_id)
        .eq("jobseeker_id", jobseeker_id)
        .execute()
    )
    if existing.data:
        return api_err("You have already applied for this vacancy.", 409)

    body = request.get_json(silent=True) or {}
    score = compute_match_score(profile, vac.data)
    payload = {
        "vacancy_id": vacancy_id,
        "jobseeker_id": jobseeker_id,
        "status": "pending",
        "match_score": round(score, 4),
        "cover_letter": body.get("cover_letter"),
    }
    app_resp = supabase.table("job_applications").insert(payload).execute()
    if not app_resp.data:
        return api_err("Failed to submit application.", 500)

    application = app_resp.data[0]
    employer = (
        supabase.table("employer_profiles")
        .select("user_id")
        .eq("id", vac.data["employer_id"])
        .single()
        .execute()
    )
    if employer.data:
        send_inapp(
            employer.data["user_id"],
            "notification",
            {
                "title": "New job application",
                "body": f"A jobseeker applied for {vac.data.get('title', 'your vacancy')}.",
                "application_id": application["id"],
            },
        )

    audit_log(
        actor_id=user_id,
        actor_role="jobseeker",
        action_type="application_submitted",
        resource_type="job_application",
        resource_id=application["id"],
        ip_address=request.remote_addr,
    )
    return api_ok(application, "Application submitted.", 201)


@jobseeker_bp.route("/applications", methods=["GET"])
@role_required("jobseeker")
def list_applications():
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_jobseeker(supabase, user_id)
    if not profile:
        return api_ok([])

    resp = (
        supabase.table("job_applications")
        .select("*, job_vacancies(title, employment_type, employer_profiles(company_name))")
        .eq("jobseeker_id", profile["id"])
        .order("applied_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])
