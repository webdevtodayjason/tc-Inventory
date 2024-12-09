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

echo "Waiting for database to be ready..."
sleep 10

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