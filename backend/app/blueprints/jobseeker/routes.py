"""Jobseeker API routes — /api/jobseeker"""

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.blueprints.jobseeker import jobseeker_bp
from app.extensions import get_supabase
from app.utils.decorators import role_required


def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data, "message": message}), status


@jobseeker_bp.route("/dashboard", methods=["GET"])
@role_required("jobseeker")
def dashboard():
    user_id = get_jwt_identity()
    supabase = get_supabase()

    profile = (
        supabase.table("jobseeker_profiles")
        .select("id")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    jobseeker_id = profile.data["id"] if profile.data else None

    applications = {"total": 0, "pending": 0}
    interviews = 0

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

        interviews = 0

    vacancies = (
        supabase.table("job_vacancies").select("id").eq("status", "active").execute()
    )

    return _ok(
        {
            "applications": applications,
            "interviews": interviews,
            "active_jobs": len(vacancies.data or []),
        }
    )


@jobseeker_bp.route("/profile", methods=["GET"])
@role_required("jobseeker")
def get_profile():
    user_id = get_jwt_identity()
    supabase = get_supabase()
    resp = (
        supabase.table("jobseeker_profiles")
        .select("*")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return _ok(resp.data)
