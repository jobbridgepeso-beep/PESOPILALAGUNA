"""
JobFairAttendance ORM model.

Maps to the ``job_fair_attendance`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job_fair_registration import JobFairRegistration
    from app.models.user import User


class JobFairAttendance(Base):
    """An attendance record created when a jobseeker's QR code is scanned."""

    __tablename__ = "job_fair_attendance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    registration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_fair_registrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    scanned_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    scanned_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    registration: Mapped["JobFairRegistration"] = relationship(
        "JobFairRegistration", back_populates="attendance_records"
    )
    scanner: Mapped[Optional["User"]] = relationship(
        "User", back_populates="scanned_attendances", foreign_keys=[scanned_by]
    )

    def __repr__(self) -> str:
        return (
            f"<JobFairAttendance id={self.id!s} registration_id={self.registration_id!s} "
            f"scanned_at={self.scanned_at!r}>"
        )
