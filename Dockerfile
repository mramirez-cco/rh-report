FROM python:3.11-slim

# Metadata
LABEL maintainer="tu@email.com"
LABEL description="Red Hat Catalog Image Reporter CLI"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py pyproject.toml MANIFEST.in ./

# Install the package
RUN pip install --no-cache-dir -e .

# Create data directory
RUN mkdir -p /data
WORKDIR /data

# Set entry point
ENTRYPOINT ["rh-report"]
CMD ["--help"]
