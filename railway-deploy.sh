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

# Function to increment version directly in database
increment_version() {
    python3 << EOF
from sqlalchemy import create_engine, text
import os

try:
    # Connect to database
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        # Get current version
        result = conn.execute(text("SELECT value FROM configuration WHERE key = 'build_number'"))
        current = result.scalar()
        
        if current:
            # Parse and increment version
            major, minor, patch = current.split('.')
            new_version = f"{major}.{minor}.{int(patch) + 1}"
            
            # Update version
            conn.execute(text("UPDATE configuration SET value = :new_version WHERE key = 'build_number'"), 
                        {'new_version': new_version})
            conn.commit()
            print(f"Version incremented from {current} to {new_version}")
        else:
            # Insert initial version if not exists
            conn.execute(text("INSERT INTO configuration (key, value, description) VALUES ('build_number', '1.0.0', 'Current build number')"))
            conn.commit()
            print("Initial version 1.0.0 created")
        
except Exception as e:
    print(f"Error incrementing version: {str(e)}")
    exit(1)
EOF
}

echo "=== Starting deployment process ==="
echo "Current time: $(date)"

echo "Waiting for database to be ready..."
sleep 30

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

# Increment version directly in database
echo "=== Incrementing build version ==="
increment_version

echo "=== Deployment complete ==="
echo "Final time: $(date)"