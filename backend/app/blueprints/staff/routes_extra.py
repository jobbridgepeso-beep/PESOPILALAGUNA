"""Additional PESO staff routes."""

from datetime import datetime, timezone

from flask import request
from flask_jwt_extended import get_jwt_identity

from app.blueprints.staff import staff_bp
from app.extensions import get_supabase
from app.services.notification_service import send_inapp
from app.services.qr_service import validate_scan
from app.utils.decorators import role_required
from app.utils.responses import api_err, api_ok

PROGRAM_TYPES = ("spes", "dilp", "owwa", "mst")


@staff_bp.route("/jobseekers", methods=["GET"])
@role_required("staff")
def list_jobseekers():
    supabase = get_supabase()
    resp = (
        supabase.table("jobseeker_profiles")
        .select("*, users(email, is_active)")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@staff_bp.route("/employers", methods=["GET"])
@role_required("staff")
def list_employers():
    supabase = get_supabase()
    resp = (
        supabase.table("employer_profiles")
        .select("*, users(email, is_active)")
        .order("created_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@staff_bp.route("/vacancies", methods=["GET"])
@role_required("staff")
def list_vacancies():
    supabase = get_supabase()
    status = request.args.get("status")
    q = supabase.table("job_vacancies").select(
        "*, employer_profiles(company_name)"
    )
    if status:
        q = q.eq("status", status)
    resp = q.order("created_at", desc=True).execute()
    return api_ok(resp.data or [])


@staff_bp.route("/interviews", methods=["GET"])
@role_required("staff")
def interviews():
    supabase = get_supabase()
    resp = (
        supabase.table("interviews")
        .select("*, job_applications(job_vacancies(title), jobseeker_profiles(first_name, last_name))")
        .order("scheduled_at", desc=True)
        .limit(100)
        .execute()
    )
    return api_ok(resp.data or [])


@staff_bp.route("/employment", methods=["GET", "PATCH"])
@role_required("staff")
def employment():
    supabase = get_supabase()
    if request.method == "GET":
        resp = (
            supabase.table("employment_records")
            .select("*, jobseeker_profiles(first_name, last_name), employer_profiles(company_name)")
            .order("created_at", desc=True)
            .execute()
        )
        return api_ok(resp.data or [])

    body = request.get_json(silent=True) or {}
    record_id = body.get("id")
    if not record_id:
        return api_err("id is required.", 422)
    allowed = {"start_date", "end_date", "employment_type", "status"}
    updates = {k: v for k, v in body.items() if k in allowed}
    resp = (
        supabase.table("employment_records")
        .update(updates)
        .eq("id", record_id)
        .execute()
    )
    return api_ok(resp.data[0] if resp.data else updates, "Employment record updated.")


@staff_bp.route("/job-fairs", methods=["GET", "POST"])
@role_required("staff")
def job_fairs():
    supabase = get_supabase()
    if request.method == "GET":
        resp = supabase.table("job_fairs").select("*").order("event_date", desc=True).execute()
        return api_ok(resp.data or [])

    body = request.get_json(silent=True) or {}
    required = ["title", "event_date", "start_time", "end_time", "venue"]
    missing = [f for f in required if not body.get(f)]
    if missing:
        return api_err(f"Missing: {', '.join(missing)}", 422)

    payload = {
        "title": body["title"],
        "description": body.get("description"),
        "event_date": body["event_date"],
        "start_time": body["start_time"],
        "end_time": body["end_time"],
        "venue": body["venue"],
        "status": "upcoming",
        "created_by": get_jwt_identity(),
    }
    resp = supabase.table("job_fairs").insert(payload).execute()
    return api_ok(resp.data[0], "Job fair created.", 201)


@staff_bp.route("/job-fairs/<fair_id>/scan", methods=["POST"])
@role_required("staff")
def scan_job_fair(fair_id: str):
    body = request.get_json(silent=True) or {}
    token = (body.get("token") or "").strip()
    if not token:
        return api_err("token is required.", 422)

    valid, data = validate_scan(token, fair_id)
    if not valid:
        return api_err(data.get("error", "Invalid QR code."), 422)

    supabase = get_supabase()
    reg = (
        supabase.table("job_fair_registrations")
        .select("id")
        .eq("job_fair_id", fair_id)
        .eq("jobseeker_id", data["participant_id"])
        .limit(1)
        .execute()
    )
    if not reg.data:
        return api_err("Registration not found.", 404)

    supabase.table("job_fair_attendance").insert(
        {
            "registration_id": reg.data[0]["id"],
            "scanned_by": get_jwt_identity(),
        }
    ).execute()
    return api_ok(data, "Attendance recorded.")


@staff_bp.route("/programs/<program_type>", methods=["GET", "PATCH"])
@role_required("staff")
def programs(program_type: str):
    if program_type not in PROGRAM_TYPES:
        return api_err("Invalid program type.", 422)
    supabase = get_supabase()

    if request.method == "GET":
        resp = (
            supabase.table("program_applications")
            .select("*, jobseeker_profiles(first_name, last_name, phone)")
            .eq("program_type", program_type)
            .order("created_at", desc=True)
            .execute()
        )
        return api_ok(resp.data or [])

    body = request.get_json(silent=True) or {}
    app_id = body.get("id")
    status = body.get("status")
    if not app_id or status not in ("approved", "rejected"):
        return api_err("id and status (approved/rejected) required.", 422)

    supabase.table("program_applications").update(
        {
            "status": status,
            "decision_reason": body.get("reason"),
            "reviewed_by": get_jwt_identity(),
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", app_id).execute()

    app = (
        supabase.table("program_applications")
        .select("jobseeker_id")
        .eq("id", app_id)
        .limit(1)
        .execute()
    )
    if app.data:
        seeker = (
            supabase.table("jobseeker_profiles")
            .select("user_id")
            .eq("id", app.data[0]["jobseeker_id"])
            .limit(1)
            .execute()
        )
        if seeker.data:
            send_inapp(
                seeker.data[0]["user_id"],
                "notification",
                {
                    "title": f"Program {program_type.upper()} {status}",
                    "body": body.get("reason") or f"Your application was {status}.",
                },
            )
    return api_ok({"status": status}, "Application updated.")


@staff_bp.route("/lmi-reports", methods=["GET"])
@role_required("staff")
def lmi_reports():
    supabase = get_supabase()
    resp = (
        supabase.table("lmi_reports")
        .select("*")
        .order("generated_at", desc=True)
        .execute()
    )
    return api_ok(resp.data or [])


@staff_bp.route("/announcements", methods=["POST"])
@role_required("staff")
def announcements():
    body = request.get_json(silent=True) or {}
    title = (body.get("title") or "").strip()
    message = (body.get("body") or "").strip()
    audience = body.get("audience", "jobseeker")
    if not title or not message:
        return api_err("title and body are required.", 422)

    supabase = get_supabase()
    role_filter = audience if audience in ("jobseeker", "employer") else "jobseeker"
    users = supabase.table("users").select("id").eq("role", role_filter).eq("is_active", True).execute()
    count = 0
    for u in users.data or []:
        send_inapp(
            u["id"],
            "announcement",
            {"title": title, "body": message},
        )
        count += 1
    return api_ok({"sent": count}, f"Announcement sent to {count} users.")


@staff_bp.route("/notifications", methods=["GET"])
@role_required("staff")
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


@staff_bp.route("/settings", methods=["GET"])
@role_required("staff")
def settings():
    supabase = get_supabase()
    resp = supabase.table("system_settings").select("key, value, description").execute()
    return api_ok(resp.data or [])
