# Multi-stage build for DoR-Dash Application
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend build
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm install

# Install serve for production frontend serving
RUN npm install -g serve

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production with environment variables
ENV VITE_API_URL=""
ENV VITE_USE_MOCK=false
RUN npm run build

# Backend stage
FROM python:3.11-slim AS backend-base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ /app/backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Create uploads and logs directories
RUN mkdir -p /app/uploads /app/logs

# Create startup script with auto-update functionality
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Environment variables
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 7117

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]