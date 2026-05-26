"""
JobseekerProfile ORM model.

Maps to the ``jobseeker_profiles`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import Date, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_application import JobApplication
    from app.models.job_fair_registration import JobFairRegistration
    from app.models.program_application import ProgramApplication
    from app.models.employment_record import EmploymentRecord


class JobseekerProfile(Base):
    """Profile information for a jobseeker user."""

    __tablename__ = "jobseeker_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birthdate: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    civil_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    education: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    experience: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    resume_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    profile_photo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    user: Mapped["User"] = relationship("User", back_populates="jobseeker_profile")
    job_applications: Mapped[List["JobApplication"]] = relationship(
        "JobApplication", back_populates="jobseeker", cascade="all, delete-orphan"
    )
    job_fair_registrations: Mapped[List["JobFairRegistration"]] = relationship(
        "JobFairRegistration", back_populates="jobseeker", cascade="all, delete-orphan"
    )
    program_applications: Mapped[List["ProgramApplication"]] = relationship(
        "ProgramApplication", back_populates="jobseeker", cascade="all, delete-orphan"
    )
    employment_records: Mapped[List["EmploymentRecord"]] = relationship(
        "EmploymentRecord",
        back_populates="jobseeker",
        foreign_keys="EmploymentRecord.jobseeker_id",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<JobseekerProfile id={self.id!s} user_id={self.user_id!s} "
            f"name={self.first_name!r} {self.last_name!r}>"
        )
