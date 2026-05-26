"""
EmployerProfileSchema — Marshmallow 3.x serialization schema for the
EmployerProfile model.
"""

from marshmallow import Schema, fields, validate


class EmployerProfileSchema(Schema):
    """Schema for the ``employer_profiles`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    user_id = fields.UUID(required=True)

    # --- Company information ---
    company_name = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=255),
    )
    industry = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=100),
    )
    address = fields.String(allow_none=True, load_default=None)
    phone = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=20),
    )
    website = fields.Url(
        allow_none=True,
        load_default=None,
        relative=False,
        metadata={"description": "Company website URL"},
    )
    description = fields.String(allow_none=True, load_default=None)
    logo_url = fields.String(allow_none=True, load_default=None)
