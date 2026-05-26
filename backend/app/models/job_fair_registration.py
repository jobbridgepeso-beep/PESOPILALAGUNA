"""
JobFairRegistration ORM model.

Maps to the ``job_fair_registrations`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job_fair import JobFair
    from app.models.jobseeker_profile import JobseekerProfile
    from app.models.job_fair_attendance import JobFairAttendance


class JobFairRegistration(Base):
    """A jobseeker's registration for a job fair event."""

    __tablename__ = "job_fair_registrations"
    __table_args__ = (
        UniqueConstraint("job_fair_id", "jobseeker_id", name="uq_job_fair_registration"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_fair_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_fairs.id", ondelete="CASCADE"),
        nullable=False,
    )
    jobseeker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobseeker_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    qr_token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    qr_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    job_fair: Mapped["JobFair"] = relationship("JobFair", back_populates="registrations")
    jobseeker: Mapped["JobseekerProfile"] = relationship(
        "JobseekerProfile", back_populates="job_fair_registrations"
    )
    attendance_records: Mapped[List["JobFairAttendance"]] = relationship(
        "JobFairAttendance", back_populates="registration", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<JobFairRegistration id={self.id!s} job_fair_id={self.job_fair_id!s} "
            f"jobseeker_id={self.jobseeker_id!s}>"
        )
