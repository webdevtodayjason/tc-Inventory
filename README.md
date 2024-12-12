# TC Inventory System

A comprehensive inventory management system built with Flask, designed for tracking general inventory items and computer systems.

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3118/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL Version](https://img.shields.io/badge/postgresql-16-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Core Functionality
- Track both general inventory items and computer systems
- Barcode scanning support with UPCItemDB integration
- Dark/Light mode support across all components
- Location-based inventory tracking
- Reorder threshold monitoring
- Multi-user support with role-based access control (Admin/User)
- Quick checkout system with PIN code access
- Automated build number versioning

### Item Management
- Add, edit, view, and delete inventory items
- Barcode scanning for quick item addition
- Storage location tracking
- Automatic restock alerts with email notifications
- Custom tagging system with color coding
- Printable 4x2 labels with barcodes and QR codes
- Bulk item management
- Purchase URL tracking
- CSV import/export functionality with templates

### Computer Systems
- Separate tracking for computer systems
- Detailed computer specifications tracking
- CPU and model management
- Testing results tracking with status indicators
- Component tracking (RAM, Storage, OS)
- Performance benchmarks
- Serial tag management
- Testing status workflow

### Data Management
- Database backup and restore functionality
- CSV import/export with field mapping
- Downloadable import templates
- Log management with date-based filtering
- Automatic data validation
- Nullable field support

### User Management (Admin Only)
- User creation and management
- Role assignment (Admin/User)
- PIN code management for quick access
- Email and password management
- Activity logging per user
- User-specific permissions

### Search and Filter
- Advanced search functionality
- Multiple filter options:
  - Category
  - Type
  - Status
  - Location
  - Tags
- Sortable columns
- Tag-based filtering
- Smart search suggestions

### Interface Features
- Modern responsive design
- Dark/Light mode toggle with full theme support
- Icon-based actions
- Status indicators
- Tag color coding
- Pagination
- Mobile-friendly interface
- Tabbed interface for system types
- Modal dialogs with theme support

### Logging and Monitoring
- Detailed system logs
- Human-readable activity logging
- Downloadable logs with date filtering
- Email notifications for low stock
- Error tracking and reporting
- User activity monitoring

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

4. Set up the PostgreSQL database (version 16 required):

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

# System Defaults
DEFAULT_ITEMS_PER_PAGE=20
DEFAULT_ALLOW_REGISTRATION=false
DEFAULT_REQUIRE_EMAIL_VERIFICATION=false
DEFAULT_ALLOW_PASSWORD_RESET=true

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password
ADMIN_PIN=123456

# API Keys
UPCITEMDB_API_KEY=your_api_key_here
```

6. Initialize the database:

```bash
flask db upgrade
flask create-category
flask create-admin
flask init-config
```

## Usage

1. Start the application:

```bash
flask run -p 5001
```

2. Access the application at `http://127.0.0.1:5001`

3. Log in with the admin credentials configured in your `.env` file

## Docker Deployment

The system includes a Dockerfile for containerized deployment:

```bash
docker build -t tcinventory .
docker run -p 8080:8080 --env-file .env tcinventory
```

## Key Components

### Models
- InventoryItem: Base model for all inventory items
- ComputerSystem: Extended model for computer systems
- Category: Item categorization
- Tag: Item tagging system
- User: User management with role-based access
- Configuration: System settings and preferences

### Features
- Barcode scanning for quick item addition
- Location-based inventory tracking
- Automatic restock alerts with email notifications
- PIN-based quick checkout system
- Role-based access control
- Dark/Light mode theme switching
- 4x2 label printing with barcodes and QR codes
- CSV import/export functionality
- Database backup and restore
- Log management and filtering

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
