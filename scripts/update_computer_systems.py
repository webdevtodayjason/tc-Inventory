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
                
                # 1. Create new computer_systems table if it doesn't exist
                print("Creating new computer_systems table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS computer_systems (
                        id SERIAL PRIMARY KEY,
                        tracking_id VARCHAR(50) UNIQUE,
                        model_id INTEGER REFERENCES computer_model(id) NOT NULL,
                        cpu_id INTEGER REFERENCES cpu(id) NOT NULL,
                        ram VARCHAR(64) NOT NULL,
                        storage VARCHAR(128) NOT NULL,
                        os VARCHAR(50) NOT NULL,
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
                
                # 2. Migrate existing computer systems from items table
                print("Migrating existing computer systems...")
                conn.execute(text("""
                    INSERT INTO computer_systems (
                        tracking_id, model_id, cpu_id, ram, storage, os,
                        storage_location, status, created_at, updated_at,
                        creator_id, cpu_benchmark, usb_ports_status,
                        usb_ports_notes, video_status, video_notes,
                        network_status, network_notes, general_notes, tested_by
                    )
                    SELECT 
                        i.tracking_id, cs.model_id, cs.cpu_id, cs.ram,
                        cs.storage, cs.os, i.storage_location, i.status,
                        i.created_at, i.updated_at, i.creator_id,
                        cs.cpu_benchmark, cs.usb_ports_status,
                        cs.usb_ports_notes, cs.video_status, cs.video_notes,
                        cs.network_status, cs.network_notes,
                        cs.general_notes, cs.tested_by
                    FROM items i
                    JOIN computer_system cs ON cs.id = i.id
                    ON CONFLICT (tracking_id) DO NOTHING
                """))
                
                # 3. Delete migrated computer systems from items table
                print("Removing migrated systems from items table...")
                conn.execute(text("""
                    DELETE FROM items i
                    WHERE EXISTS (
                        SELECT 1 FROM computer_system cs
                        WHERE cs.id = i.id
                    )
                """))
                
                # 4. Drop old computer_system table
                print("Dropping old computer_system table...")
                conn.execute(text("""
                    DROP TABLE IF EXISTS computer_system CASCADE
                """))
                
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