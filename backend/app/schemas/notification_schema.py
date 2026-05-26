"""
NotificationSchema — Marshmallow 3.x serialization schema for the
Notification model.
"""

from marshmallow import Schema, fields, validate


class NotificationSchema(Schema):
    """Schema for the ``notifications`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    user_id = fields.UUID(required=True)

    # --- Required fields ---
    event_type = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )

    # --- Optional fields ---
    body = fields.String(allow_none=True, load_default=None)
    payload = fields.Dict(
        allow_none=True,
        load_default=None,
        metadata={"description": "Arbitrary JSON payload attached to the notification"},
    )
    is_read = fields.Boolean(load_default=False)
