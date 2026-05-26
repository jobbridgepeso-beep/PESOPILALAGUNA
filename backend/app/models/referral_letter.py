"""
ReferralLetter ORM model.

Maps to the ``referral_letters`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job_application import JobApplication
    from app.models.user import User


class ReferralLetter(Base):
    """A generated referral letter PDF for a job application."""

    __tablename__ = "referral_letters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    generated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    pdf_url: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    application: Mapped["JobApplication"] = relationship(
        "JobApplication", back_populates="referral_letters"
    )
    generator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="generated_referral_letters",
        foreign_keys=[generated_by],
    )

    def __repr__(self) -> str:
        return (
            f"<ReferralLetter id={self.id!s} application_id={self.application_id!s} "
            f"generated_at={self.generated_at!r}>"
        )
