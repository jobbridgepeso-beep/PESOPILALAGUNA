"""
SQLAlchemy declarative base for all JobBridge ORM models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base class.

    All ORM models inherit from this class so that SQLAlchemy can
    discover the full metadata graph (tables, relationships, etc.)
    from a single registry.
    """
    pass
