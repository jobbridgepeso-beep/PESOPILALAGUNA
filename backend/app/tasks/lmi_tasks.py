"""
Celery tasks for LMI (Labour Market Information) report generation.

Full implementation is in task 11.2. This stub registers the task name
with Celery so that the worker can discover it and APScheduler can
dispatch it by name before the implementation is complete.
"""

from celery_worker import celery


@celery.task(bind=True, name="app.tasks.lmi_tasks.generate_lmi_report_task")
def generate_lmi_report_task(
    self,
    report_type: str,
    period_start: str,
    period_end: str,
    triggered_by: str | None = None,
) -> dict:
    """Generate an LMI report for the given period.

    Args:
        report_type:   One of 'monthly', 'quarterly', 'annual', 'custom'.
        period_start:  ISO-8601 date string for the start of the report period.
        period_end:    ISO-8601 date string for the end of the report period.
        triggered_by:  UUID of the user who triggered the report, or None for
                       scheduled runs.

    Returns:
        A dict with keys ``report_id``, ``pdf_url``, and ``excel_url`` once
        the full implementation is in place.

    Note:
        This is a stub. The full implementation (task 11.2) will:
        1. Call ``lmi_generator.compute_lmi_stats(period_start, period_end)``
        2. Generate PDF via ``pdf_service.generate_lmi_report_pdf()``
        3. Generate Excel via ``excel_service.generate_lmi_report_excel()``
        4. Upload both files to Supabase Storage (``lmi-reports`` bucket)
        5. Insert an ``lmi_reports`` record in the database
        6. Notify PESO Staff and Admin via ``notification_service.notify()``
    """
    # TODO: implement in task 11.2
    raise NotImplementedError(
        "generate_lmi_report_task is not yet implemented (see task 11.2)."
    )
