"""
JobFairRegistrationSchema — Marshmallow 3.x serialization schema for the
JobFairRegistration model.
"""

from marshmallow import Schema, fields, validate


class JobFairRegistrationSchema(Schema):
    """Schema for the ``job_fair_registrations`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    registered_at = fields.DateTime(dump_only=True)

    # --- Foreign keys ---
    job_fair_id = fields.UUID(required=True)
    jobseeker_id = fields.UUID(required=True)

    # --- QR fields (server-generated, read-only on output) ---
    qr_token = fields.String(
        dump_only=True,
        metadata={"description": "Unique signed QR token for attendance scanning"},
    )
    qr_url = fields.String(
        dump_only=True,
        allow_none=True,
        metadata={"description": "Supabase Storage URL for the QR code image"},
    )
