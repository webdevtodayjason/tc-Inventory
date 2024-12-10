import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

# Database configuration
DATABASE_URL = 'postgresql://postgres:nDwmCtTvZyKpmDvDnlpZoGItQctaVAsq@junction.proxy.rlwy.net:18705/railway'

def update_database():
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            try:
                print("Starting database update...")
                
                # Check if serial_tag column exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'computer_systems' 
                    AND column_name = 'serial_tag'
                """))
                
                if not result.fetchone():
                    print("Adding serial_tag column...")
                    conn.execute(text("""
                        ALTER TABLE computer_systems
                        ADD COLUMN serial_tag VARCHAR(100)
                    """))
                    print("Serial tag column added successfully!")
                else:
                    print("Serial tag column already exists")
                
                # Commit transaction
                trans.commit()
                print("Database update completed successfully!")
                
            except Exception as e:
                # Rollback in case of error
                trans.rollback()
                print(f"Error during update: {str(e)}")
                raise
                
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        update_database()
    except Exception as e:
        print(f"Script failed: {str(e)}")
        sys.exit(1)
    sys.exit(0) 