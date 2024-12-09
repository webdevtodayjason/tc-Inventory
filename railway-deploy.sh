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
    # Try internal URL first
    engine = create_engine(os.environ['DATABASE_URL'])
    try:
        connection = engine.connect()
        connection.close()
        print("Database connection successful using internal URL!")
        exit(0)
    except Exception as internal_error:
        print(f"Internal connection failed: {internal_error}")
        
        # Try public URL as fallback
        if 'DATABASE_PUBLIC_URL' in os.environ:
            print("Trying public URL...")
            engine = create_engine(os.environ['DATABASE_PUBLIC_URL'])
            connection = engine.connect()
            connection.close()
            print("Database connection successful using public URL!")
            exit(0)
        raise
except Exception as e:
    print(f"Database connection failed: {e}")
    exit(1)
EOF
}

echo "Waiting for database to be ready..."
sleep 30  # Increased initial wait time

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

echo "Deployment complete!"