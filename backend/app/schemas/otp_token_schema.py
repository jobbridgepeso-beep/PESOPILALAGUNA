"""
OTPTokenSchema — Marshmallow 3.x serialization schema for the OTPToken model.
"""

from marshmallow import Schema, fields, validate

VALID_PURPOSES = ("registration", "password_reset")


class OTPTokenSchema(Schema):
    """Schema for the ``otp_tokens`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # --- Readable fields ---
    user_id = fields.UUID(required=True)
    token = fields.String(
        required=True,
        validate=validate.Length(equal=6, error="OTP token must be exactly 6 characters"),
    )
    purpose = fields.String(
        required=True,
        validate=validate.OneOf(VALID_PURPOSES, error="purpose must be one of: registration, password_reset"),
    )
    expires_at = fields.DateTime(required=True)
    used_at = fields.DateTime(allow_none=True, load_default=None)
