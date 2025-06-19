#!/usr/bin/env python3
"""
Rollback script for the system price and purchase links migration.

To run:
    python migrations/manual/rollback_system_price_and_links.py

This will:
1. Remove sell_price column from computer_systems table
2. Drop system_purchase_links table
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app, db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def run_rollback():
    """Rollback the price and purchase links migration."""
    app = create_app()
    
    with app.app_context():
        print("Starting rollback: Remove price and purchase links from computer systems")
        print("=" * 60)
        print("⚠️  WARNING: This will remove data! Make sure to backup first.")
        print("=" * 60)
        
        try:
            # Step 1: Drop system_purchase_links table
            print("Dropping system_purchase_links table...")
            db.session.execute(text("DROP TABLE IF EXISTS system_purchase_links CASCADE"))
            print("✓ Successfully dropped system_purchase_links table")
            
            # Step 2: Remove sell_price column from computer_systems table
            print("\nRemoving sell_price column from computer_systems table...")
            db.session.execute(text("""
                ALTER TABLE computer_systems 
                DROP COLUMN IF EXISTS sell_price
            """))
            print("✓ Successfully removed sell_price column")
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ Rollback completed successfully!")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"\n❌ Error during rollback: {str(e)}")
            print("The rollback has been cancelled. No changes were made.")
            return False
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Unexpected error: {str(e)}")
            print("The rollback has been cancelled. No changes were made.")
            return False
    
    return True

if __name__ == "__main__":
    # Safety check
    print("This script will REMOVE the sell_price column and system_purchase_links table!")
    print("Database URL:", os.environ.get('DATABASE_URL', 'Not set')[:50] + '...')
    
    response = input("\nAre you sure you want to rollback? (yes/no): ")
    if response.lower() != 'yes':
        print("Rollback cancelled.")
        sys.exit(0)
    
    if run_rollback():
        sys.exit(0)
    else:
        sys.exit(1)