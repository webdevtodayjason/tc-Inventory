# TC Inventory System

A comprehensive web-based inventory management system for tracking computer and networking equipment. Built with Flask and modern Python practices.

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3118/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Computer system inventory tracking
- Component management (CPUs, Models)
- QR code and barcode generation
- Label printing (2x4 inch format)
- Cost tracking (purchase and selling prices)
- Purchase URL tracking
- Tag-based organization
- Restock alerts
- Multi-tag filtering
- Search and filter functionality
- User authentication and authorization
- PIN-based quick checkout system
- Tablet-optimized checkout interface
- Dark mode support
- Audit trail for inventory changes

## Status System
Items in the system can have the following statuses:
- In Stock (green): Item is available
- Needs Restock (orange): Quantity at or below reorder threshold
- Out of Stock (red): Item is unavailable

## Tag System
Default tags for quick identification and filtering:
- NO TOUCH: Items that should not be handled
- JUMP BOX: Network jump box systems
- DESKTOP: Desktop computers
- INTERNAL: Internal use only
- FOR SALE: Items available for sale
- DO NOT SELL: Items not for sale

Tags can be:
- Assigned to any item type
- Used for filtering in dashboard
- Combined for complex queries
- Added/removed through item management

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Conda (for environment management)
- Modern web browser with JavaScript enabled

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/webdevtodayjason/tc-Inventory.git
cd tc-Inventory
```

### 2. Create and Activate Conda Environment

```bash
# Create a new conda environment
conda create -n inventory-system python=3.11

# Activate the environment
conda activate inventory-system

# Install pip inside conda environment
conda install pip
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

```bash
# Connect to PostgreSQL as postgres user
psql -U postgres

# Create database and user
postgres=# DROP DATABASE IF EXISTS inventory_db;
postgres=# CREATE DATABASE inventory_db;
postgres=# DROP USER IF EXISTS inventory_admin;
postgres=# CREATE USER inventory_admin WITH PASSWORD 'your_password';

# Connect to the inventory_db
postgres=# \c inventory_db

# Set up proper permissions
postgres=# GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_admin;
postgres=# GRANT USAGE ON SCHEMA public TO inventory_admin;
postgres=# GRANT CREATE ON SCHEMA public TO inventory_admin;
postgres=# ALTER SCHEMA public OWNER TO inventory_admin;
postgres=# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO inventory_admin;
postgres=# GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO inventory_admin;
postgres=# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inventory_admin;
postgres=# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inventory_admin;

# Exit psql
postgres=# \q
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your development configuration:
# - Set DATABASE_URL with your PostgreSQL credentials
# - Generate a secure SECRET_KEY
# - Set other configuration options as needed
```

### 6. Initialize Database and Create Initial Data

```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial database setup"

# Apply migrations
flask db upgrade
```

### 7. Create Initial Data

The system comes with predefined CLI commands to set up initial data:

```bash
# Create categories
flask create-category

# Create initial CPU database
flask create-cpus

# Create default tags
flask create-tags

# Create admin user (interactive)
flask create-admin
```

Available CLI Commands:
- `flask create-category`: Creates default category hierarchy
- `flask create-cpus`: Populates database with common CPU models
- `flask create-tags`: Creates default tags (NO TOUCH, JUMP BOX, etc.)
- `flask create-admin`: Creates an admin user (interactive)
- `flask add-computer-model`: Adds a new computer model (interactive)
- `flask add-cpu`: Adds a new CPU model (interactive)

### 8. Run Development Server

```bash
flask run --port=5001
```

The application will be available at `http://localhost:5001`

## Production Deployment (Railway)

### 1. Configure Railway Project

1. Create new project on Railway
2. Add PostgreSQL addon
3. Configure environment variables:
   - `DATABASE_URL` (provided by Railway)
   - `SECRET_KEY`
   - `FLASK_ENV=production`
   - `DEBUG=False`

### 2. Deploy to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link project
railway link

# Deploy
railway up
```

### 3. Initialize Production Database

```bash
railway run flask db upgrade
railway run flask create-category
railway run flask create-cpus
railway run flask create-admin
```

## CLI Commands Reference

### Database Management

```bash
# Create new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Data Management

```bash
# Create categories
flask create-category

# Create CPU database
flask create-cpus

# Create default tags
flask create-tags

# Create admin user
flask create-admin

# Set user PIN
flask set-user-pin <username>
```

## Checkout System

The system includes a tablet-optimized checkout interface that allows:
- Quick PIN-based authentication for technicians
- Barcode/QR code scanning
- Multiple item quantity selection
- Automatic stock level tracking
- Checkout history tracking
- Recent transactions view

## Project Structure

```plaintext
tc-Inventory/
├── app/                  # Application package
│   ├── models/          # Database models
│   ├── routes/          # Route handlers
│   ├── templates/       # Jinja2 templates
│   └── static/          # Static files
├── tests/               # Test suite
├── migrations/          # Database migrations
├── .env                 # Environment variables
└── requirements.txt     # Project dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
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
