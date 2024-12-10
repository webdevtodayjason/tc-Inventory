import os
import sys
from sqlalchemy import create_engine, text

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
                
                # Check if item_tags table exists
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'item_tags'
                    )
                """))
                
                table_exists = result.scalar()
                
                if not table_exists:
                    print("Creating item_tags table...")
                    conn.execute(text("""
                        CREATE TABLE item_tags (
                            item_id INTEGER NOT NULL,
                            tag_id INTEGER NOT NULL,
                            PRIMARY KEY (item_id, tag_id),
                            FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE,
                            FOREIGN KEY (tag_id) REFERENCES tag (id) ON DELETE CASCADE
                        )
                    """))
                    print("Item tags table created successfully!")
                else:
                    print("Item tags table already exists")
                
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