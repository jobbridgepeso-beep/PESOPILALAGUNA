"""PESO Staff blueprint — /api/staff"""

from flask import Blueprint

staff_bp = Blueprint("staff", __name__)

from app.blueprints.staff import routes  # noqa: F401, E402
