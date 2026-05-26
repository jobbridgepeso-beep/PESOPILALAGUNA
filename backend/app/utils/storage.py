"""
Supabase Storage upload/delete helpers for the JobBridge application.

Requirements: 19.3
"""

from __future__ import annotations

import logging
from typing import Optional

from app.extensions import get_supabase

logger = logging.getLogger(__name__)


def upload_file(
    bucket: str,
    path: str,
    file_bytes: bytes,
    content_type: str,
) -> str:
    """Upload a file to Supabase Storage and return its public/signed URL.

    Args:
        bucket:       Bucket name (e.g. ``'resumes'``, ``'qr-codes'``).
        path:         Object path within the bucket (e.g. ``'user_id/resume.pdf'``).
        file_bytes:   Raw file content.
        content_type: MIME type string (e.g. ``'application/pdf'``).

    Returns:
        The public URL string for public buckets, or a signed URL for private
        buckets (valid for 1 hour).

    Raises:
        RuntimeError: If the upload fails.
    """
    supabase = get_supabase()

    try:
        supabase.storage.from_(bucket).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"},
        )
    except Exception as exc:
        logger.error("Storage upload failed: bucket=%s path=%s error=%s", bucket, path, exc)
        raise RuntimeError(f"Failed to upload file to {bucket}/{path}: {exc}") from exc

    # Return public URL for public buckets; signed URL for private buckets
    _PUBLIC_BUCKETS = {"company-logos", "profile-photos"}
    if bucket in _PUBLIC_BUCKETS:
        url_resp = supabase.storage.from_(bucket).get_public_url(path)
        return url_resp
    else:
        signed = supabase.storage.from_(bucket).create_signed_url(path, expires_in=3600)
        return signed.get("signedURL") or signed.get("signedUrl", "")


def delete_file(bucket: str, path: str) -> None:
    """Delete a file from Supabase Storage.

    Args:
        bucket: Bucket name.
        path:   Object path within the bucket.

    Raises:
        RuntimeError: If the deletion fails.
    """
    supabase = get_supabase()
    try:
        supabase.storage.from_(bucket).remove([path])
        logger.info("Deleted storage object: bucket=%s path=%s", bucket, path)
    except Exception as exc:
        logger.error("Storage delete failed: bucket=%s path=%s error=%s", bucket, path, exc)
        raise RuntimeError(f"Failed to delete file {bucket}/{path}: {exc}") from exc
