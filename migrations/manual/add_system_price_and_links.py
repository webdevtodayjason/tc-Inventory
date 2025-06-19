#!/usr/bin/env python3
"""
Manual migration script to add price and purchase links to computer systems.
This script can be run safely on the production database.

To run:
    python migrations/manual/add_system_price_and_links.py

This will:
1. Add sell_price column to computer_systems table
2. Create system_purchase_links table
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app, db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def check_if_column_exists(table_name, column_name):
    """Check if a column already exists in a table."""
    query = text("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name = :table_name 
        AND column_name = :column_name
    """)
    result = db.session.execute(query, {
        'table_name': table_name,
        'column_name': column_name
    })
    return result.scalar() > 0

def check_if_table_exists(table_name):
    """Check if a table already exists."""
    query = text("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_name = :table_name
    """)
    result = db.session.execute(query, {'table_name': table_name})
    return result.scalar() > 0

def run_migration():
    """Run the migration to add price and purchase links to computer systems."""
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Add price and purchase links to computer systems")
        print("=" * 60)
        
        try:
            # Step 1: Add sell_price column to computer_systems table
            if not check_if_column_exists('computer_systems', 'sell_price'):
                print("Adding sell_price column to computer_systems table...")
                db.session.execute(text("""
                    ALTER TABLE computer_systems 
                    ADD COLUMN sell_price NUMERIC(10, 2)
                """))
                db.session.commit()
                print("✓ Successfully added sell_price column")
            else:
                print("⚠ sell_price column already exists, skipping...")
            
            # Step 2: Create system_purchase_links table
            if not check_if_table_exists('system_purchase_links'):
                print("\nCreating system_purchase_links table...")
                db.session.execute(text("""
                    CREATE TABLE system_purchase_links (
                        id SERIAL PRIMARY KEY,
                        system_id INTEGER NOT NULL,
                        url VARCHAR(500) NOT NULL,
                        title VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER,
                        FOREIGN KEY (system_id) REFERENCES computer_systems(id) ON DELETE CASCADE,
                        FOREIGN KEY (created_by) REFERENCES users(id)
                    )
                """))
                
                # Create indexes for better performance
                print("Creating indexes...")
                db.session.execute(text("""
                    CREATE INDEX idx_system_purchase_links_system_id 
                    ON system_purchase_links(system_id)
                """))
                
                db.session.commit()
                print("✓ Successfully created system_purchase_links table and indexes")
            else:
                print("⚠ system_purchase_links table already exists, skipping...")
            
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Test the new functionality locally")
            print("2. Deploy the updated code")
            print("3. The new fields will be available in the application")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"\n❌ Error during migration: {str(e)}")
            print("The migration has been rolled back. No changes were made.")
            return False
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Unexpected error: {str(e)}")
            print("The migration has been rolled back. No changes were made.")
            return False
    
    return True

if __name__ == "__main__":
    # Safety check
    print("This script will modify the database schema.")
    print("Database URL:", os.environ.get('DATABASE_URL', 'Not set')[:50] + '...')
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)
    
    if run_migration():
        sys.exit(0)
    else:
        sys.exit(1)