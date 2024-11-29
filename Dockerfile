FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

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

# Initialize database and start application
CMD flask db stamp head || true && \
    flask db upgrade && \
    if [ ! -f .initialized ]; then \
      flask create-category && \
      flask create-cpus && \
      flask create-tags && \
      flask create-admin && \
      touch .initialized; \
    fi && \
    gunicorn --bind 0.0.0.0:8080 run:app 