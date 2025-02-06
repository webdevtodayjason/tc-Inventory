"""Application configuration"""
import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres@localhost/inventory_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API config
    API_TITLE = 'TC Inventory API'
    API_VERSION = '1.0'
    API_DESCRIPTION = 'API for TC Inventory System'
    
    # Development server
    DEV_SERVER_HOST = '127.0.0.1'
    DEV_SERVER_PORT = 5001
    
    # Base URLs for different environments
    LOCAL_URL = f'http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}'
    STAGING_URL = 'https://tc-inventory-staging.up.railway.app'
    PRODUCTION_URL = 'https://inventory.ticom.pro'
    
    # Default to local development
    BASE_URL = LOCAL_URL
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5001',
        'http://127.0.0.1:5001',
    ]
    
    # Timezone
    TIMEZONE = 'America/Chicago' 