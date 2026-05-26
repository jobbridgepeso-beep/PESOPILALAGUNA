"""
ProgramApplication ORM model.

Maps to the ``program_applications`` table in the JobBridge PostgreSQL schema.
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
    from app.models.jobseeker_profile import JobseekerProfile
    from app.models.user import User
    from app.models.program_document import ProgramDocument


class ProgramApplication(Base):
    """A jobseeker's application to a PESO employment program (SPES, DILP, OWWA, MST)."""

    __tablename__ = "program_applications"

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
    program_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
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
    jobseeker: Mapped["JobseekerProfile"] = relationship(
        "JobseekerProfile", back_populates="program_applications"
    )
    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="reviewed_program_applications",
        foreign_keys=[reviewed_by],
    )
    documents: Mapped[List["ProgramDocument"]] = relationship(
        "ProgramDocument", back_populates="application", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<ProgramApplication id={self.id!s} jobseeker_id={self.jobseeker_id!s} "
            f"program_type={self.program_type!r} status={self.status!r}>"
        )
