"""
Celery worker entry point for the JobBridge application.

Start the worker with:
    celery -A celery_worker.celery worker --loglevel=info

The Celery app is created here and bound to the Flask application context
so that tasks can access Flask extensions (DB, mail, etc.).
"""

import os
from celery import Celery
from app import create_app

# ---------------------------------------------------------------------------
# Create the Flask app and Celery instance
# ---------------------------------------------------------------------------

flask_app = create_app(os.environ.get("FLASK_ENV", "development"))


def make_celery(app) -> Celery:
    """Create a Celery instance that runs tasks inside the Flask app context."""
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(
        task_always_eager=app.config.get("CELERY_TASK_ALWAYS_EAGER", False),
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="Asia/Manila",
        enable_utc=True,
    )

    class ContextTask(celery.Task):
        """Ensure every task runs inside a Flask application context."""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(flask_app)

# ---------------------------------------------------------------------------
# Auto-discover tasks from the app.tasks package
# ---------------------------------------------------------------------------
celery.autodiscover_tasks(["app.tasks"])
