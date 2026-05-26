"""
Configuration classes for the JobBridge Flask application.
Loads settings from environment variables via python-dotenv.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Shared configuration values across all environments."""

    # Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG: bool = False
    TESTING: bool = False

    # JWT (Flask-JWT-Extended)
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)
    JWT_TOKEN_LOCATION: list = ["headers", "cookies"]
    JWT_COOKIE_SECURE: bool = True
    JWT_COOKIE_SAMESITE: str = "Lax"
    JWT_COOKIE_CSRF_PROTECT: bool = False  # CSRF handled separately

    # CORS
    CORS_ORIGINS: list = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    # Flask-Mail (Gmail SMTP)
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER: str = os.environ.get("MAIL_USERNAME", "noreply@jobbridge.ph")
    MAIL_DEBUG: bool = False  # never leak SMTP credentials to logs

    # Supabase
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

    # Redis
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Celery
    CELERY_BROKER_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Dialogflow
    DIALOGFLOW_PROJECT_ID: str = os.environ.get("DIALOGFLOW_PROJECT_ID", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", ""
    )

    # File upload limits
    MAX_CONTENT_LENGTH: int = 5 * 1024 * 1024  # 5 MB

    # Flask-SocketIO
    SOCKETIO_MESSAGE_QUEUE: str = os.environ.get(
        "REDIS_URL", "redis://localhost:6379/0"
    )


class DevelopmentConfig(BaseConfig):
    """Development environment — debug on, cookies not secure."""

    DEBUG: bool = True
    JWT_COOKIE_SECURE: bool = False


class TestingConfig(BaseConfig):
    """Testing environment — eager Celery tasks, no real SMTP."""

    TESTING: bool = True
    DEBUG: bool = True
    JWT_COOKIE_SECURE: bool = False
    CELERY_TASK_ALWAYS_EAGER: bool = True
    MAIL_SUPPRESS_SEND: bool = True


class ProductionConfig(BaseConfig):
    """Production environment — strict security settings."""

    JWT_COOKIE_SECURE: bool = True
    JWT_COOKIE_CSRF_PROTECT: bool = True


# Mapping used by the app factory
config_map: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
