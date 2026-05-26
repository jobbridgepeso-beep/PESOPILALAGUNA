"""
models package — SQLAlchemy ORM models for the JobBridge system.

Import all models here so that:
  1. SQLAlchemy's mapper registry is fully populated before any
     ``Base.metadata.create_all()`` or Alembic migration call.
  2. Application code can do ``from app.models import User`` etc.
"""

from app.models.base import Base  # noqa: F401 — must be first

from app.models.user import User  # noqa: F401
from app.models.otp_token import OTPToken  # noqa: F401
from app.models.jobseeker_profile import JobseekerProfile  # noqa: F401
from app.models.employer_profile import EmployerProfile  # noqa: F401
from app.models.job_vacancy import JobVacancy  # noqa: F401
from app.models.job_application import JobApplication  # noqa: F401
from app.models.interview import Interview  # noqa: F401
from app.models.referral_letter import ReferralLetter  # noqa: F401
from app.models.job_fair import JobFair  # noqa: F401
from app.models.job_fair_registration import JobFairRegistration  # noqa: F401
from app.models.job_fair_attendance import JobFairAttendance  # noqa: F401
from app.models.program_application import ProgramApplication  # noqa: F401
from app.models.program_document import ProgramDocument  # noqa: F401
from app.models.employment_record import EmploymentRecord  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.audit_trail import AuditTrail  # noqa: F401
from app.models.lmi_report import LMIReport  # noqa: F401
from app.models.system_setting import SystemSetting  # noqa: F401

__all__ = [
    "Base",
    "User",
    "OTPToken",
    "JobseekerProfile",
    "EmployerProfile",
    "JobVacancy",
    "JobApplication",
    "Interview",
    "ReferralLetter",
    "JobFair",
    "JobFairRegistration",
    "JobFairAttendance",
    "ProgramApplication",
    "ProgramDocument",
    "EmploymentRecord",
    "Notification",
    "AuditTrail",
    "LMIReport",
    "SystemSetting",
]
