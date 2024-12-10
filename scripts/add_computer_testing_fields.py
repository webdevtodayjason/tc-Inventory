import os
import sys

# Set required environment variables
os.environ['DATABASE_URL'] = 'postgresql://postgres:nDwmCtTvZyKpmDvDnlpZoGItQctaVAsq@junction.proxy.rlwy.net:18705/railway'
os.environ['FLASK_APP'] = 'run.py'
os.environ['SECRET_KEY'] = '0a29fe553a88c890fc2e0aa60fe675992886159ec76914bc2a66c1e22ede13aa'

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import create_app, db
from sqlalchemy import text

def add_computer_testing_fields():
    app = create_app()
    with app.app_context():
        try:
            # Check if columns already exist
            with db.engine.connect() as conn:
                # Get existing columns
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'computer_system'
                """))
                existing_columns = [row[0] for row in result]
                
                # Define the columns to add
                columns = {
                    'cpu_benchmark': 'FLOAT',
                    'usb_ports_status': 'VARCHAR(20)',
                    'usb_ports_notes': 'TEXT',
                    'video_status': 'VARCHAR(20)',
                    'video_notes': 'TEXT',
                    'network_status': 'VARCHAR(20)',
                    'network_notes': 'TEXT',
                    'general_notes': 'TEXT',
                    'tested_by': 'INTEGER REFERENCES users(id)'
                }
                
                # Add each column if it doesn't exist
                for column_name, column_type in columns.items():
                    if column_name not in existing_columns:
                        print(f"Adding column {column_name}...")
                        conn.execute(text(f"""
                            ALTER TABLE computer_system 
                            ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                        """))
                        print(f"Added {column_name} column successfully")
                    else:
                        print(f"Column {column_name} already exists")
                
                conn.commit()
                print("\nAll computer testing fields added successfully!")
                
        except Exception as e:
            print(f"Error adding computer testing fields: {str(e)}")
            raise

if __name__ == '__main__':
    add_computer_testing_fields()
    print("\nScript completed!") 