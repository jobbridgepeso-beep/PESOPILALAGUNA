"""
File validation utilities for the JobBridge application.

Validates uploaded files against MIME type and size constraints.
Requirements: 19.1, 19.2, 19.4
"""

from __future__ import annotations

import magic  # python-magic

# Accepted MIME types for all upload endpoints (Requirement 19.1)
ACCEPTED_MIME_TYPES = frozenset(["image/jpeg", "image/png", "application/pdf"])

# Maximum file size: 5 MB (Requirement 19.2)
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5,242,880 bytes


def validate_file(file_bytes: bytes, filename: str) -> tuple[bool, str]:
    """Validate a file against JobBridge upload rules.

    Checks:
      1. File size does not exceed 5 MB.
      2. MIME type (detected from file content, not extension) is in the
         accepted set: image/jpeg, image/png, application/pdf.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename:   Original filename (used only for error messages).

    Returns:
        ``(True, "")`` if the file is valid.
        ``(False, error_message)`` if the file is invalid.

    Requirements: 4.3, 19.1, 19.2, 19.4
    """
    # --- Size check ---
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return False, "File exceeds the 5MB size limit."

    # --- MIME type check (server-side, content-based) ---
    try:
        mime = magic.from_buffer(file_bytes, mime=True)
    except Exception:
        return False, "Could not determine file type. Please upload a JPG, PNG, or PDF."

    if mime not in ACCEPTED_MIME_TYPES:
        return False, "Only JPG, PNG, and PDF files are accepted."

    return True, ""
