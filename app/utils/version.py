from app.models.config import Configuration
from app import db

def increment_build_number():
    """Increment the build number in the configuration table"""
    try:
        # Get or create the build number configuration
        config = Configuration.query.filter_by(key='build_number').first()
        if not config:
            config = Configuration(
                key='build_number',
                value='1.0.0',
                description='Current build number of the application'
            )
            db.session.add(config)
            db.session.commit()
        
        # Parse current version
        try:
            major, minor, patch = config.value.split('.')
            new_build = f"{major}.{minor}.{int(patch) + 1}"
        except (ValueError, AttributeError):
            # If version is invalid, reset to 1.0.0
            new_build = '1.0.0'
        
        # Update the configuration
        config.value = new_build
        db.session.commit()
        print(f"Successfully incremented version to {new_build}")
        return new_build
        
    except Exception as e:
        db.session.rollback()
        print(f"Error incrementing build number: {str(e)}")
        return None 