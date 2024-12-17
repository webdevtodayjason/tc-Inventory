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

# Create version increment script
cat > increment_version.py << 'EOF'
from sqlalchemy import create_engine, text
import os
import sys

print("Starting version increment script...")
print(f"Python version: {sys.version}")

try:
    # Get database URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL not found in environment")
        sys.exit(1)
    print("Database URL found")
    
    # Connect to database
    print("Connecting to database...")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("Connected to database")
        
        # Get current version
        print("Fetching current version...")
        result = conn.execute(text("SELECT value FROM configuration WHERE key = 'build_number'"))
        current = result.scalar()
        print(f"Current version: {current}")
        
        if current:
            # Parse and increment version
            major, minor, patch = current.split('.')
            new_version = f"{major}.{minor}.{int(patch) + 1}"
            
            # Update version
            print(f"Updating version to {new_version}...")
            conn.execute(text("UPDATE configuration SET value = :new_version WHERE key = 'build_number'"), 
                        {'new_version': new_version})
            conn.commit()
            print(f"Version successfully incremented from {current} to {new_version}")
        else:
            # Insert initial version if not exists
            print("No version found, creating initial version...")
            conn.execute(text("INSERT INTO configuration (key, value, description) VALUES ('build_number', '1.0.0', 'Current build number')"))
            conn.commit()
            print("Initial version 1.0.0 created")
        
except Exception as e:
    print(f"Error incrementing version: {str(e)}")
    sys.exit(1)

print("Version increment completed successfully")
EOF

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

# Run version increment script
echo "=== Incrementing build version ==="
echo "Running version increment script..."
python3 increment_version.py
VERSION_RESULT=$?
if [ $VERSION_RESULT -eq 0 ]; then
    echo "Version increment completed successfully"
else
    echo "Version increment failed with exit code: $VERSION_RESULT"
fi

echo "=== Deployment complete ==="
echo "Final time: $(date)"