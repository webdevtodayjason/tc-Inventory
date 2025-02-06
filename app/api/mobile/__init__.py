"""Mobile API Blueprint"""
from flask import Blueprint, redirect, url_for
from flask_wtf.csrf import CSRFProtect

# Create Blueprint
bp = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

# Create a CSRF protect instance that will be used to exempt mobile API routes
csrf = CSRFProtect()

# Import swagger configuration first
from app.api.mobile.swagger import api, ns_auth, ns_items, ns_search, ns_checkout, ns_systems

# Initialize API with blueprint
api.init_app(bp)

# Add namespaces to API
api.add_namespace(ns_auth)
api.add_namespace(ns_items)
api.add_namespace(ns_systems)
api.add_namespace(ns_search)
api.add_namespace(ns_checkout)

# Root route redirects to API documentation
@bp.route('/')
def index():
    """Redirect root to API documentation"""
    return redirect(url_for('mobile_api.swagger'))

# Import routes after blueprint creation to avoid circular imports
from app.api.mobile import auth, items, search, checkout

# Export all for easier imports
__all__ = ['bp', 'csrf', 'api'] 