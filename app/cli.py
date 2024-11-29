from flask.cli import with_appcontext
import click
from app import db
from app.models import Category, User, ComputerModel, CPU, Tag

def init_app(app):
    app.cli.add_command(create_category_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(add_computer_model_command)
    app.cli.add_command(add_cpu_command)
    app.cli.add_command(create_cpus_command)
    app.cli.add_command(create_tags_command)
    app.cli.add_command(set_user_pin_command)

@click.command('create-category')
@with_appcontext
def create_category_command():
    """Create initial categories"""
    try:
        # First, clear existing categories
        Category.query.delete()
        
        # Create main categories
        main_categories = {
            "Hardware": ["Computer Parts", "Networking Hardware", "Monitors", "Cases", "Power Supply"],
            "Storage": ["HDD-PATA", "HDD-SSD", "HDD-SAS"],
            "Memory": ["RAM-MEMORY"],
            "Cables": ["Cables-Networking", "Cables-Video", "Cables-Power", "Bulk Cat5/Cat6"],
            "Components": ["Network Cards", "Video Cards", "Motherboards", "CPU Coolers"],
            "Networking": ["Network Switches", "Routers", "Access Points", "Patch Panels"],
            "Accessories": ["Server Rails", "Server Caddies", "KVM Switches", "Keyboard/Mouse"],
            "Adapters": ["Adapters-Video", "Adapters-Network", "Adapters-Power"],
            "Systems": ["Computer Systems"]
        }
        
        # Create parent categories first
        for parent_name in main_categories.keys():
            parent = Category(name=parent_name)
            db.session.add(parent)
            db.session.flush()  # This will assign an ID to the parent
            
            # Create child categories
            for child_name in main_categories[parent_name]:
                child = Category(name=child_name, parent_id=parent.id)
                db.session.add(child)
        
        db.session.commit()
        print("Categories created successfully!")
        
        # Print category hierarchy
        parents = Category.query.filter_by(parent_id=None).all()
        for parent in parents:
            print(f"\n{parent.name}")
            for child in parent.children:
                print(f"  └─ {child.name}")
                
    except Exception as e:
        db.session.rollback()
        print(f"Error creating categories: {str(e)}")

@click.command('create-admin')
@click.option('--username', envvar='ADMIN_USERNAME', default='admin')
@click.option('--email', envvar='ADMIN_EMAIL', default='admin@example.com')
@click.option('--password', envvar='ADMIN_PASSWORD', default='admin123')
@click.option('--pin', envvar='ADMIN_PIN', default='123456')
@with_appcontext
def create_admin_command(username, email, password, pin):
    """Create an admin user"""
    try:
        # Check if admin already exists
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.username}")
            return

        # Create new admin user
        user = User(
            username=username,
            email=email,
            role='admin'
        )
        user.set_password(password)
        user.set_pin(pin)
        
        db.session.add(user)
        db.session.commit()
        print(f"Admin user created successfully:")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"PIN: {pin}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")

@click.command('add-computer-model')
@with_appcontext
def add_computer_model_command():
    """Add a new computer model"""
    manufacturer = click.prompt('Enter manufacturer')
    model_name = click.prompt('Enter model name')
    model_type = click.prompt('Enter type (desktop/laptop/server)')
    
    model = ComputerModel(
        manufacturer=manufacturer,
        model_name=model_name,
        model_type=model_type
    )
    
    db.session.add(model)
    db.session.commit()
    print(f"Computer model {manufacturer} {model_name} added successfully!")

@click.command('add-cpu')
@with_appcontext
def add_cpu_command():
    """Add a new CPU"""
    manufacturer = click.prompt('Enter manufacturer (Intel/AMD)')
    model = click.prompt('Enter model')
    speed = click.prompt('Enter speed (e.g., 3.6 GHz)')
    cores = click.prompt('Enter number of cores', type=int)
    
    cpu = CPU(
        manufacturer=manufacturer,
        model=model,
        speed=speed,
        cores=cores
    )
    
    db.session.add(cpu)
    db.session.commit()
    print(f"CPU {manufacturer} {model} added successfully!")

@click.command('create-cpus')
@with_appcontext
def create_cpus_command():
    """Create initial CPU database"""
    try:
        # Intel Core Series
        intel_cores = [
            # 13th Gen
            ("Intel", "Core i9-13900K", "3.0 GHz", 24),
            ("Intel", "Core i7-13700K", "3.4 GHz", 16),
            ("Intel", "Core i5-13600K", "3.5 GHz", 14),
            # 12th Gen
            ("Intel", "Core i9-12900K", "3.2 GHz", 16),
            ("Intel", "Core i7-12700K", "3.6 GHz", 12),
            ("Intel", "Core i5-12600K", "3.7 GHz", 10),
            # 11th Gen
            ("Intel", "Core i9-11900K", "3.5 GHz", 8),
            ("Intel", "Core i7-11700K", "3.6 GHz", 8),
            ("Intel", "Core i5-11600K", "3.9 GHz", 6),
            # 10th Gen
            ("Intel", "Core i9-10900K", "3.7 GHz", 10),
            ("Intel", "Core i7-10700K", "3.8 GHz", 8),
            ("Intel", "Core i5-10600K", "4.1 GHz", 6),
        ]

        # Intel Xeon Series
        intel_xeons = [
            ("Intel", "Xeon W-3175X", "3.1 GHz", 28),
            ("Intel", "Xeon Platinum 8180", "2.5 GHz", 28),
            ("Intel", "Xeon Gold 6258R", "2.7 GHz", 28),
            ("Intel", "Xeon Silver 4314", "2.4 GHz", 16),
            ("Intel", "Xeon E-2388G", "3.2 GHz", 8),
            ("Intel", "Xeon E-2286G", "4.0 GHz", 6),
        ]

        # AMD Ryzen Series
        amd_ryzen = [
            # Ryzen 7000 Series
            ("AMD", "Ryzen 9 7950X", "4.5 GHz", 16),
            ("AMD", "Ryzen 9 7900X", "4.7 GHz", 12),
            ("AMD", "Ryzen 7 7700X", "4.5 GHz", 8),
            ("AMD", "Ryzen 5 7600X", "4.7 GHz", 6),
            # Ryzen 5000 Series
            ("AMD", "Ryzen 9 5950X", "3.4 GHz", 16),
            ("AMD", "Ryzen 9 5900X", "3.7 GHz", 12),
            ("AMD", "Ryzen 7 5800X", "3.8 GHz", 8),
            ("AMD", "Ryzen 5 5600X", "3.7 GHz", 6),
        ]

        # AMD EPYC Server
        amd_epyc = [
            ("AMD", "EPYC 7763", "2.45 GHz", 64),
            ("AMD", "EPYC 7742", "2.25 GHz", 64),
            ("AMD", "EPYC 7543", "2.8 GHz", 32),
            ("AMD", "EPYC 7443", "2.85 GHz", 24),
        ]

        # Combine all CPUs
        all_cpus = intel_cores + intel_xeons + amd_ryzen + amd_epyc

        # Clear existing CPUs
        CPU.query.delete()

        # Add all CPUs to database
        for manufacturer, model, speed, cores in all_cpus:
            cpu = CPU(
                manufacturer=manufacturer,
                model=model,
                speed=speed,
                cores=cores
            )
            db.session.add(cpu)

        db.session.commit()
        print("CPUs created successfully!")
        
        # Print summary
        print("\nCPUs in database:")
        print("Intel Core Series:", len(intel_cores))
        print("Intel Xeon Series:", len(intel_xeons))
        print("AMD Ryzen Series:", len(amd_ryzen))
        print("AMD EPYC Series:", len(amd_epyc))
        print("Total CPUs:", len(all_cpus))

    except Exception as e:
        db.session.rollback()
        print(f"Error creating CPUs: {str(e)}")

@click.command('create-tags')
@with_appcontext
def create_tags_command():
    """Create initial tags"""
    try:
        # Default tags
        default_tags = [
            'NO TOUCH',
            'JUMP BOX',
            'DESKTOP',
            'INTERNAL',
            'FOR SALE',
            'DO NOT SELL'
        ]
        
        # Add tags
        for tag_name in default_tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
        
        db.session.commit()
        print("Default tags created successfully!")
        
        # Print summary
        tags = Tag.query.all()
        print("\nAvailable tags:")
        for tag in tags:
            print(f"- {tag.name}")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error creating tags: {str(e)}")

@click.command('set-user-pin')
@click.argument('username')
@with_appcontext
def set_user_pin_command(username):
    """Set PIN code for a user"""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User {username} not found")
            return
        
        pin = input("Enter 6-digit PIN: ")
        try:
            user.set_pin(pin)
            db.session.commit()
            print(f"PIN set successfully for user {username}")
        except ValueError as e:
            print(f"Error: {str(e)}")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error setting PIN: {str(e)}") 