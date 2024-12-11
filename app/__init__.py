from flask import Flask, render_template, current_app, request
import logging
from logging.handlers import RotatingFileHandler
import sys
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

    # Set up logging
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Log to stdout for Railway/Docker
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(stream_handler)
    
    # Set overall logging level
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('TC Inventory startup')

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models to ensure they're known to Flask-Migrate
    from app.models import user, inventory

    # Register blueprints
    from app.routes import auth, inventory, admin, system
    app.register_blueprint(auth.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(system.bp)

    # Register CLI commands
    from app import cli
    cli.init_app(app)

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