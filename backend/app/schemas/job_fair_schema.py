"""
JobFairSchema — Marshmallow 3.x serialization schema for the JobFair model.
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError

VALID_STATUSES = ("upcoming", "ongoing", "completed", "cancelled")


class JobFairSchema(Schema):
    """Schema for the ``job_fairs`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    created_by = fields.UUID(allow_none=True, load_default=None)

    # --- Required fields ---
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    event_date = fields.Date(required=True, format="%Y-%m-%d")
    start_time = fields.Time(required=True, format="%H:%M:%S")
    end_time = fields.Time(required=True, format="%H:%M:%S")
    venue = fields.String(
        required=True,
        validate=validate.Length(min=1),
    )

    # --- Optional fields ---
    description = fields.String(allow_none=True, load_default=None)
    status = fields.String(
        load_default="upcoming",
        validate=validate.OneOf(
            VALID_STATUSES,
            error="status must be one of: upcoming, ongoing, completed, cancelled",
        ),
    )

    @validates_schema
    def validate_time_range(self, data, **kwargs):
        """Ensure end_time is after start_time."""
        start = data.get("start_time")
        end = data.get("end_time")
        if start is not None and end is not None and end <= start:
            raise ValidationError(
                "end_time must be after start_time",
                field_name="end_time",
            )
