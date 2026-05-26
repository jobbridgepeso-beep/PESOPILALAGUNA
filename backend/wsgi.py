"""
WSGI entry point for the JobBridge Flask application.

Used by Gunicorn in production:
    gunicorn wsgi:app --worker-class eventlet -w 1 --bind 0.0.0.0:5000

The single-worker constraint is required by Flask-SocketIO when using
the eventlet async mode with a Redis message queue.
"""

import os
from app import create_app
from app.extensions import socketio

config_name = os.environ.get("FLASK_ENV", "production")
app = create_app(config_name)

if __name__ == "__main__":
    # Development convenience: run with SocketIO's built-in server.
    # Do NOT use this in production — use Gunicorn instead.
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config.get("DEBUG", False),
    )
