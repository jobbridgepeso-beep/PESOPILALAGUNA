"""PESO Staff API routes — /api/staff"""

from datetime import datetime, timezone

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.blueprints.staff import staff_bp
from app.extensions import get_supabase
from app.services.audit_service import log as audit_log
from app.services.notification_service import send_inapp
from app.utils.decorators import role_required
from app.utils.responses import api_err, api_ok


@staff_bp.route("/dashboard", methods=["GET"])
@role_required("staff")
def dashboard():
    supabase = get_supabase()
    jobseekers = supabase.table("users").select("id").eq("role", "jobseeker").execute()
    active = supabase.table("job_vacancies").select("id").eq("status", "active").execute()
    pending = supabase.table("job_vacancies").select("id").eq("status", "pending").execute()
    fairs = supabase.table("job_fairs").select("id").eq("status", "upcoming").execute()
    programs = (
        supabase.table("program_applications").select("id").eq("status", "pending").execute()
    )
    return api_ok(
        {
            "total_jobseekers": len(jobseekers.data or []),
            "active_vacancies": len(active.data or []),
            "pending_approvals": len(pending.data or []),
            "upcoming_job_fairs": len(fairs.data or []),
            "pending_programs": len(programs.data or []),
        }
    )


@staff_bp.route("/vacancies/pending", methods=["GET"])
@role_required("staff")
def pending_vacancies():
    supabase = get_supabase()
    resp = (
        supabase.table("job_vacancies")
        .select("*, employer_profiles(company_name, industry, phone)")
        .eq("status", "pending")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@staff_bp.route("/vacancies/<vacancy_id>/approve", methods=["PATCH"])
@role_required("staff")
def approve_vacancy(vacancy_id: str):
    staff_id = get_jwt_identity()
    supabase = get_supabase()
    now = datetime.now(timezone.utc).isoformat()

    vac = (
        supabase.table("job_vacancies")
        .select("*, employer_profiles(user_id, company_name)")
        .eq("id", vacancy_id)
        .single()
        .execute()
    )
    if not vac.data:
        return api_err("Vacancy not found.", 404)
    if vac.data.get("status") != "pending":
        return api_err("Vacancy is not pending approval.", 409)

    supabase.table("job_vacancies").update(
        {"status": "active", "approved_by": staff_id, "approved_at": now}
    ).eq("id", vacancy_id).execute()

    employer = vac.data.get("employer_profiles") or {}
    if employer.get("user_id"):
        send_inapp(
            employer["user_id"],
            "notification",
            {
                "title": "Vacancy approved",
                "body": f'"{vac.data.get("title")}" is now live on JobBridge.',
            },
        )

    audit_log(
        actor_id=staff_id,
        actor_role="staff",
        action_type="vacancy_approved",
        resource_type="job_vacancy",
        resource_id=vacancy_id,
        ip_address=request.remote_addr,
    )
    return api_ok({"status": "active"}, "Vacancy approved and published.")


@staff_bp.route("/vacancies/<vacancy_id>/reject", methods=["PATCH"])
@role_required("staff")
def reject_vacancy(vacancy_id: str):
    staff_id = get_jwt_identity()
    supabase = get_supabase()
    body = request.get_json(silent=True) or {}
    reason = (body.get("reason") or "").strip()
    if not reason:
        return api_err("Rejection reason is required.", 422)

    vac = (
        supabase.table("job_vacancies")
        .select("*, employer_profiles(user_id)")
        .eq("id", vacancy_id)
        .single()
        .execute()
    )
    if not vac.data:
        return api_err("Vacancy not found.", 404)

    supabase.table("job_vacancies").update(
        {"status": "rejected", "rejection_reason": reason}
    ).eq("id", vacancy_id).execute()

    employer = vac.data.get("employer_profiles") or {}
    if employer.get("user_id"):
        send_inapp(
            employer["user_id"],
            "notification",
            {
                "title": "Vacancy not approved",
                "body": f'"{vac.data.get("title")}" was rejected: {reason}',
            },
        )

    audit_log(
        actor_id=staff_id,
        actor_role="staff",
        action_type="vacancy_rejected",
        resource_type="job_vacancy",
        resource_id=vacancy_id,
        ip_address=request.remote_addr,
        metadata={"reason": reason},
    )
    return api_ok({"status": "rejected"}, "Vacancy rejected.")
