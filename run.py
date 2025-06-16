from flask import Flask
from app import create_app, db
from app.models.inventory import Category, CPU, Tag
from app.models.user import User
from app.models.config import Configuration
import click
import os
import time
from sqlalchemy import text

app = create_app()

def wait_for_db(max_attempts=5, wait_time=5):
    """Wait for database to be available."""
    for attempt in range(max_attempts):
        try:
            # Try internal URL first
            with app.app_context():
                try:
                    db.session.execute(text('SELECT 1'))
                    db.session.commit()
                    print("Database connection successful using internal URL!")
                    return True
                except Exception as internal_error:
                    print(f"Internal connection failed: {internal_error}")
                    
                    # Try public URL as fallback
                    if 'DATABASE_PUBLIC_URL' in os.environ:
                        print("Trying public URL...")
                        # Temporarily override the SQLAlchemy URL
                        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_PUBLIC_URL']
                        db.session.execute(text('SELECT 1'))
                        db.session.commit()
                        print("Database connection successful using public URL!")
                        return True
                    raise
        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
    return False

@app.cli.command("verify-db")
def verify_db():
    """Verify database connection."""
    if wait_for_db():
        print("Database verification successful!")
    else:
        print("Database verification failed!")
        exit(1)

@app.cli.command("create-category")
def create_category():
    """Create initial categories."""
    try:
        if not wait_for_db():
            print("Could not connect to database!")
            return

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

@app.cli.command("create-admin")
def create_admin():
    """Create the admin user."""
    try:
        if not wait_for_db():
            print("Could not connect to database!")
            return

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

@app.cli.command("init-config")
def init_config():
    """Initialize configuration settings with defaults from environment variables."""
    try:
        if not wait_for_db():
            print("Could not connect to database!")
            return

        # Only set configuration if it doesn't exist
        def init_setting(key, env_key, description, default=None):
            if not Configuration.get_value(key):
                value = os.environ.get(env_key)
                if value is None:
                    value = default
                if value is not None:
                    Configuration.set_value(key, str(value).lower(), description)

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
        raise  # Re-raise the exception to see the full traceback

if __name__ == '__main__':
    app.run() 