"""
JobFairAttendanceSchema — Marshmallow 3.x serialization schema for the
JobFairAttendance model.
"""

from marshmallow import Schema, fields


class JobFairAttendanceSchema(Schema):
    """Schema for the ``job_fair_attendance`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    scanned_at = fields.DateTime(dump_only=True)

    # --- Foreign keys ---
    registration_id = fields.UUID(required=True)
    scanned_by = fields.UUID(allow_none=True, load_default=None)
