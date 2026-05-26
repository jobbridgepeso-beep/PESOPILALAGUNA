"""Employer blueprint — /api/employer"""

from flask import Blueprint

employer_bp = Blueprint("employer", __name__)

from app.blueprints.employer import routes  # noqa: F401, E402
from app.blueprints.employer import routes_extra  # noqa: F401, E402
