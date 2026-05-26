"""
ProgramDocumentSchema — Marshmallow 3.x serialization schema for the
ProgramDocument model.

File validation (MIME type + size) is handled at the upload layer
(OCRProcessor.validate_file); this schema validates the metadata record
that is persisted after a successful upload.
"""

from marshmallow import Schema, fields, validate

# Allowed document types for program applications
VALID_DOCUMENT_TYPES = (
    "birth_certificate",
    "barangay_clearance",
    "school_id",
    "employment_certificate",
    "medical_certificate",
    "valid_id",
    "other",
)


class ProgramDocumentSchema(Schema):
    """Schema for the ``program_documents`` table."""

    # --- Server-generated ---
    id = fields.UUID(dump_only=True)
    uploaded_at = fields.DateTime(dump_only=True)

    # --- Foreign key ---
    application_id = fields.UUID(required=True)

    # --- Required fields ---
    document_type = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "Type/category of the uploaded document"},
    )
    file_url = fields.String(
        required=True,
        validate=validate.Length(min=1),
        metadata={"description": "Supabase Storage URL for the uploaded file"},
    )

    # --- OCR output (server-set, optional) ---
    ocr_data = fields.Dict(
        allow_none=True,
        load_default=None,
        metadata={"description": "Structured data extracted by OCR from the document"},
    )
