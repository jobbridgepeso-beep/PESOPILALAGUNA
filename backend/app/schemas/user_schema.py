"""
UserSchema — Marshmallow 3.x serialization schema for the User model.

password_hash is excluded from all output (dump_only fields are never
included in the serialised output when the field is also marked load_only,
but here we simply omit it from dump entirely via ``dump_default=marshmallow.missing``
and mark it load_only so it can only be supplied on input, never returned).
"""

from marshmallow import Schema, fields, validate, validates, ValidationError

# Valid roles as defined in the data model
VALID_ROLES = ("jobseeker", "employer", "staff", "admin")


class UserSchema(Schema):
    """Schema for the ``users`` table."""

    # --- Server-generated (read-only on output) ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Readable fields ---
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255),
        metadata={"description": "User's unique email address"},
    )
    role = fields.String(
        required=True,
        validate=validate.OneOf(VALID_ROLES, error="role must be one of: jobseeker, employer, staff, admin"),
    )
    is_active = fields.Boolean(dump_default=False)
    is_verified = fields.Boolean(dump_default=False)
    first_login = fields.Boolean(dump_default=True)

    # --- Write-only (never serialised to output) ---
    password_hash = fields.String(load_only=True)
