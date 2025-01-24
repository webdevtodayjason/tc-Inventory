"""Mobile API Blueprint"""
from flask import Blueprint
from flask_wtf.csrf import CSRFProtect

# Create blueprint with url_prefix
bp = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

# Create a CSRF protect instance that will be used to exempt mobile API routes
csrf = CSRFProtect()

# Import swagger first to initialize the API
from app.api.mobile import swagger

# Import routes after swagger initialization
from app.api.mobile import auth, items, checkout

# Export all for easier imports
__all__ = ['bp', 'csrf', 'swagger', 'auth', 'items', 'checkout'] 