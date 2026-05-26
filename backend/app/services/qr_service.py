"""
QR Code service for the JobBridge application.

Generates HMAC-signed QR tokens for job fair registrations and validates
scanned tokens.

Requirements: 10.1, 10.3, 10.4
"""

from __future__ import annotations

import hashlib
import hmac
import io
import logging
import time
from typing import Any

import qrcode
from flask import current_app

logger = logging.getLogger(__name__)


def _get_secret() -> bytes:
    """Return the HMAC signing secret from Flask config."""
    return current_app.config["SECRET_KEY"].encode("utf-8")


def _build_token(participant_id: str, event_id: str, timestamp: int) -> str:
    """Build a signed token string: ``{participant_id}:{event_id}:{timestamp}:{hmac}``."""
    message = f"{participant_id}:{event_id}:{timestamp}".encode("utf-8")
    signature = hmac.new(_get_secret(), message, hashlib.sha256).hexdigest()
    return f"{participant_id}:{event_id}:{timestamp}:{signature}"


def generate_qr(participant_id: str, event_id: str) -> bytes:
    """Generate a QR code PNG for a job fair registration.

    Creates an HMAC-signed token encoding the participant and event IDs,
    then renders it as a PNG image.

    Args:
        participant_id: UUID string of the registered jobseeker.
        event_id:       UUID string of the job fair event.

    Returns:
        PNG image bytes.

    Requirements: 10.1
    """
    timestamp = int(time.time())
    token = _build_token(participant_id, event_id, timestamp)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def validate_scan(token: str, event_id: str) -> tuple[bool, dict[str, Any]]:
    """Validate a scanned QR token.

    Verifies the HMAC signature and checks that the token belongs to the
    specified event.

    Args:
        token:    The raw token string scanned from the QR code.
        event_id: UUID string of the job fair event being scanned.

    Returns:
        ``(True, {"participant_id": ..., "event_id": ..., "timestamp": ...})``
        on success.
        ``(False, {"error": error_message})`` on failure.

    Requirements: 10.3, 10.4
    """
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return False, {"error": "Invalid QR code format."}

        p_id, e_id, ts_str, provided_sig = parts

        # Verify event_id matches
        if e_id != event_id:
            return False, {"error": "QR code does not belong to this event."}

        # Verify HMAC signature
        message = f"{p_id}:{e_id}:{ts_str}".encode("utf-8")
        expected_sig = hmac.new(_get_secret(), message, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_sig, provided_sig):
            return False, {"error": "Invalid QR code signature."}

        return True, {
            "participant_id": p_id,
            "event_id": e_id,
            "timestamp": int(ts_str),
        }

    except Exception as exc:
        logger.error("QR validation error: %s", exc, exc_info=True)
        return False, {"error": "QR code validation failed."}
