# Multi-stage build for DoR-Dash Application
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend build
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm install

# Install serve for production frontend serving (fallback)
RUN npm install -g serve

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production with environment variables
ENV VITE_API_URL=""
ENV VITE_USE_MOCK=false
RUN npm run build

# Backend stage
FROM python:3.11-slim AS backend-base

# Install system dependencies including SSH and Node.js
RUN apt-get update && apt-get install -y \
    git \
    curl \
    openssh-server \
    sudo \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for frontend server)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Configure SSH
RUN mkdir /var/run/sshd
RUN echo 'root:dor-ssh-password-2024' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Create a non-root user for SSH access
RUN useradd -m -s /bin/bash dor-user && \
    echo 'dor-user:dor-user-password-2024' | chpasswd && \
    usermod -aG sudo dor-user

# Setup SSH keys for automated access
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh && \
    echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDKCukViia1sdF9sP4RhdPa9fq6lyuEq7vLMZFhzpsouBq1D5rTVsoa2YTwuMY9AXG2cPIbzR9x/wj36GTWkwANg5w6sn4j7gQSTEoKqxF8SDfGIAwWfWD2hgOwwhbSEcScqze/fOzT5Zx8U/xujIEqY0vZJVPmqWRafEQeJgSxjyc65xpYDpNDs4wcIdT4cuCpq8FdXDXfpC5+nW23WiPpIR9os1dxikj51MEN3x0VDIwo82sAXGvm63OAYvPU/BAgtCXly0r+Enbtg7Rl/sdPMe9FsbkhoJvnjzBQ17dpmS/A4J7oEpCP8cVv1xUh6z9RyWKGfOmZzlF/pqKrN3WIB8JKPNeIavJVrrwBIOn9lOE7rGkjZBMY8/WXn2vngqoMUR28LgZyPkB7uyrEy3VTWt6qHIDmX/g7p/wQAZADmUGY3bh9yBz9NqLTf5V+V6LhgOKCTGn1Xsp9YP4SXAL4gvPvNwlEU6p6Q5i3FoQiaBHUWavgO5wOyP//IT+hVi8= codeuser@1294490bc291" > /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

# Generate host keys
RUN ssh-keygen -A

# Set working directory
WORKDIR /app

# Copy backend requirements and install dependencies
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ /app/backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build /app/frontend/build
COPY --from=frontend-builder /app/frontend/server.js /app/frontend/
COPY --from=frontend-builder /app/frontend/package*.json /app/frontend/
COPY --from=frontend-builder /app/frontend/node_modules /app/frontend/node_modules

# Create uploads and logs directories
RUN mkdir -p /app/uploads /app/logs

# Create startup script with auto-update functionality
COPY docker/docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Environment variables
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 1717 22

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]