"""
Celery task definitions for the JobBridge application.

Tasks are auto-discovered by the Celery worker via:
    celery.autodiscover_tasks(["app.tasks"])

Submodules:
    lmi_tasks           — LMI report generation tasks (task 11.2)
    notification_tasks  — Async notification delivery tasks
"""
