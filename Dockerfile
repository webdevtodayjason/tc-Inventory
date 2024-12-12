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

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Start the application
CMD gunicorn --bind 0.0.0.0:8080 run:app