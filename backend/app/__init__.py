"""
JobBridge Flask Application Factory.

Usage:
    from app import create_app
    app = create_app()          # uses FLASK_ENV or defaults to 'development'
    app = create_app('testing') # explicit environment
"""

import os
from flask import Flask, jsonify

from app.config import config_map
from app.extensions import cors, jwt, mail, socketio, init_supabase


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: One of 'development', 'testing', 'production'.
                     Falls back to the FLASK_ENV environment variable,
                     then to 'default' (DevelopmentConfig).

    Returns:
        A fully configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__, instance_relative_config=False)

    # ------------------------------------------------------------------
    # Load configuration
    # ------------------------------------------------------------------
    cfg_class = config_map.get(config_name, config_map["default"])
    app.config.from_object(cfg_class)

    # ------------------------------------------------------------------
    # Initialise extensions
    # ------------------------------------------------------------------
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGINS"],
        message_queue=app.config.get("SOCKETIO_MESSAGE_QUEUE"),
        async_mode="eventlet",
    )

    # Supabase — only initialise when credentials are present so that
    # unit tests that don't need a real DB can still boot the app.
    supabase_url = app.config.get("SUPABASE_URL", "")
    # Server-side routes use the service role key to bypass RLS safely.
    supabase_key = app.config.get("SUPABASE_SERVICE_KEY") or app.config.get(
        "SUPABASE_KEY", ""
    )
    if supabase_url and supabase_key:
        init_supabase(supabase_url, supabase_key)

    # ------------------------------------------------------------------
    # Register blueprints
    # ------------------------------------------------------------------
    _register_blueprints(app)

    # ------------------------------------------------------------------
    # Register centralised error handlers
    # ------------------------------------------------------------------
    _register_error_handlers(app)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify(
            {"success": True, "data": {"status": "ok"}, "message": "JobBridge API is running."}
        )

    return app


# ---------------------------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------------------------

def _register_blueprints(app: Flask) -> None:
    """Import and register all Flask blueprints."""

    # Auth blueprint — /api/auth
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Jobseeker blueprint — /api/jobseeker
    from app.blueprints.jobseeker import jobseeker_bp
    app.register_blueprint(jobseeker_bp, url_prefix="/api/jobseeker")

    # Employer blueprint — /api/employer
    from app.blueprints.employer import employer_bp
    app.register_blueprint(employer_bp, url_prefix="/api/employer")

    # PESO Staff blueprint — /api/staff
    from app.blueprints.staff import staff_bp
    app.register_blueprint(staff_bp, url_prefix="/api/staff")

    # Admin blueprint — /api/admin
    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")


# ---------------------------------------------------------------------------
# Centralised error handlers
# ---------------------------------------------------------------------------

def _register_error_handlers(app: Flask) -> None:
    """Register application-wide HTTP and generic exception handlers."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "data": None, "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "data": None, "message": str(e)}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "data": None, "message": str(e)}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "data": None, "message": str(e)}), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({"success": False, "data": None, "message": str(e)}), 409

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return (
            jsonify(
                {
                    "success": False,
                    "data": None,
                    "message": "File exceeds the 5MB size limit.",
                }
            ),
            413,
        )

    @app.errorhandler(415)
    def unsupported_media_type(e):
        return (
            jsonify(
                {
                    "success": False,
                    "data": None,
                    "message": "Only JPG, PNG, and PDF files are accepted.",
                }
            ),
            415,
        )

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({"success": False, "data": None, "message": str(e)}), 422

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"success": False, "data": None, "message": str(e)}), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        return (
            jsonify(
                {
                    "success": False,
                    "data": None,
                    "message": "An internal server error occurred.",
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Catch-all for any unhandled exception."""
        app.logger.exception("Unhandled exception: %s", e)
        return (
            jsonify(
                {
                    "success": False,
                    "data": None,
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )
