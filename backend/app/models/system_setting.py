"""
SystemSetting ORM model.

Maps to the ``system_settings`` table in the JobBridge PostgreSQL schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SystemSetting(Base):
    """A configurable system-wide key-value setting."""

    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    updater: Mapped[Optional["User"]] = relationship(
        "User", back_populates="updated_system_settings", foreign_keys=[updated_by]
    )

    def __repr__(self) -> str:
        return f"<SystemSetting id={self.id!s} key={self.key!r} value={self.value!r}>"
