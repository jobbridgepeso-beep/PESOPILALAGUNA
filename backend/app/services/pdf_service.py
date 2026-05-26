"""
PDF generation service for the JobBridge application.

Uses WeasyPrint with Jinja2 HTML templates to generate PDF documents.

Requirements: 8.4, 13.2
"""

from __future__ import annotations

import logging
from typing import Any

from flask import render_template

logger = logging.getLogger(__name__)


def generate_referral_letter(application_data: dict[str, Any]) -> bytes:
    """Generate a referral letter PDF for a job application.

    Args:
        application_data: Dict containing jobseeker, employer, and vacancy info.

    Returns:
        PDF bytes.

    Requirements: 8.4
    """
    from weasyprint import HTML

    html_content = render_template(
        "pdf/referral_letter.html", **application_data
    )
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes


def generate_lmi_report_pdf(report_data: dict[str, Any]) -> bytes:
    """Generate an LMI report PDF.

    Args:
        report_data: Dict containing LMI statistics and metadata.

    Returns:
        PDF bytes.

    Requirements: 13.2
    """
    from weasyprint import HTML

    html_content = render_template("pdf/lmi_report.html", **report_data)
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes
