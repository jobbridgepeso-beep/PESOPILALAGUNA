"""
OCR Processor service for the JobBridge application.

Uses Google Vision API for text extraction and spaCy NLP for entity
recognition to parse structured data from resume files.

Requirements: 4.1, 4.2, 11.1
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports — only loaded when actually called so the app boots without
# Google credentials configured.
_vision_client = None
_nlp = None


def _get_vision_client():
    global _vision_client
    if _vision_client is None:
        from google.cloud import vision
        _vision_client = vision.ImageAnnotatorClient()
    return _vision_client


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            _nlp = None
    return _nlp


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def extract_from_file(file_bytes: bytes, mime_type: str) -> dict[str, Any]:
    """Extract structured resume data from an uploaded file.

    Calls Google Vision API for text extraction, then passes the raw text
    through a spaCy NLP pipeline to identify named entities.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        mime_type:  MIME type string (``'image/jpeg'``, ``'image/png'``,
                    or ``'application/pdf'``).

    Returns:
        A dict with keys:
          - ``name``       (str | None)
          - ``email``      (str | None)
          - ``phone``      (str | None)
          - ``education``  (list[dict])
          - ``experience`` (list[dict])
          - ``skills``     (list[str])
          - ``raw_text``   (str)
          - ``ocr_confidence`` (float)  — 0.0 on failure

    Requirements: 4.1, 4.2
    """
    raw_text = ""
    ocr_confidence = 0.0

    try:
        raw_text, ocr_confidence = _extract_text_vision(file_bytes, mime_type)
    except Exception as exc:
        logger.error("Google Vision API failed: %s", exc, exc_info=True)
        # Return partial data — allow manual entry (Requirement 4.5)
        return _empty_result(ocr_confidence=0.0)

    if not raw_text.strip():
        return _empty_result(ocr_confidence=ocr_confidence)

    # NLP entity extraction
    try:
        structured = _extract_entities(raw_text)
    except Exception as exc:
        logger.error("spaCy NLP extraction failed: %s", exc, exc_info=True)
        structured = _empty_result(ocr_confidence=ocr_confidence)

    structured["raw_text"] = raw_text
    structured["ocr_confidence"] = ocr_confidence
    return structured


# ---------------------------------------------------------------------------
# Vision API helpers
# ---------------------------------------------------------------------------

def _extract_text_vision(file_bytes: bytes, mime_type: str) -> tuple[str, float]:
    """Call Google Vision API and return (raw_text, confidence)."""
    from google.cloud import vision

    client = _get_vision_client()
    image = vision.Image(content=file_bytes)

    if mime_type == "application/pdf":
        # For PDFs use document_text_detection
        response = client.document_text_detection(image=image)
    else:
        response = client.document_text_detection(image=image)

    if response.error.message:
        raise RuntimeError(f"Vision API error: {response.error.message}")

    full_text = response.full_text_annotation.text or ""

    # Compute average confidence from pages
    confidence = 0.0
    pages = response.full_text_annotation.pages
    if pages:
        page_confidences = []
        for page in pages:
            for block in page.blocks:
                page_confidences.append(block.confidence)
        if page_confidences:
            confidence = sum(page_confidences) / len(page_confidences)

    return full_text, confidence


# ---------------------------------------------------------------------------
# NLP entity extraction
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"(?:\+63|0)[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}")

_SKILL_KEYWORDS = {
    "python", "java", "javascript", "typescript", "react", "vue", "angular",
    "node", "flask", "django", "sql", "postgresql", "mysql", "mongodb",
    "html", "css", "git", "docker", "kubernetes", "aws", "azure", "gcp",
    "excel", "word", "powerpoint", "photoshop", "illustrator",
    "communication", "leadership", "teamwork", "problem solving",
    "customer service", "data analysis", "project management",
}


def _extract_entities(text: str) -> dict[str, Any]:
    """Use regex + spaCy to extract structured fields from raw resume text."""
    result = _empty_result()

    # --- Email ---
    email_match = _EMAIL_RE.search(text)
    if email_match:
        result["email"] = email_match.group(0)

    # --- Phone ---
    phone_match = _PHONE_RE.search(text)
    if phone_match:
        result["phone"] = re.sub(r"[\s\-]", "", phone_match.group(0))

    # --- Skills (keyword matching) ---
    text_lower = text.lower()
    found_skills = [skill for skill in _SKILL_KEYWORDS if skill in text_lower]
    result["skills"] = sorted(set(found_skills))

    # --- spaCy NER for name ---
    nlp = _get_nlp()
    if nlp:
        doc = nlp(text[:5000])  # Limit to first 5000 chars for performance
        for ent in doc.ents:
            if ent.label_ == "PERSON" and result["name"] is None:
                result["name"] = ent.text
            elif ent.label_ == "ORG":
                # Could be employer or school — add to experience/education heuristically
                pass

    return result


def _empty_result(ocr_confidence: float = 0.0) -> dict[str, Any]:
    return {
        "name": None,
        "email": None,
        "phone": None,
        "education": [],
        "experience": [],
        "skills": [],
        "raw_text": "",
        "ocr_confidence": ocr_confidence,
    }
