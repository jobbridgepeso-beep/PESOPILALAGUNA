"""
JobVacancySchema — Marshmallow 3.x serialization schema for the JobVacancy model.
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError

VALID_EMPLOYMENT_TYPES = ("full-time", "part-time", "contract", "temporary")
VALID_STATUSES = ("pending", "active", "rejected", "closed")


class JobVacancySchema(Schema):
    """Schema for the ``job_vacancies`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    approved_at = fields.DateTime(dump_only=True, allow_none=True)

    # --- Foreign keys ---
    employer_id = fields.UUID(required=True)
    approved_by = fields.UUID(allow_none=True, load_default=None)

    # --- Required fields ---
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=1),
    )
    requirements = fields.String(
        required=True,
        validate=validate.Length(min=1),
    )

    # --- Optional fields ---
    skills_required = fields.List(
        fields.String(validate=validate.Length(min=1, max=100)),
        allow_none=True,
        load_default=None,
    )
    employment_type = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.OneOf(
            VALID_EMPLOYMENT_TYPES,
            error="employment_type must be one of: full-time, part-time, contract, temporary",
        ),
    )
    salary_min = fields.Decimal(
        allow_none=True,
        load_default=None,
        as_string=True,
        places=2,
        validate=validate.Range(min=0, error="salary_min must be non-negative"),
    )
    salary_max = fields.Decimal(
        allow_none=True,
        load_default=None,
        as_string=True,
        places=2,
        validate=validate.Range(min=0, error="salary_max must be non-negative"),
    )
    slots = fields.Integer(
        load_default=1,
        validate=validate.Range(min=1, error="slots must be at least 1"),
    )
    status = fields.String(
        load_default="pending",
        validate=validate.OneOf(
            VALID_STATUSES,
            error="status must be one of: pending, active, rejected, closed",
        ),
    )
    rejection_reason = fields.String(allow_none=True, load_default=None)

    @validates_schema
    def validate_salary_range(self, data, **kwargs):
        """Ensure salary_max >= salary_min when both are provided."""
        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")
        if salary_min is not None and salary_max is not None:
            if salary_max < salary_min:
                raise ValidationError(
                    "salary_max must be greater than or equal to salary_min",
                    field_name="salary_max",
                )
