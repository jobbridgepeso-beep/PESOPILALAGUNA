"""PESO Staff API routes — /api/staff"""

from flask import jsonify

from app.blueprints.staff import staff_bp
from app.extensions import get_supabase
from app.utils.decorators import role_required


def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data, "message": message}), status


@staff_bp.route("/dashboard", methods=["GET"])
@role_required("staff")
def dashboard():
    supabase = get_supabase()

    jobseekers = (
        supabase.table("users").select("id").eq("role", "jobseeker").execute()
    )
    active_vacancies = (
        supabase.table("job_vacancies").select("id").eq("status", "active").execute()
    )
    pending = (
        supabase.table("job_vacancies").select("id").eq("status", "pending").execute()
    )
    fairs = (
        supabase.table("job_fairs")
        .select("id")
        .eq("status", "upcoming")
        .execute()
    )
    programs = (
        supabase.table("program_applications")
        .select("id")
        .eq("status", "pending")
        .execute()
    )

    return _ok(
        {
            "total_jobseekers": len(jobseekers.data or []),
            "active_vacancies": len(active_vacancies.data or []),
            "pending_approvals": len(pending.data or []),
            "upcoming_job_fairs": len(fairs.data or []),
            "pending_programs": len(programs.data or []),
        }
    )
