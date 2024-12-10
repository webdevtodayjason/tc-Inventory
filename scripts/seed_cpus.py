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
from app.models.inventory import CPU

def seed_cpus():
    app = create_app()
    with app.app_context():
        try:
            # Define CPU data
            cpus = [
                # Intel Core i3
                {'manufacturer': 'Intel', 'model': 'Core i3-12100', 'speed': '3.3 GHz', 'cores': 4},
                {'manufacturer': 'Intel', 'model': 'Core i3-13100', 'speed': '3.4 GHz', 'cores': 4},
                {'manufacturer': 'Intel', 'model': 'Core i3-10100', 'speed': '3.6 GHz', 'cores': 4},
                
                # Intel Core i5
                {'manufacturer': 'Intel', 'model': 'Core i5-12600K', 'speed': '3.7 GHz', 'cores': 10},
                {'manufacturer': 'Intel', 'model': 'Core i5-13600K', 'speed': '3.5 GHz', 'cores': 14},
                {'manufacturer': 'Intel', 'model': 'Core i5-11600K', 'speed': '3.9 GHz', 'cores': 6},
                {'manufacturer': 'Intel', 'model': 'Core i5-10600K', 'speed': '4.1 GHz', 'cores': 6},
                
                # Intel Core i7
                {'manufacturer': 'Intel', 'model': 'Core i7-12700K', 'speed': '3.6 GHz', 'cores': 12},
                {'manufacturer': 'Intel', 'model': 'Core i7-13700K', 'speed': '3.4 GHz', 'cores': 16},
                {'manufacturer': 'Intel', 'model': 'Core i7-11700K', 'speed': '3.6 GHz', 'cores': 8},
                {'manufacturer': 'Intel', 'model': 'Core i7-10700K', 'speed': '3.8 GHz', 'cores': 8},
                
                # Intel Core i9
                {'manufacturer': 'Intel', 'model': 'Core i9-12900K', 'speed': '3.2 GHz', 'cores': 16},
                {'manufacturer': 'Intel', 'model': 'Core i9-13900K', 'speed': '3.0 GHz', 'cores': 24},
                {'manufacturer': 'Intel', 'model': 'Core i9-11900K', 'speed': '3.5 GHz', 'cores': 8},
                {'manufacturer': 'Intel', 'model': 'Core i9-10900K', 'speed': '3.7 GHz', 'cores': 10},
                
                # Intel Xeon
                {'manufacturer': 'Intel', 'model': 'Xeon E-2378G', 'speed': '2.8 GHz', 'cores': 8},
                {'manufacturer': 'Intel', 'model': 'Xeon W-3175X', 'speed': '3.1 GHz', 'cores': 28},
                {'manufacturer': 'Intel', 'model': 'Xeon Gold 6338', 'speed': '2.0 GHz', 'cores': 32},
                {'manufacturer': 'Intel', 'model': 'Xeon Platinum 8380', 'speed': '2.3 GHz', 'cores': 40},
                
                # AMD Ryzen 3
                {'manufacturer': 'AMD', 'model': 'Ryzen 3 5300G', 'speed': '4.0 GHz', 'cores': 4},
                {'manufacturer': 'AMD', 'model': 'Ryzen 3 4100', 'speed': '3.8 GHz', 'cores': 4},
                {'manufacturer': 'AMD', 'model': 'Ryzen 3 3300X', 'speed': '3.8 GHz', 'cores': 4},
                
                # AMD Ryzen 5
                {'manufacturer': 'AMD', 'model': 'Ryzen 5 7600X', 'speed': '4.7 GHz', 'cores': 6},
                {'manufacturer': 'AMD', 'model': 'Ryzen 5 5600X', 'speed': '3.7 GHz', 'cores': 6},
                {'manufacturer': 'AMD', 'model': 'Ryzen 5 5600G', 'speed': '3.9 GHz', 'cores': 6},
                
                # AMD Ryzen 7
                {'manufacturer': 'AMD', 'model': 'Ryzen 7 7700X', 'speed': '4.5 GHz', 'cores': 8},
                {'manufacturer': 'AMD', 'model': 'Ryzen 7 5800X', 'speed': '3.8 GHz', 'cores': 8},
                {'manufacturer': 'AMD', 'model': 'Ryzen 7 5700G', 'speed': '3.8 GHz', 'cores': 8},
                
                # AMD Ryzen 9
                {'manufacturer': 'AMD', 'model': 'Ryzen 9 7950X', 'speed': '4.5 GHz', 'cores': 16},
                {'manufacturer': 'AMD', 'model': 'Ryzen 9 5950X', 'speed': '3.4 GHz', 'cores': 16},
                {'manufacturer': 'AMD', 'model': 'Ryzen 9 5900X', 'speed': '3.7 GHz', 'cores': 12},
                
                # AMD EPYC (Server)
                {'manufacturer': 'AMD', 'model': 'EPYC 7763', 'speed': '2.45 GHz', 'cores': 64},
                {'manufacturer': 'AMD', 'model': 'EPYC 7662', 'speed': '2.0 GHz', 'cores': 64},
                {'manufacturer': 'AMD', 'model': 'EPYC 7542', 'speed': '2.9 GHz', 'cores': 32}
            ]
            
            # First, get existing CPUs to avoid duplicates
            existing_cpus = {(cpu.manufacturer, cpu.model) for cpu in CPU.query.all()}
            
            # Add new CPUs
            for cpu_data in cpus:
                if (cpu_data['manufacturer'], cpu_data['model']) not in existing_cpus:
                    cpu = CPU(**cpu_data)
                    db.session.add(cpu)
                    print(f"Adding {cpu_data['manufacturer']} {cpu_data['model']}")
                else:
                    print(f"Skipping existing CPU: {cpu_data['manufacturer']} {cpu_data['model']}")
            
            db.session.commit()
            print("\nCPU seeding completed successfully!")
            
            # Print all CPUs for verification
            print("\nCurrent CPU List:")
            all_cpus = CPU.query.order_by(CPU.manufacturer, CPU.model).all()
            for cpu in all_cpus:
                print(f"{cpu.manufacturer} {cpu.model} ({cpu.speed}, {cpu.cores} cores)")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding CPUs: {str(e)}")
            raise

if __name__ == '__main__':
    seed_cpus()
    print("\nScript completed!") 