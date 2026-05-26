"""
Flask extension instances for the JobBridge application.

All extensions are instantiated here without being bound to an app.
They are initialised inside the app factory (create_app) via their
respective init_app() calls so that the application context is
available before any extension tries to use it.
"""

import os

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO
from supabase import Client, create_client

# ---------------------------------------------------------------------------
# Extension instances
# ---------------------------------------------------------------------------

cors = CORS()
jwt = JWTManager()
mail = Mail()
socketio = SocketIO()

# Supabase client — initialised lazily inside create_app so that the
# environment variables are guaranteed to be loaded first.
supabase_client: Client | None = None


def init_supabase(url: str, key: str) -> Client:
    """Create and return a Supabase client using the provided credentials."""
    global supabase_client
    supabase_client = create_client(url, key)
    return supabase_client


def get_supabase() -> Client:
    """Return the initialised Supabase client.

    Raises RuntimeError if called before init_supabase().
    """
    if supabase_client is None:
        raise RuntimeError(
            "Supabase client has not been initialised. "
            "Call init_supabase() inside the app factory first."
        )
    return supabase_client
