# Use Microsoft Playwright image as base
FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy
# Set working directory
WORKDIR /app
ENV TZ=Asia/Shanghai

# Prevent interactive prompts during package installation (like tzdata asking for region)
ARG DEBIAN_FRONTEND=noninteractive

# Install tzdata package, netcat (for entrypoint wait), curl (for healthcheck)
# and configure system timezone
RUN apt-get update && \
    # Combine installations into one layer
    apt-get install -y --no-install-recommends \
      tzdata \
      netcat \
      curl && \
    # Configure the system timezone using the TZ variable
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    # Clean up apt cache to reduce image size
    rm -rf /var/lib/apt/lists/*
# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DB_HOST=mysql
ENV MYSQL_ROOT_PASSWORD=password


# Expose the port Gunicorn will run on
EXPOSE 5000

# Create entrypoint script
# Waits for DB, initializes DB, then runs Gunicorn
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Wait for the database to be ready' >> /app/entrypoint.sh && \
    echo 'echo "Waiting for MySQL ($DB_HOST:$DB_PORT)..."' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Initialize the database (create tables, etc.)' >> /app/entrypoint.sh && \
    echo 'echo "Initializing database..."' >> /app/entrypoint.sh && \
    echo 'python db_init.py' >> /app/entrypoint.sh && \
    echo 'echo "Database initialization complete."' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Start the application using Gunicorn' >> /app/entrypoint.sh && \
    echo 'echo "Starting application with Gunicorn..."' >> /app/entrypoint.sh && \
    echo 'exec gunicorn --workers 4 --bind 0.0.0.0:5000 app:app' >> /app/entrypoint.sh && \
    # Make the script executable
    chmod +x /app/entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Optional: Add a basic healthcheck (adjust endpoint if needed)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
   CMD curl -f http://localhost:5000/health || exit 1