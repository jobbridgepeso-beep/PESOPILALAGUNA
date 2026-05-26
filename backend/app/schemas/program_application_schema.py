"""
ProgramApplicationSchema — Marshmallow 3.x serialization schema for the
ProgramApplication model.
"""

from marshmallow import Schema, fields, validate

VALID_PROGRAM_TYPES = ("spes", "dilp", "owwa", "mst")
VALID_STATUSES = ("pending", "approved", "rejected")


class ProgramApplicationSchema(Schema):
    """Schema for the ``program_applications`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    reviewed_at = fields.DateTime(dump_only=True, allow_none=True)

    # --- Foreign keys ---
    jobseeker_id = fields.UUID(required=True)
    reviewed_by = fields.UUID(allow_none=True, load_default=None)

    # --- Required fields ---
    program_type = fields.String(
        required=True,
        validate=validate.OneOf(
            VALID_PROGRAM_TYPES,
            error="program_type must be one of: spes, dilp, owwa, mst",
        ),
    )

    # --- Status (server-managed) ---
    status = fields.String(
        load_default="pending",
        validate=validate.OneOf(
            VALID_STATUSES,
            error="status must be one of: pending, approved, rejected",
        ),
    )
    decision_reason = fields.String(allow_none=True, load_default=None)
