# --- Minimal MVP Dockerfile for backend/ ---
FROM python:3.11-slim

# Avoid .pyc files and ensure stdout is flushed
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Install system dependencies (optional — remove if not needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code into container
COPY . .

# Default command to run the API
CMD ["uvicorn", "arxiv_importer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Build the Docker Image
# docker build -t arxiv-importer-backend ./backend
# Run the Container
# docker run -p 8000:8000 arxiv-importer-backend
