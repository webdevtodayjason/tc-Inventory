import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

# Get the database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:nDwmCtTvZyKpmDvDnlpZoGItQctaVAsq@junction.proxy.rlwy.net:18705/railway')

def increment_build_number():
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            try:
                # Get current build number
                result = conn.execute(text("""
                    SELECT value FROM configuration 
                    WHERE key = 'build_number'
                """))
                current_build = result.scalar()
                
                if not current_build:
                    # Initialize build number if it doesn't exist
                    new_build = '1.0.0'
                    conn.execute(text("""
                        INSERT INTO configuration (key, value, description)
                        VALUES ('build_number', :build, 'Current build number')
                    """), {'build': new_build})
                else:
                    # Increment the last number
                    major, minor, patch = current_build.split('.')
                    new_build = f"{major}.{minor}.{int(patch) + 1}"
                    conn.execute(text("""
                        UPDATE configuration 
                        SET value = :new_build,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE key = 'build_number'
                    """), {'new_build': new_build})
                
                # Commit transaction
                trans.commit()
                print(f"Build number updated to {new_build}")
                
            except Exception as e:
                # Rollback in case of error
                trans.rollback()
                print(f"Error updating build number: {str(e)}")
                raise
                
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        increment_build_number()
    except Exception as e:
        print(f"Script failed: {str(e)}")
        sys.exit(1)
    sys.exit(0) 