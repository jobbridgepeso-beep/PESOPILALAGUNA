"""
EmploymentRecord ORM model.

Maps to the ``employment_records`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.jobseeker_profile import JobseekerProfile
    from app.models.employer_profile import EmployerProfile
    from app.models.job_vacancy import JobVacancy
    from app.models.job_application import JobApplication


class EmploymentRecord(Base):
    """An employment record linking a jobseeker to an employer/vacancy."""

    __tablename__ = "employment_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    jobseeker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobseeker_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    employer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employer_profiles.id"),
        nullable=True,
    )
    vacancy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_vacancies.id"),
        nullable=True,
    )
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_applications.id"),
        nullable=True,
    )
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    jobseeker: Mapped["JobseekerProfile"] = relationship(
        "JobseekerProfile",
        back_populates="employment_records",
        foreign_keys=[jobseeker_id],
    )
    employer: Mapped[Optional["EmployerProfile"]] = relationship(
        "EmployerProfile",
        back_populates="employment_records",
        foreign_keys=[employer_id],
    )
    vacancy: Mapped[Optional["JobVacancy"]] = relationship(
        "JobVacancy",
        back_populates="employment_records",
        foreign_keys=[vacancy_id],
    )
    application: Mapped[Optional["JobApplication"]] = relationship(
        "JobApplication",
        back_populates="employment_records",
        foreign_keys=[application_id],
    )

    def __repr__(self) -> str:
        return (
            f"<EmploymentRecord id={self.id!s} jobseeker_id={self.jobseeker_id!s} "
            f"employer_id={self.employer_id!s} status={self.status!r}>"
        )
