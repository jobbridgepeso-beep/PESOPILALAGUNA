"""
AuditTrailSchema — Marshmallow 3.x serialization schema for the AuditTrail model.

The audit_trail table is append-only; all fields are effectively dump_only
except those supplied at write time (actor_id, actor_role, action_type, etc.).
"""

from marshmallow import Schema, fields, validate

VALID_ROLES = ("jobseeker", "employer", "staff", "admin", "system")


class AuditTrailSchema(Schema):
    """Schema for the ``audit_trail`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # --- Required fields ---
    actor_role = fields.String(
        required=True,
        validate=validate.OneOf(
            VALID_ROLES,
            error="actor_role must be one of: jobseeker, employer, staff, admin, system",
        ),
    )
    action_type = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
    )

    # --- Optional fields ---
    actor_id = fields.UUID(allow_none=True, load_default=None)
    resource_type = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=100),
    )
    resource_id = fields.UUID(allow_none=True, load_default=None)
    ip_address = fields.String(
        allow_none=True,
        load_default=None,
        metadata={"description": "IPv4 or IPv6 address of the request origin"},
    )
    # Mapped from the ``metadata`` column (aliased as extra_metadata in the ORM)
    extra_metadata = fields.Dict(
        data_key="metadata",
        allow_none=True,
        load_default=None,
        metadata={"description": "Arbitrary JSON context for the audit event"},
    )
