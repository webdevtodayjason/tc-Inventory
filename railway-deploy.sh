#!/bin/bash

# Function to retry a command
retry_command() {
    local -r cmd="$1"
    local -r max_attempts=5
    local -r wait_time=5
    local attempt=1
    
    until $cmd || [ $attempt -eq $max_attempts ]; do
        echo "Attempt $attempt failed! Waiting $wait_time seconds..."
        sleep $wait_time
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo "All attempts failed!"
        return 1
    fi
    return 0
}

# Function to check database connection
check_db_connection() {
    python3 << EOF
from sqlalchemy import create_engine
import os

try:
    engine = create_engine(os.environ['DATABASE_URL'])
    connection = engine.connect()
    connection.close()
    print("Database connection successful!")
    exit(0)
except Exception as e:
    print(f"Database connection failed: {e}")
    exit(1)
EOF
}

echo "=== Starting deployment process ==="
echo "Current time: $(date)"

echo "Waiting for database to be ready..."
sleep 30

echo "Verifying database connection..."
retry_command "check_db_connection"

if [ $? -ne 0 ]; then
    echo "Could not establish database connection. Exiting."
    exit 1
fi

# Apply database migrations
echo "Running database migrations..."
retry_command "flask db upgrade"

# Create initial data
echo "Creating initial categories..."
retry_command "flask create-category"

echo "Creating admin user..."
retry_command "flask create-admin"

echo "Initializing configuration..."
retry_command "flask init-config"

# Increment version
echo "=== Incrementing build version ==="
retry_command "flask increment-version"

echo "=== Deployment complete ==="
echo "Final time: $(date)"