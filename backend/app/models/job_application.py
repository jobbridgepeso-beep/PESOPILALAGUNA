"""
JobApplication ORM model.

Maps to the ``job_applications`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job_vacancy import JobVacancy
    from app.models.jobseeker_profile import JobseekerProfile
    from app.models.interview import Interview
    from app.models.referral_letter import ReferralLetter
    from app.models.employment_record import EmploymentRecord


class JobApplication(Base):
    """A jobseeker's application to a specific job vacancy."""

    __tablename__ = "job_applications"
    __table_args__ = (UniqueConstraint("vacancy_id", "jobseeker_id", name="uq_application"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_vacancies.id", ondelete="CASCADE"),
        nullable=False,
    )
    jobseeker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobseeker_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    match_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    vacancy: Mapped["JobVacancy"] = relationship(
        "JobVacancy", back_populates="job_applications"
    )
    jobseeker: Mapped["JobseekerProfile"] = relationship(
        "JobseekerProfile", back_populates="job_applications"
    )
    interviews: Mapped[List["Interview"]] = relationship(
        "Interview", back_populates="application", cascade="all, delete-orphan"
    )
    referral_letters: Mapped[List["ReferralLetter"]] = relationship(
        "ReferralLetter", back_populates="application", cascade="all, delete-orphan"
    )
    employment_records: Mapped[List["EmploymentRecord"]] = relationship(
        "EmploymentRecord",
        back_populates="application",
        foreign_keys="EmploymentRecord.application_id",
    )

    def __repr__(self) -> str:
        return (
            f"<JobApplication id={self.id!s} vacancy_id={self.vacancy_id!s} "
            f"jobseeker_id={self.jobseeker_id!s} status={self.status!r}>"
        )
