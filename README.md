# TC Inventory System

A comprehensive inventory management system built with Flask, designed for tracking general inventory items and computer systems.

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3118/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Core Functionality
- Track both general inventory items and computer systems
- Barcode scanning support with UPCItemDB integration
- Dark/Light mode support
- Location-based inventory tracking
- Reorder threshold monitoring
- Multi-user support with role-based access control (Admin/User)
- Quick checkout system with PIN code access

### Item Management
- Add, edit, view, and delete inventory items
- Barcode scanning for quick item addition
- Storage location tracking
- Automatic restock alerts
- Custom tagging system
- Printable 4x2 labels with barcodes
- Bulk item management
- Purchase URL tracking

### Computer Systems
- Detailed computer specifications tracking
- CPU and model management
- Testing results tracking
- Component tracking (RAM, Storage, OS)
- Performance benchmarks

### User Management (Admin Only)
- User creation and management
- Role assignment (Admin/User)
- PIN code management for quick access
- Email and password management

### Search and Filter
- Advanced search functionality
- Multiple filter options:
  - Category
  - Type
  - Status
  - Location
- Sortable columns
- Tag-based filtering

### Interface Features
- Responsive design
- Dark/Light mode toggle
- Icon-based actions
- Status indicators
- Tag color coding
- Pagination
- Mobile-friendly interface

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd tcinvintory
```

2. Create and activate a Conda environment:

```bash
conda create -n inventory python=3.11
conda activate inventory
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up the PostgreSQL database:

```bash
createdb inventory_db
createuser inventory_admin
```

5. Configure environment variables in `.env`:

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://inventory_admin:your_password@localhost:5432/inventory_db
DEBUG=True
ITEMS_PER_PAGE=20
PORT=5001
```

6. Initialize the database:

```bash
flask db upgrade
```

## Usage

1. Start the application:

```bash
flask run -p 5001
```

2. Access the application at `http://127.0.0.1:5001`

3. Create an admin user:

```sql
UPDATE "user" SET role = 'admin' WHERE username = 'your_username';
```

## Key Components

### Models
- InventoryItem: Base model for all inventory items
- ComputerSystem: Extended model for computer systems
- Category: Item categorization
- Tag: Item tagging system
- User: User management with role-based access

### Features
- Barcode scanning for quick item addition
- Location-based inventory tracking
- Automatic restock alerts
- PIN-based quick checkout system
- Role-based access control
- Dark/Light mode theme switching
- 4x2 label printing with barcodes

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Author

**WebDevTodayJason** - [GitHub Profile](https://github.com/webdevtodayjason)

## Repository

- **Repository URL:** [https://github.com/webdevtodayjason/tc-Inventory](https://github.com/webdevtodayjason/tc-Inventory)
- **Clone URL:** [https://github.com/webdevtodayjason/tc-Inventory.git](https://github.com/webdevtodayjason/tc-Inventory.git)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Made with ❤️ by [WebDevTodayJason](https://github.com/webdevtodayjason)
