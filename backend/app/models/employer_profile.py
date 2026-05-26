"""
EmployerProfile ORM model.

Maps to the ``employer_profiles`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_vacancy import JobVacancy
    from app.models.employment_record import EmploymentRecord


class EmployerProfile(Base):
    """Profile information for an employer user."""

    __tablename__ = "employer_profiles"

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
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    user: Mapped["User"] = relationship("User", back_populates="employer_profile")
    job_vacancies: Mapped[List["JobVacancy"]] = relationship(
        "JobVacancy", back_populates="employer", cascade="all, delete-orphan"
    )
    employment_records: Mapped[List["EmploymentRecord"]] = relationship(
        "EmploymentRecord",
        back_populates="employer",
        foreign_keys="EmploymentRecord.employer_id",
    )

    def __repr__(self) -> str:
        return (
            f"<EmployerProfile id={self.id!s} user_id={self.user_id!s} "
            f"company_name={self.company_name!r}>"
        )
