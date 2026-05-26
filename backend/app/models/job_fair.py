"""
JobFair ORM model.

Maps to the ``job_fairs`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, ForeignKey, String, Text, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_fair_registration import JobFairRegistration


class JobFair(Base):
    """A job fair event organised by PESO staff."""

    __tablename__ = "job_fairs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    venue: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="upcoming")
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
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
    creator: Mapped[Optional["User"]] = relationship(
        "User", back_populates="created_job_fairs", foreign_keys=[created_by]
    )
    registrations: Mapped[List["JobFairRegistration"]] = relationship(
        "JobFairRegistration", back_populates="job_fair", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<JobFair id={self.id!s} title={self.title!r} "
            f"event_date={self.event_date!r} status={self.status!r}>"
        )
