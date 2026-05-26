"""
JobApplicationSchema — Marshmallow 3.x serialization schema for the
JobApplication model.
"""

from marshmallow import Schema, fields, validate

VALID_STATUSES = ("pending", "reviewed", "shortlisted", "rejected", "hired")


class JobApplicationSchema(Schema):
    """Schema for the ``job_applications`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    applied_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Foreign keys ---
    vacancy_id = fields.UUID(required=True)
    jobseeker_id = fields.UUID(required=True)

    # --- Status & scoring (server-managed) ---
    status = fields.String(
        load_default="pending",
        validate=validate.OneOf(
            VALID_STATUSES,
            error="status must be one of: pending, reviewed, shortlisted, rejected, hired",
        ),
    )
    match_score = fields.Decimal(
        allow_none=True,
        load_default=None,
        as_string=True,
        places=4,
        validate=validate.Range(
            min=0.0,
            max=1.0,
            error="match_score must be between 0.0 and 1.0",
        ),
    )

    # --- Applicant-supplied ---
    cover_letter = fields.String(allow_none=True, load_default=None)
