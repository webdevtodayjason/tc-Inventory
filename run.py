from flask.cli import FlaskGroup
from app import create_app, db
from app.models.inventory import Category, CPU, Tag
from app.models.user import User
from app.models.config import Configuration
import click
import os

app = create_app()
cli = FlaskGroup(app)

@cli.command("create-category")
def create_category():
    """Create initial categories."""
    try:
        categories = ["Desktop", "Laptop", "Server", "Network", "Peripheral", "Component", "Software", "Other"]
        for cat_name in categories:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                category = Category(name=cat_name)
                db.session.add(category)
        db.session.commit()
        print("Categories created successfully!")
    except Exception as e:
        print(f"Error creating categories: {e}")

@cli.command("create-admin")
def create_admin():
    """Create the admin user."""
    try:
        admin = User.query.filter_by(username=os.environ.get('ADMIN_USERNAME')).first()
        if not admin:
            admin = User(
                username=os.environ.get('ADMIN_USERNAME'),
                email=os.environ.get('ADMIN_EMAIL'),
                role='admin'
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD'))
            admin.set_pin(os.environ.get('ADMIN_PIN'))
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
    except Exception as e:
        print(f"Error creating admin user: {e}")

@cli.command("init-config")
def init_config():
    """Initialize configuration settings with defaults from environment variables."""
    try:
        # Only set configuration if it doesn't exist
        def init_setting(key, env_key, description, default=None):
            if not Configuration.get_setting(key):
                value = os.environ.get(env_key, default)
                if value is not None:
                    Configuration.set_setting(key, str(value).lower(), description)

        # Admin Settings
        init_setting(
            'admin_username',
            'ADMIN_USERNAME',
            'Administrator username',
            'admin'
        )

        # User Management Settings
        init_setting(
            'allow_public_registration',
            'DEFAULT_ALLOW_REGISTRATION',
            'Allow public user registration',
            'false'
        )
        init_setting(
            'require_email_verification',
            'DEFAULT_REQUIRE_EMAIL_VERIFICATION',
            'Require email verification for new users',
            'false'
        )
        init_setting(
            'allow_password_reset',
            'DEFAULT_ALLOW_PASSWORD_RESET',
            'Allow users to reset passwords via email',
            'true'
        )
        
        # Inventory Settings
        init_setting(
            'items_per_page',
            'DEFAULT_ITEMS_PER_PAGE',
            'Number of items to display per page',
            '20'
        )
        init_setting(
            'enable_barcode_scanner',
            None,  # No env var, just set default
            'Enable barcode scanning functionality',
            'true'
        )
        init_setting(
            'enable_low_stock_alerts',
            None,  # No env var, just set default
            'Enable low stock alerts',
            'true'
        )
        
        db.session.commit()
        print("Configuration settings initialized successfully!")
    except Exception as e:
        print(f"Error initializing configuration settings: {e}")

if __name__ == "__main__":
    cli() 