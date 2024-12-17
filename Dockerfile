FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and PostgreSQL 16 tools
RUN apt-get update && \
    apt-get install -y gcc curl gnupg2 && \
    # Add PostgreSQL repository
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/postgresql.list && \
    # Update and install PostgreSQL 16 client
    apt-get update && \
    apt-get install -y postgresql-client-16 && \
    # Cleanup
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Incrementing version number..."\n\
python3 << EOF\n\
from sqlalchemy import create_engine, text\n\
import os\n\
import time\n\
\n\
# Wait for database\n\
time.sleep(5)\n\
\n\
try:\n\
    engine = create_engine(os.environ["DATABASE_URL"])\n\
    with engine.connect() as conn:\n\
        result = conn.execute(text("SELECT value FROM configuration WHERE key = '\''build_number'\''"))\n\
        current = result.scalar()\n\
        if current:\n\
            major, minor, patch = current.split(".")\n\
            new_version = f"{major}.{minor}.{int(patch) + 1}"\n\
            conn.execute(\n\
                text("UPDATE configuration SET value = :new_version WHERE key = '\''build_number'\''"),\n\
                {"new_version": new_version}\n\
            )\n\
        else:\n\
            conn.execute(\n\
                text("INSERT INTO configuration (key, value, description) VALUES ('\''build_number'\'', '\''1.0.0'\'', '\''Current build number'\'')")\n\
            )\n\
        conn.commit()\n\
except Exception as e:\n\
    print(f"Error updating version: {str(e)}")\n\
EOF\n\
\n\
exec gunicorn --bind 0.0.0.0:8080 run:app' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Start the application using the startup script
CMD ["/app/start.sh"]