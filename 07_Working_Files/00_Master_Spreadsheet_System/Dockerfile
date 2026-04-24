# Financial Master - Docker Image
# Multi-stage build for production deployment

# Stage 1: Python dependencies
FROM python:3.11-slim as python-deps

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Node.js build for React dashboard
FROM node:20-alpine as node-build

WORKDIR /app/dashboard

# Copy dashboard files
COPY dashboard/package*.json ./
RUN npm install

COPY dashboard/ ./
RUN npm run build

# Stage 3: Final production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from stage 1
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy application code
COPY *.py ./
COPY .env.example ./.env

# Copy built dashboard
COPY --from=node-build /app/dashboard/dist ./dashboard/dist

# Create necessary directories
RUN mkdir -p data logs backups models

# Expose ports
EXPOSE 8000 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start command
CMD ["python", "main.py"]
