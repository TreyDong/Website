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

# Expose the port the app runs on
EXPOSE 5000

# Create entrypoint script
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'echo "Waiting for MySQL to start..."' >> /app/entrypoint.sh && \
 echo 'python db_init.py' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "Starting application..."' >> /app/entrypoint.sh && \
    echo 'exec python app.py' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
