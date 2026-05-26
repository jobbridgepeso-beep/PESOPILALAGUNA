"""
LMIReportSchema — Marshmallow 3.x serialization schema for the LMIReport model.
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError

VALID_REPORT_TYPES = ("monthly", "quarterly", "annual", "custom")


class LMIReportSchema(Schema):
    """Schema for the ``lmi_reports`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    generated_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    generated_by = fields.UUID(allow_none=True, load_default=None)

    # --- Required fields ---
    report_type = fields.String(
        required=True,
        validate=validate.OneOf(
            VALID_REPORT_TYPES,
            error="report_type must be one of: monthly, quarterly, annual, custom",
        ),
    )
    period_start = fields.Date(required=True, format="%Y-%m-%d")
    period_end = fields.Date(required=True, format="%Y-%m-%d")

    # --- Output file URLs (server-set) ---
    pdf_url = fields.String(allow_none=True, load_default=None)
    excel_url = fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_period(self, data, **kwargs):
        """Ensure period_end is not before period_start."""
        start = data.get("period_start")
        end = data.get("period_end")
        if start is not None and end is not None and end < start:
            raise ValidationError(
                "period_end must be on or after period_start",
                field_name="period_end",
            )
