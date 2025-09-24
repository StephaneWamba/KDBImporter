# Dockerfile for oQo-scripts
FROM python:3.11-slim

# Avoid .pyc files and ensure stdout is flushed
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create include directory for tags and categories
RUN mkdir -p /app/include

# Set default environment variables
ENV INCLUDE_PATH=/app/include
ENV PG_HOST=postgres
ENV PG_PORT=5432
ENV PG_USER=myuser
ENV PG_PASSWORD=mypassword
ENV PG_DB=mydatabase

# Default command (can be overridden)
CMD ["python", "src/main_arxiv.py"]
