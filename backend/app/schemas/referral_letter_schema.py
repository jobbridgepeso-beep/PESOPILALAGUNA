"""
ReferralLetterSchema — Marshmallow 3.x serialization schema for the
ReferralLetter model.
"""

from marshmallow import Schema, fields, validate


class ReferralLetterSchema(Schema):
    """Schema for the ``referral_letters`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    generated_at = fields.DateTime(dump_only=True)

    # --- Foreign keys ---
    application_id = fields.UUID(required=True)
    generated_by = fields.UUID(allow_none=True, load_default=None)

    # --- Required fields ---
    pdf_url = fields.String(
        required=True,
        validate=validate.Length(min=1),
        metadata={"description": "Supabase Storage URL for the generated PDF"},
    )
