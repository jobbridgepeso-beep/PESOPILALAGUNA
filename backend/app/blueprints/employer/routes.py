"""Employer API routes — /api/employer"""

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.blueprints.employer import employer_bp
from app.extensions import get_supabase
from app.utils.decorators import role_required


def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data, "message": message}), status


@employer_bp.route("/dashboard", methods=["GET"])
@role_required("employer")
def dashboard():
    user_id = get_jwt_identity()
    supabase = get_supabase()

    profile = (
        supabase.table("employer_profiles")
        .select("id")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    employer_id = profile.data["id"] if profile.data else None

    active_vacancies = 0
    total_applicants = 0
    hired = 0
    pending_reviews = 0

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

    return _ok(
        {
            "active_vacancies": active_vacancies,
            "total_applicants": total_applicants,
            "hired": hired,
            "pending_reviews": pending_reviews,
        }
    )
