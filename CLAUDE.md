# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TC Inventory System is a comprehensive Flask-based inventory management system with both web and mobile interfaces. It tracks general inventory items and computer systems with features like barcode scanning, location tracking, and multi-user support.

## Key Technologies

- **Backend**: Python 3.11, Flask 3.1.0, PostgreSQL 16, SQLAlchemy 2.0
- **Frontend**: Jinja2 templates, Bootstrap, JavaScript
- **Mobile**: Flutter (iOS/Android)
- **Authentication**: Flask-Login (web), Flask-JWT-Extended (mobile API)

## Essential Commands

### Development
```bash
# Run development server
flask run -p 5001

# Run production server
gunicorn --bind 0.0.0.0:8080 run:app
```

### Database Management
```bash
# Apply database migrations
flask db upgrade

# Initialize categories
flask create-category

# Create admin user (uses env vars)
flask create-admin

# Initialize configuration
flask init-config

# Create new migration
flask db migrate -m "Description"
```

### Testing
```bash
# Run tests
pytest

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8
```

### Docker
```bash
# Build image
docker build -t tcinventory .

# Run container
docker run -p 8080:8080 --env-file .env tcinventory
```

## Architecture Overview

### Application Structure
```
app/
├── api/mobile/          # Mobile API endpoints with JWT auth
├── models/              # SQLAlchemy models
│   ├── inventory.py     # InventoryItem, ComputerSystem, Category, Tag
│   ├── user.py          # User model with roles
│   └── config.py        # Configuration settings
├── routes/              # Web routes (Flask-Login protected)
├── templates/           # Jinja2 templates with dark/light theme support
├── static/              # CSS, JS, API documentation
└── utils/               # Utility modules (email, barcode, CSV import/export)
```

### Key Models
- **InventoryItem**: Base model for all inventory items
- **ComputerSystem**: Extended model with computer-specific fields
- **User**: Supports admin/user roles with PIN codes
- **Configuration**: Dynamic system settings stored in DB

### Authentication Flow
- **Web**: Session-based with Flask-Login, PIN code quick access
- **Mobile API**: JWT tokens via `/api/mobile/auth/login`
- **CSRF**: Disabled for mobile API endpoints

### Database Migrations
Uses Flask-Migrate (Alembic). All schema changes must go through migrations:
1. Make model changes
2. Generate migration: `flask db migrate -m "description"`
3. Review generated migration file
4. Apply: `flask db upgrade`

### Mobile API
- Base path: `/api/mobile/`
- Auth header: `Authorization: Bearer <token>`
- OpenAPI spec: `/app/static/api/tc_inventory_api.yaml`

### Environment Variables
Required in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key
- `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_PIN`
- `UPCITEMDB_API_KEY`: For barcode scanning

### Testing Approach
- Test framework: pytest
- Test location: `/tests/`
- Run all tests: `pytest`
- Current coverage: Basic authentication tests

### Common Development Tasks

#### Adding a New Route
1. Create route function in appropriate file under `app/routes/`
2. Use `@login_required` decorator for protected routes
3. Follow existing naming conventions and template structure

#### Adding Mobile API Endpoint
1. Add endpoint to `app/api/mobile/`
2. Use `@jwt_required()` for protected endpoints
3. Return JSON responses with appropriate status codes

#### Modifying Database Schema
1. Update model in `app/models/`
2. Generate migration: `flask db migrate -m "description"`
3. Review and apply migration

#### Working with Templates
- All templates extend `base.html`
- Support dark/light themes via CSS classes
- Use Bootstrap components consistently