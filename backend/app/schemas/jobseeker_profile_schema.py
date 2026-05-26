"""
JobseekerProfileSchema — Marshmallow 3.x serialization schema for the
JobseekerProfile model, including nested EducationSchema and ExperienceSchema
for the JSONB education/experience fields.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError

VALID_GENDERS = ("male", "female", "non-binary", "prefer_not_to_say")
VALID_CIVIL_STATUSES = ("single", "married", "widowed", "separated", "divorced")


class EducationSchema(Schema):
    """Nested schema for a single education entry stored in the JSONB column."""

    degree = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    school = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    year_graduated = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1900, max=2100, error="year_graduated must be between 1900 and 2100"),
    )


class ExperienceSchema(Schema):
    """Nested schema for a single work-experience entry stored in the JSONB column."""

    company = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    position = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    start_date = fields.Date(
        required=True,
        format="%Y-%m-%d",
    )
    end_date = fields.Date(
        allow_none=True,
        load_default=None,
        format="%Y-%m-%d",
    )
    description = fields.String(
        allow_none=True,
        load_default=None,
    )


class JobseekerProfileSchema(Schema):
    """Schema for the ``jobseeker_profiles`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    user_id = fields.UUID(required=True)

    # --- Personal information ---
    first_name = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=100),
    )
    last_name = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=100),
    )
    middle_name = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=100),
    )
    birthdate = fields.Date(allow_none=True, load_default=None, format="%Y-%m-%d")
    gender = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.OneOf(
            VALID_GENDERS,
            error="gender must be one of: male, female, non-binary, prefer_not_to_say",
        ),
    )
    civil_status = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.OneOf(
            VALID_CIVIL_STATUSES,
            error="civil_status must be one of: single, married, widowed, separated, divorced",
        ),
    )
    address = fields.String(allow_none=True, load_default=None)
    phone = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(max=20),
    )

    # --- JSONB nested fields ---
    education = fields.List(
        fields.Nested(EducationSchema),
        allow_none=True,
        load_default=None,
    )
    experience = fields.List(
        fields.Nested(ExperienceSchema),
        allow_none=True,
        load_default=None,
    )

    # --- Array field ---
    skills = fields.List(
        fields.String(validate=validate.Length(min=1, max=100)),
        allow_none=True,
        load_default=None,
    )

    # --- File URLs (server-set) ---
    resume_url = fields.String(allow_none=True, load_default=None)
    profile_photo = fields.String(allow_none=True, load_default=None)
