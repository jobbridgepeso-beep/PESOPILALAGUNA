"""Jobseeker blueprint — /api/jobseeker"""

from flask import Blueprint

jobseeker_bp = Blueprint("jobseeker", __name__)

from app.blueprints.jobseeker import routes  # noqa: F401, E402
from app.blueprints.jobseeker import routes_extra  # noqa: F401, E402
