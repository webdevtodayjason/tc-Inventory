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
                
                # 1. Create new computer_systems table
                print("Creating new computer_systems table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS computer_systems (
                        id SERIAL PRIMARY KEY,
                        tracking_id VARCHAR(50) UNIQUE,
                        serial_tag VARCHAR(100),
                        model_id INTEGER REFERENCES computer_model(id),
                        cpu_id INTEGER REFERENCES cpu(id),
                        ram VARCHAR(64),
                        storage VARCHAR(128),
                        os VARCHAR(50),
                        storage_location VARCHAR(100),
                        status VARCHAR(50) DEFAULT 'available',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        creator_id INTEGER REFERENCES users(id),
                        cpu_benchmark FLOAT,
                        usb_ports_status VARCHAR(20),
                        usb_ports_notes TEXT,
                        video_status VARCHAR(20),
                        video_notes TEXT,
                        network_status VARCHAR(20),
                        network_notes TEXT,
                        general_notes TEXT,
                        tested_by INTEGER REFERENCES users(id)
                    )
                """))
                
                # 2. Migrate data from items table
                print("Migrating data from items table...")
                conn.execute(text("""
                    INSERT INTO computer_systems (
                        tracking_id, storage_location, status, created_at, 
                        updated_at, creator_id
                    )
                    SELECT 
                        i.tracking_id, i.storage_location, i.status, i.created_at,
                        i.updated_at, i.creator_id
                    FROM items i
                    JOIN category c ON i.category_id = c.id
                    WHERE c.name = 'Computer System'
                    ON CONFLICT (tracking_id) DO NOTHING
                """))
                
                # 3. Remove computer systems from items table
                print("Removing computer systems from items table...")
                conn.execute(text("""
                    DELETE FROM items i
                    USING category c
                    WHERE i.category_id = c.id
                    AND c.name = 'Computer System'
                """))
                
                print("Database update completed successfully!")
                
                # Commit transaction
                trans.commit()
                
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