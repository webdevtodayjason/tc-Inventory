# TC Inventory System

A comprehensive web-based inventory management system for tracking computer and networking equipment. Built with Flask and modern Python practices.

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3118/)
[![Flask Version](https://img.shields.io/badge/flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Conda (for environment management)
- Modern web browser with JavaScript enabled

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/inventory-system.git
cd inventory-system
```


2. Create and activate a Conda environment:
```bash
# Create a new conda environment
conda create -n inventory-system python=3.11

# Activate the environment
conda activate inventory-system

# Install pip inside conda environment (if not already installed)
conda install pip
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your development configuration
```

5. Initialize Database and Create Initial Data:
```bash
flask db upgrade
```

6. Create a test admin user:
```bash
flask create-admin
```

7. Run the development server:
```bash
flask run --debug
```

The application will be available at `http://localhost:5000`

### Production Setup

1. Set up a production server (e.g., Ubuntu 22.04 LTS)

2. Install system dependencies:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql nginx
```

3. Create a PostgreSQL database:
```bash
sudo -u postgres createdb inventory_db
```

4. Clone and set up the application:
```bash
git clone https://github.com/yourusername/inventory-system.git
cd inventory-system
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with production settings
```

6. Set up Gunicorn and Nginx:
```bash
pip install gunicorn
# Configure Nginx (see deployment/nginx.conf)
```

7. Set up SSL with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx
```

## Development

### Code Style

We follow [PEP 8](https://peps.python.org/pep-0008/) guidelines and use several tools to maintain code quality:

- **Black**: For code formatting
- **Flake8**: For style guide enforcement
- **isort**: For import sorting
- **mypy**: For static type checking

```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8

# Type checking
mypy .
```

### Database Management

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migrations
flask db downgrade
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_inventory.py
```

## API Documentation

The API follows REST principles and provides the following endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/register` - User registration

### Inventory
- `GET /api/inventory` - List all items
- `POST /api/inventory` - Create new item
- `GET /api/inventory/<id>` - Get item details
- `PUT /api/inventory/<id>` - Update item
- `DELETE /api/inventory/<id>` - Delete item

Full API documentation is available at `/api/docs` when running in development mode.

## Project Structure

```plaintext
inventory_system/
├── app/                  # Application package
│   ├── models/          # Database models
│   ├── routes/          # Route handlers
│   ├── templates/       # Jinja2 templates
│   └── static/          # Static files
├── tests/               # Test suite
├── migrations/          # Database migrations
├── deployment/          # Deployment configurations
├── docs/                # Documentation
├── .env                 # Environment variables
└── requirements.txt     # Project dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Security

- All passwords are hashed using industry-standard algorithms
- CSRF protection enabled on all forms
- SQL injection prevention through SQLAlchemy ORM
- Regular security updates and dependency monitoring
- Rate limiting on authentication endpoints
- Session management and secure cookie handling

## Backup and Recovery

The system includes automated backup procedures:

1. Daily database backups
2. File system backups for uploaded content
3. Backup rotation policy (7 daily, 4 weekly, 3 monthly)
4. Automated recovery testing

## Monitoring and Logging

- Application logs stored in `/var/log/inventory-system/`
- Error tracking and reporting
- Performance monitoring
- User action audit trails
- System health checks

## Credits

### Built With
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Bootstrap](https://getbootstrap.com/) - Frontend framework
- [QRCode](https://github.com/lincolnloop/python-qrcode) - QR code generation
- [ReportLab](https://www.reportlab.com/) - PDF generation

### Contributors
- **Your Name** - *Initial work* - [YourGithub](https://github.com/yourusername)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📫 Email: support@example.com
- 💬 Discord: [Join our server](https://discord.gg/yourserver)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/inventory-system/issues)

## Acknowledgments

- Hat tip to the Flask team for the amazing framework
- Inspired by various inventory management systems
- Thanks to all contributors who have helped shape this project

---
Made with ❤️ by [Your Name](https://github.com/yourusername)

### CLI Commands

The application includes several custom Flask CLI commands for database management and initialization:

#### Category Management

After setting up PostgreSQL and configuring the environment, initialize the database and create initial data:

```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial database setup"

# Apply migrations
flask db upgrade
```

#### Create Categories

The system comes with predefined CLI commands to set up initial data:

```bash
flask create-category
```

This command creates a hierarchical structure of categories:

- Hardware
  - Computer Parts
  - Networking Hardware
  - Monitors
  - Cases
  - Power Supply
- Storage
  - HDD-PATA
  - HDD-SSD
  - HDD-SAS
- Memory
  - RAM-MEMORY
- Cables
  - Cables-Networking
  - Cables-Video
  - Cables-Power
  - Bulk Cat5/Cat6
- Components
  - Network Cards
  - Video Cards
  - Motherboards
  - CPU Coolers
- Networking
  - Network Switches
  - Routers
  - Access Points
  - Patch Panels
- Accessories
  - Server Rails
  - Server Caddies
  - KVM Switches
  - Keyboard/Mouse
- Adapters
  - Adapters-Video
  - Adapters-Network
  - Adapters-Power

#### Create Admin User

When running the `create-admin` command, you'll be prompted to enter:
- Username
- Email
- Password

Save these credentials as they'll be needed to log into the system.

### 8. Run the Development Server
```bash
flask run
```

The application will be available at `http://localhost:5001`
