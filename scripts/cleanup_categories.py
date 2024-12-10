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
from app.models.inventory import Category, InventoryItem
from datetime import datetime

def cleanup_and_seed_categories():
    app = create_app()
    with app.app_context():
        print("Cleaning up existing categories...")
        
        # First, update any items to use a temporary category ID
        InventoryItem.query.update({InventoryItem.category_id: None})
        
        # Delete all existing categories
        Category.query.delete()
        db.session.commit()
        
        print("Creating new category structure...")
        
        # Define the category structure
        categories = {
            "Computer Systems": [
                "Desktop Computers",
                "Laptop Computers",
                "Servers",
                "Workstations",
                "Mini PCs",
            ],
            "Computer Components": [
                "CPUs",
                "Motherboards",
                "Memory (RAM)",
                "Storage Drives",
                "Power Supplies",
                "Graphics Cards",
                "Cases",
                "Cooling Systems",
            ],
            "Networking Equipment": [
                "Routers",
                "Switches",
                "Access Points",
                "Network Cards",
                "Cables & Connectors",
                "Patch Panels",
                "Firewalls",
            ],
            "Peripherals": [
                "Monitors",
                "Keyboards",
                "Mice & Pointing Devices",
                "Printers & Scanners",
                "Audio Equipment",
                "Webcams",
            ],
            "Testing Equipment": [
                "Network Testers",
                "Power Supply Testers",
                "Memory Testers",
                "Cable Testers",
                "Diagnostic Tools",
            ],
            "Spare Parts": [
                "Display Parts",
                "Keyboard Parts",
                "Battery Replacements",
                "Power Adapters",
                "Cables & Adapters",
            ],
            "Tools": [
                "Hand Tools",
                "Power Tools",
                "Cleaning Supplies",
                "Anti-Static Equipment",
                "Tool Kits",
            ],
            "Software & Licenses": [
                "Operating Systems",
                "Office Software",
                "Antivirus & Security",
                "Backup Solutions",
                "Diagnostic Software",
            ]
        }
        
        # Create categories
        created_categories = {}
        for main_category, subcategories in categories.items():
            print(f"Creating main category: {main_category}")
            parent = Category(name=main_category)
            db.session.add(parent)
            db.session.flush()  # Get the ID
            created_categories[main_category] = parent
            
            for subcategory in subcategories:
                print(f"  - Creating subcategory: {subcategory}")
                child = Category(name=subcategory, parent_id=parent.id)
                db.session.add(child)
        
        try:
            db.session.commit()
            print("\nCategory structure created successfully!")
            
            # Print the final structure
            print("\nFinal Category Structure:")
            main_categories = Category.query.filter_by(parent_id=None).order_by(Category.name).all()
            for main in main_categories:
                print(f"\n{main.name} (ID: {main.id})")
                subcategories = Category.query.filter_by(parent_id=main.id).order_by(Category.name).all()
                for sub in subcategories:
                    print(f"  - {sub.name} (ID: {sub.id})")
                    
        except Exception as e:
            db.session.rollback()
            print(f"Error creating categories: {str(e)}")

if __name__ == '__main__':
    cleanup_and_seed_categories()
    print("\nScript completed!") 