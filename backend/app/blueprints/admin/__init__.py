"""Admin blueprint — /api/admin"""

from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

from app.blueprints.admin import routes  # noqa: F401, E402
from app.blueprints.admin import routes_extra  # noqa: F401, E402
