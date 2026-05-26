"""
Celery tasks for asynchronous notification delivery.

Offloading notification sends to a Celery worker ensures that email
delivery (which can be slow) does not block the HTTP request cycle.
"""

from celery_worker import celery


@celery.task(bind=True, name="app.tasks.notification_tasks.send_email_task")
def send_email_task(
    self,
    to_email: str,
    subject: str,
    template: str,
    context: dict,
) -> None:
    """Send a transactional email asynchronously.

    Args:
        to_email:  Recipient email address.
        subject:   Email subject line.
        template:  Jinja2 template name (relative to ``templates/email/``).
        context:   Template rendering context dict.

    Note:
        This is a stub. The full implementation will delegate to
        ``notification_service.send_email()`` once that service is
        implemented in task 8.1.
    """
    # TODO: implement in task 8.1
    raise NotImplementedError(
        "send_email_task is not yet implemented (see task 8.1)."
    )


@celery.task(bind=True, name="app.tasks.notification_tasks.send_inapp_notification_task")
def send_inapp_notification_task(
    self,
    user_id: str,
    event_type: str,
    payload: dict,
) -> None:
    """Persist and emit an in-app notification asynchronously.

    Args:
        user_id:    UUID of the target user.
        event_type: Notification event type string (e.g. 'application_update').
        payload:    Arbitrary JSON-serialisable payload dict.

    Note:
        This is a stub. The full implementation will delegate to
        ``notification_service.send_inapp()`` once that service is
        implemented in task 8.1.
    """
    # TODO: implement in task 8.1
    raise NotImplementedError(
        "send_inapp_notification_task is not yet implemented (see task 8.1)."
    )
