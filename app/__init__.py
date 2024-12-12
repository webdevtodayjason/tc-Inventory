from flask import Flask, render_template, current_app, request
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up logging
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S %p'
    )
    
    # Log to file
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Log to stdout for Railway/Docker
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    
    # Set handlers and level
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.DEBUG)
    
    # Initial log message
    app.logger.info('TC Inventory startup')

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models to ensure they're known to Flask-Migrate
    from app.models import user, inventory, config

    # Register blueprints
    from app.routes import auth, inventory, admin, wiki
    app.register_blueprint(auth.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(wiki.bp)

    # Register CLI commands
    from app import cli
    cli.init_app(app)

    # Add template context processor
    @app.context_processor
    def utility_processor():
        from app.models.config import Configuration
        return dict(Configuration=Configuration)

    # Register the root route directly in the app
    @app.route('/')
    def index():
        app.logger.debug('Accessing index route')
        try:
            return render_template('index.html')
        except Exception as e:
            app.logger.error(f'Error rendering index template: {str(e)}')
            raise

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.error(f'403 error: {error}')
        return render_template('errors/403.html'), 403

    @app.before_request
    def log_request_info():
        app.logger.debug('Headers: %s', request.headers)
        app.logger.debug('Body: %s', request.get_data())

    return app 