"""
SystemSettingSchema — Marshmallow 3.x serialization schema for the
SystemSetting model.
"""

from marshmallow import Schema, fields, validate


class SystemSettingSchema(Schema):
    """Schema for the ``system_settings`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    updated_by = fields.UUID(allow_none=True, load_default=None)

    # --- Required fields ---
    key = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "Unique setting key (e.g. 'max_file_size_mb')"},
    )
    value = fields.String(
        required=True,
        validate=validate.Length(min=1),
        metadata={"description": "Setting value stored as text"},
    )

    # --- Optional fields ---
    description = fields.String(allow_none=True, load_default=None)
