#!/bin/bash

# TC Inventory Local Development Startup Script
# This script sets up and starts the application for local development

echo "🚀 Starting TC Inventory System (Local Development)"
echo "=================================================="

# Load environment variables from .env file
if [ -f .env ]; then
    echo "✅ Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file based on .env.example"
    exit 1
fi

# Check if conda environment is active
if [ -z "$CONDA_DEFAULT_ENV" ] || [ "$CONDA_DEFAULT_ENV" != "flask" ]; then
    echo "⚠️  Conda 'flask' environment not active"
    echo "Please run: conda activate flask"
    echo "Then run this script again"
    exit 1
else
    echo "✅ Conda environment 'flask' is active"
fi

# Check PostgreSQL connection
echo ""
echo "🔍 Checking database connection..."
flask verify-db
if [ $? -ne 0 ]; then
    echo "❌ Database connection failed!"
    echo "Please ensure PostgreSQL is running and DATABASE_URL is correct in .env"
    exit 1
fi

# Run database migrations
echo ""
echo "🔄 Running database migrations..."
flask db upgrade

# Initialize data if needed
echo ""
echo "🔧 Initializing application data..."

# Create categories
flask create-category

# Create admin user
flask create-admin

# Initialize configuration
flask init-config

echo ""
echo "=================================================="
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Flask development server on port 5001..."
echo "🔗 Access the application at: http://127.0.0.1:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Start the Flask development server
flask run -p 5001