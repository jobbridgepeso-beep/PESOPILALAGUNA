"""
InterviewSchema — Marshmallow 3.x serialization schema for the Interview model.
"""

from marshmallow import Schema, fields, validate

VALID_STATUSES = ("scheduled", "completed", "cancelled")


class InterviewSchema(Schema):
    """Schema for the ``interviews`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    application_id = fields.UUID(required=True)

    # --- Required fields ---
    scheduled_at = fields.DateTime(required=True)

    # --- Optional fields ---
    location = fields.String(allow_none=True, load_default=None)
    meeting_link = fields.Url(
        allow_none=True,
        load_default=None,
        relative=False,
        metadata={"description": "Video call / meeting URL"},
    )
    notes = fields.String(allow_none=True, load_default=None)
    status = fields.String(
        load_default="scheduled",
        validate=validate.OneOf(
            VALID_STATUSES,
            error="status must be one of: scheduled, completed, cancelled",
        ),
    )
