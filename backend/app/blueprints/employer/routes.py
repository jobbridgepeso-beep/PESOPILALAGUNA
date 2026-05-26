"""Employer API routes — /api/employer"""

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.blueprints.employer import employer_bp
from app.extensions import get_supabase
from app.services.ai_matcher import rank_applicants
from app.services.audit_service import log as audit_log
from app.services.notification_service import send_inapp
from app.utils.db_helpers import safe_single
from app.utils.decorators import role_required
from app.utils.responses import api_err, api_ok


def _get_employer(supabase, user_id: str):
    return safe_single(
        supabase.table("employer_profiles").select("*").eq("user_id", user_id)
    )


@employer_bp.route("/dashboard", methods=["GET"])
@role_required("employer")
def dashboard():
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_employer(supabase, user_id)
    employer_id = profile["id"] if profile else None

    active_vacancies = total_applicants = hired = pending_reviews = 0
    if employer_id:
        vacancies = (
            supabase.table("job_vacancies")
            .select("id, status")
            .eq("employer_id", employer_id)
            .execute()
        )
        vac_rows = vacancies.data or []
        active_vacancies = sum(1 for v in vac_rows if v.get("status") == "active")
        vac_ids = [v["id"] for v in vac_rows]
        if vac_ids:
            apps = (
                supabase.table("job_applications")
                .select("status")
                .in_("vacancy_id", vac_ids)
                .execute()
            )
            app_rows = apps.data or []
            total_applicants = len(app_rows)
            hired = sum(1 for a in app_rows if a.get("status") == "hired")
            pending_reviews = sum(
                1 for a in app_rows if a.get("status") in ("pending", "reviewed")
            )

    return api_ok(
        {
            "active_vacancies": active_vacancies,
            "total_applicants": total_applicants,
            "hired": hired,
            "pending_reviews": pending_reviews,
        }
    )


@employer_bp.route("/profile", methods=["GET", "PUT"])
@role_required("employer")
def profile():
    user_id = get_jwt_identity()
    supabase = get_supabase()

    if request.method == "GET":
        data = _get_employer(supabase, user_id)
        if not data:
            return api_err("Profile not found.", 404)
        return api_ok(data)

    body = request.get_json(silent=True) or {}
    allowed = {
        "company_name",
        "industry",
        "address",
        "phone",
        "website",
        "description",
    }
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        return api_err("No valid fields to update.", 422)

    resp = (
        supabase.table("employer_profiles")
        .update(updates)
        .eq("user_id", user_id)
        .execute()
    )
    return api_ok(resp.data[0] if resp.data else updates, "Company profile updated.")


@employer_bp.route("/vacancies", methods=["GET", "POST"])
@role_required("employer")
def vacancies():
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_employer(supabase, user_id)
    if not profile:
        return api_err("Employer profile not found.", 404)

    employer_id = profile["id"]

    if request.method == "GET":
        resp = (
            supabase.table("job_vacancies")
            .select("*")
            .eq("employer_id", employer_id)
            .order("created_at", desc=True)
            .execute()
        )
        return api_ok(resp.data or [])

    body = request.get_json(silent=True) or {}
    required = ["title", "description", "requirements"]
    missing = [f for f in required if not body.get(f)]
    if missing:
        return api_err(f"Missing fields: {', '.join(missing)}", 422)

    payload = {
        "employer_id": employer_id,
        "title": body["title"],
        "description": body["description"],
        "requirements": body["requirements"],
        "skills_required": body.get("skills_required") or [],
        "employment_type": body.get("employment_type", "full-time"),
        "salary_min": body.get("salary_min"),
        "salary_max": body.get("salary_max"),
        "slots": body.get("slots", 1),
        "status": "pending",
    }
    resp = supabase.table("job_vacancies").insert(payload).execute()
    audit_log(
        actor_id=user_id,
        actor_role="employer",
        action_type="vacancy_created",
        resource_type="job_vacancy",
        resource_id=resp.data[0]["id"] if resp.data else None,
        ip_address=request.remote_addr,
    )
    return api_ok(resp.data[0], "Vacancy submitted for PESO approval.", 201)


@employer_bp.route("/vacancies/<vacancy_id>", methods=["PUT", "DELETE"])
@role_required("employer")
def manage_vacancy(vacancy_id: str):
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_employer(supabase, user_id)
    if not profile:
        return api_err("Employer profile not found.", 404)

    vac_row = safe_single(
        supabase.table("job_vacancies")
        .select("id, employer_id, status")
        .eq("id", vacancy_id)
    )
    if not vac_row or vac_row["employer_id"] != profile["id"]:
        return api_err("Vacancy not found.", 404)

    if request.method == "DELETE":
        supabase.table("job_vacancies").update({"status": "closed"}).eq(
            "id", vacancy_id
        ).execute()
        return api_ok(None, "Vacancy closed.")

    body = request.get_json(silent=True) or {}
    allowed = {
        "title",
        "description",
        "requirements",
        "skills_required",
        "employment_type",
        "salary_min",
        "salary_max",
        "slots",
    }
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        return api_err("No valid fields to update.", 422)

    if vac_row["status"] == "active":
        updates["status"] = "pending"

    resp = (
        supabase.table("job_vacancies")
        .update(updates)
        .eq("id", vacancy_id)
        .execute()
    )
    return api_ok(resp.data[0] if resp.data else updates, "Vacancy updated.")


@employer_bp.route("/vacancies/<vacancy_id>/applicants", methods=["GET"])
@role_required("employer")
def list_applicants(vacancy_id: str):
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_employer(supabase, user_id)
    if not profile:
        return api_err("Employer profile not found.", 404)

    vacancy = safe_single(
        supabase.table("job_vacancies")
        .select("*")
        .eq("id", vacancy_id)
        .eq("employer_id", profile["id"])
    )
    if not vacancy:
        return api_err("Vacancy not found.", 404)

    apps = (
        supabase.table("job_applications")
        .select("*, jobseeker_profiles(first_name, last_name, skills, experience, phone)")
        .eq("vacancy_id", vacancy_id)
        .execute()
    )
    applicants = []
    for row in apps.data or []:
        profile_data = row.pop("jobseeker_profiles", None) or {}
        applicants.append({**row, "profile": profile_data})

    ranked = rank_applicants(vacancy, applicants)
    return api_ok(ranked)


@employer_bp.route("/applications/<application_id>/status", methods=["PATCH"])
@role_required("employer")
def update_application_status(application_id: str):
    user_id = get_jwt_identity()
    supabase = get_supabase()
    profile = _get_employer(supabase, user_id)
    if not profile:
        return api_err("Employer profile not found.", 404)

    body = request.get_json(silent=True) or {}
    new_status = (body.get("status") or "").strip().lower()
    allowed = {"reviewed", "shortlisted", "rejected", "hired"}
    if new_status not in allowed:
        return api_err(f"status must be one of: {', '.join(sorted(allowed))}", 422)

    application = safe_single(
        supabase.table("job_applications")
        .select("*, job_vacancies(employer_id, title, employment_type)")
        .eq("id", application_id)
    )
    if not application:
        return api_err("Application not found.", 404)

    vacancy = application.get("job_vacancies") or {}
    if vacancy.get("employer_id") != profile["id"]:
        return api_err("Access denied.", 403)

    supabase.table("job_applications").update({"status": new_status}).eq(
        "id", application_id
    ).execute()

    if new_status == "hired":
        supabase.table("employment_records").insert(
            {
                "jobseeker_id": application["jobseeker_id"],
                "employer_id": profile["id"],
                "vacancy_id": application["vacancy_id"],
                "application_id": application_id,
                "employment_type": vacancy.get("employment_type", "full-time"),
                "status": "active",
            }
        ).execute()

    seeker = safe_single(
        supabase.table("jobseeker_profiles")
        .select("user_id")
        .eq("id", application["jobseeker_id"])
    )
    if seeker:
        send_inapp(
            seeker["user_id"],
            "application_update",
            {
                "title": "Application status updated",
                "body": f"Your application for {vacancy.get('title')} is now: {new_status}.",
                "status": new_status,
            },
        )

    audit_log(
        actor_id=user_id,
        actor_role="employer",
        action_type="application_status_changed",
        resource_type="job_application",
        resource_id=application_id,
        ip_address=request.remote_addr,
        metadata={"status": new_status},
    )
    return api_ok({"status": new_status}, "Application status updated.")
