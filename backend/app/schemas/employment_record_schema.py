"""
EmploymentRecordSchema — Marshmallow 3.x serialization schema for the
EmploymentRecord model.
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError

VALID_EMPLOYMENT_TYPES = ("full-time", "part-time", "contract", "temporary")
VALID_STATUSES = ("active", "ended")


class EmploymentRecordSchema(Schema):
    """Schema for the ``employment_records`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Foreign keys ---
    jobseeker_id = fields.UUID(required=True)
    employer_id = fields.UUID(allow_none=True, load_default=None)
    vacancy_id = fields.UUID(allow_none=True, load_default=None)
    application_id = fields.UUID(allow_none=True, load_default=None)

    # --- Employment details ---
    employment_type = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.OneOf(
            VALID_EMPLOYMENT_TYPES,
            error="employment_type must be one of: full-time, part-time, contract, temporary",
        ),
    )
    start_date = fields.Date(allow_none=True, load_default=None, format="%Y-%m-%d")
    end_date = fields.Date(allow_none=True, load_default=None, format="%Y-%m-%d")
    status = fields.String(
        load_default="active",
        validate=validate.OneOf(
            VALID_STATUSES,
            error="status must be one of: active, ended",
        ),
    )

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        """Ensure end_date is not before start_date when both are provided."""
        start = data.get("start_date")
        end = data.get("end_date")
        if start is not None and end is not None and end < start:
            raise ValidationError(
                "end_date must be on or after start_date",
                field_name="end_date",
            )
