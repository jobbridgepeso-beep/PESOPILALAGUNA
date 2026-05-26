"""
AuditTrail ORM model.

Maps to the ``audit_trail`` table in the JobBridge PostgreSQL schema.

This table is append-only: no UPDATE or DELETE operations are permitted
at the database level (enforced via RLS policies).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditTrail(Base):
    """An immutable audit log entry recording a significant system action."""

    __tablename__ = "audit_trail"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    actor: Mapped[Optional["User"]] = relationship(
        "User", back_populates="audit_entries", foreign_keys=[actor_id]
    )

    def __repr__(self) -> str:
        return (
            f"<AuditTrail id={self.id!s} actor_id={self.actor_id!s} "
            f"action_type={self.action_type!r} resource_type={self.resource_type!r}>"
        )