from app.models.config import Configuration
from app import db

def increment_build_number():
    """Increment the build number in the configuration table"""
    try:
        # Get current build number
        current_build = Configuration.get_setting('build_number', '1.0.0')
        
        # Increment the last number
        major, minor, patch = current_build.split('.')
        new_build = f"{major}.{minor}.{int(patch) + 1}"
        
        # Update the configuration
        config = Configuration.query.filter_by(key='build_number').first()
        if config:
            config.value = new_build
        else:
            config = Configuration(
                key='build_number',
                value=new_build,
                description='Current build number of the application'
            )
            db.session.add(config)
            
        db.session.commit()
        return new_build
        
    except Exception as e:
        db.session.rollback()
        print(f"Error incrementing build number: {str(e)}")
        return None 