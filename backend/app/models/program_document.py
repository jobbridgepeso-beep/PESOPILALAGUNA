"""
ProgramDocument ORM model.

Maps to the ``program_documents`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.program_application import ProgramApplication


class ProgramDocument(Base):
    """A document uploaded as part of a program application."""

    __tablename__ = "program_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("program_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    ocr_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    application: Mapped["ProgramApplication"] = relationship(
        "ProgramApplication", back_populates="documents"
    )

    def __repr__(self) -> str:
        return (
            f"<ProgramDocument id={self.id!s} application_id={self.application_id!s} "
            f"document_type={self.document_type!r}>"
        )
