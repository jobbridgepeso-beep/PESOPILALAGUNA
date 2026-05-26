"""
User ORM model.

Maps to the ``users`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.otp_token import OTPToken
    from app.models.jobseeker_profile import JobseekerProfile
    from app.models.employer_profile import EmployerProfile
    from app.models.notification import Notification
    from app.models.audit_trail import AuditTrail
    from app.models.job_vacancy import JobVacancy
    from app.models.referral_letter import ReferralLetter
    from app.models.job_fair import JobFair
    from app.models.job_fair_attendance import JobFairAttendance
    from app.models.program_application import ProgramApplication
    from app.models.lmi_report import LMIReport
    from app.models.system_setting import SystemSetting


class User(Base):
    """Represents a registered user account."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    first_login: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    otp_tokens: Mapped[List["OTPToken"]] = relationship(
        "OTPToken", back_populates="user", cascade="all, delete-orphan"
    )
    jobseeker_profile: Mapped[Optional["JobseekerProfile"]] = relationship(
        "JobseekerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    employer_profile: Mapped[Optional["EmployerProfile"]] = relationship(
        "EmployerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    audit_entries: Mapped[List["AuditTrail"]] = relationship(
        "AuditTrail", back_populates="actor", foreign_keys="AuditTrail.actor_id"
    )
    approved_vacancies: Mapped[List["JobVacancy"]] = relationship(
        "JobVacancy", back_populates="approver", foreign_keys="JobVacancy.approved_by"
    )
    generated_referral_letters: Mapped[List["ReferralLetter"]] = relationship(
        "ReferralLetter", back_populates="generator", foreign_keys="ReferralLetter.generated_by"
    )
    created_job_fairs: Mapped[List["JobFair"]] = relationship(
        "JobFair", back_populates="creator", foreign_keys="JobFair.created_by"
    )
    scanned_attendances: Mapped[List["JobFairAttendance"]] = relationship(
        "JobFairAttendance", back_populates="scanner", foreign_keys="JobFairAttendance.scanned_by"
    )
    reviewed_program_applications: Mapped[List["ProgramApplication"]] = relationship(
        "ProgramApplication",
        back_populates="reviewer",
        foreign_keys="ProgramApplication.reviewed_by",
    )
    generated_lmi_reports: Mapped[List["LMIReport"]] = relationship(
        "LMIReport", back_populates="generator", foreign_keys="LMIReport.generated_by"
    )
    updated_system_settings: Mapped[List["SystemSetting"]] = relationship(
        "SystemSetting", back_populates="updater", foreign_keys="SystemSetting.updated_by"
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id!s} email={self.email!r} role={self.role!r} "
            f"is_active={self.is_active}>"
        )
