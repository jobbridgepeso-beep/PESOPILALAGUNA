"""Admin API routes — /api/admin"""

from flask import jsonify

from app.blueprints.admin import admin_bp
from app.extensions import get_supabase
from app.utils.decorators import role_required


def _ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "data": data, "message": message}), status


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("admin")
def dashboard():
    supabase = get_supabase()

    staff = supabase.table("users").select("id, is_active").eq("role", "staff").execute()
    jobseekers = (
        supabase.table("users").select("id").eq("role", "jobseeker").execute()
    )
    audit = (
        supabase.table("audit_trail")
        .select("id, action_type, actor_role, created_at")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    staff_rows = staff.data or []
    return _ok(
        {
            "staff_total": len(staff_rows),
            "staff_active": sum(1 for s in staff_rows if s.get("is_active")),
            "total_jobseekers": len(jobseekers.data or []),
            "recent_audit": audit.data or [],
        }
    )
