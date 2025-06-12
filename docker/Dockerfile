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
    gnupg \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify Node.js installation
RUN node --version && npm --version

# Configure SSH for proper root access
RUN mkdir -p /var/run/sshd /root/.ssh && \
    echo 'root:dor-ssh-password-2024' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config && \
    echo 'AuthorizedKeysFile .ssh/authorized_keys' >> /etc/ssh/sshd_config && \
    chmod 700 /root/.ssh

# Create a non-root user for SSH access
RUN useradd -m -s /bin/bash dor-user && \
    echo 'dor-user:dor-user-password-2024' | chpasswd && \
    usermod -aG sudo dor-user

# Setup SSH keys for automated access
RUN echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDKCukViia1sdF9sP4RhdPa9fq6lyuEq7vLMZFhzpsouBq1D5rTVsoa2YTwuMY9AXG2cPIbzR9x/wj36GTWkwANg5w6sn4j7gQSTEoKqxF8SDfGIAwWfWD2hgOwwhbSEcScqze/fOzT5Zx8U/xujIEqY0vZJVPmqWRafEQeJgSxjyc65xpYDpNDs4wcIdT4cuCpq8FdXDXfpC5+nW23WiPpIR9os1dxikj51MEN3x0VDIwo82sAXGvm63OAYvPU/BAgtCXly0r+Enbtg7Rl/sdPMe9FsbkhoJvnjzBQ17dpmS/A4J7oEpCP8cVv1xUh6z9RyWKGfOmZzlF/pqKrN3WIB8JKPNeIavJVrrwBIOn9lOE7rGkjZBMY8/WXn2vngqoMUR28LgZyPkB7uyrEy3VTWt6qHIDmX/g7p/wQAZADmUGY3bh9yBz9NqLTf5V+V6LhgOKCTGn1Xsp9YP4SXAL4gvPvNwlEU6p6Q5i3FoQiaBHUWavgO5wOyP//IT+hVi8= codeuser@1294490bc291" > /root/.ssh/authorized_keys && \
    chmod 600 /root/.ssh/authorized_keys

# Generate SSH host keys
RUN ssh-keygen -A

# Configure root user environment for better console access with splash
RUN echo '#!/bin/bash' > /root/.bash_profile && \
    echo 'clear' >> /root/.bash_profile && \
    echo 'cat << "EOF"' >> /root/.bash_profile && \
    echo ' ____        ____        ____            _     ' >> /root/.bash_profile && \
    echo '|  _ \  ___ |  _ \      |  _ \  __ _ ___| |__  ' >> /root/.bash_profile && \
    echo '| | | |/ _ \| |_) |_____| | | |/ _` / __| '\''_ \ ' >> /root/.bash_profile && \
    echo '| |_| | (_) |  _ <______| |_| | (_| \__ \ | | |' >> /root/.bash_profile && \
    echo '|____/ \___/|_| \_\     |____/ \__,_|___/_| |_|' >> /root/.bash_profile && \
    echo '                                              ' >> /root/.bash_profile && \
    echo '🏥 Mary Bird Perkins Research Management System' >> /root/.bash_profile && \
    echo '🐳 Container Environment | 🔧 Root Access Enabled' >> /root/.bash_profile && \
    echo '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' >> /root/.bash_profile && \
    echo 'EOF' >> /root/.bash_profile && \
    echo 'echo' >> /root/.bash_profile && \
    echo 'echo "📍 Working Directory: $(pwd)"' >> /root/.bash_profile && \
    echo 'echo "🔗 Frontend: http://$(hostname -i):1717"' >> /root/.bash_profile && \
    echo 'echo "🔗 Backend API: http://$(hostname -i):8000"' >> /root/.bash_profile && \
    echo 'echo "📊 Services Status:"' >> /root/.bash_profile && \
    echo 'ps aux | grep -E "(node|uvicorn)" | grep -v grep | while read line; do echo "  ✅ $line"; done' >> /root/.bash_profile && \
    echo 'echo' >> /root/.bash_profile && \
    chmod +x /root/.bash_profile

# Set up bash environment
RUN echo 'export PS1="\\[\\033[01;31m\\]root@dor-dash\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]# "' >> /root/.bashrc && \
    echo 'alias ll="ls -la"' >> /root/.bashrc && \
    echo 'alias la="ls -la"' >> /root/.bashrc && \
    echo 'alias logs="tail -f /app/logs/*.log"' >> /root/.bashrc && \
    echo 'alias restart-frontend="cd /app/frontend && HOST=0.0.0.0 PORT=1717 node server.js &"' >> /root/.bashrc && \
    echo 'cd /app' >> /root/.bashrc && \
    echo 'source /root/.bash_profile' >> /root/.bashrc

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

# Ensure root is the default user
USER root

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]