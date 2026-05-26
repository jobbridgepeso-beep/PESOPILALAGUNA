"""
JobVacancy ORM model.

Maps to the ``job_vacancies`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.employer_profile import EmployerProfile
    from app.models.user import User
    from app.models.job_application import JobApplication
    from app.models.employment_record import EmploymentRecord


class JobVacancy(Base):
    """A job vacancy posted by an employer."""

    __tablename__ = "job_vacancies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employer_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    skills_required: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    salary_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    salary_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    slots: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    employer: Mapped["EmployerProfile"] = relationship(
        "EmployerProfile", back_populates="job_vacancies"
    )
    approver: Mapped[Optional["User"]] = relationship(
        "User", back_populates="approved_vacancies", foreign_keys=[approved_by]
    )
    job_applications: Mapped[List["JobApplication"]] = relationship(
        "JobApplication", back_populates="vacancy", cascade="all, delete-orphan"
    )
    employment_records: Mapped[List["EmploymentRecord"]] = relationship(
        "EmploymentRecord",
        back_populates="vacancy",
        foreign_keys="EmploymentRecord.vacancy_id",
    )

    def __repr__(self) -> str:
        return (
            f"<JobVacancy id={self.id!s} title={self.title!r} "
            f"status={self.status!r} employer_id={self.employer_id!s}>"
        )
