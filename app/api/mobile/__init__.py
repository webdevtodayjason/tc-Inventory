"""Mobile API Blueprint"""
from flask import Blueprint
from flask_wtf.csrf import CSRFProtect

# Create Blueprint
bp = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

# Create a CSRF protect instance that will be used to exempt mobile API routes
csrf = CSRFProtect()

# Import swagger configuration first
from app.api.mobile.swagger import api

# Initialize API with blueprint
api.init_app(bp)

# Import routes after blueprint creation to avoid circular imports
from app.api.mobile import auth, items, search, checkout

# Export all for easier imports
__all__ = ['bp', 'csrf', 'api'] 