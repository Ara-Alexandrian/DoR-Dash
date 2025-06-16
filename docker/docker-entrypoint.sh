#!/bin/bash
set -e

# Configuration
REPO_URL="${REPO_URL:-https://github.com/Ara-Alexandrian/DoR-Dash.git}"
BRANCH="${BRANCH:-master}"
UPDATE_CHECK_INTERVAL="${UPDATE_CHECK_INTERVAL:-300}" # Check every 5 minutes
APP_DIR="/app"
BACKEND_DIR="/app/backend"
FRONTEND_BUILD_DIR="/app/frontend/build"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to check for updates
check_for_updates() {
    if [ ! -d "/tmp/repo-check" ]; then
        git clone --depth 1 --branch "$BRANCH" "$REPO_URL" /tmp/repo-check >/dev/null 2>&1 || {
            warn "Failed to clone repository for update check"
            return 1
        }
    else
        cd /tmp/repo-check
        git fetch origin "$BRANCH" >/dev/null 2>&1 || {
            warn "Failed to fetch updates"
            return 1
        }
        git reset --hard "origin/$BRANCH" >/dev/null 2>&1
    fi
    
    # Get the latest commit hash
    cd /tmp/repo-check
    LATEST_COMMIT=$(git rev-parse HEAD)
    
    # Compare with current commit if it exists
    if [ -f "/app/.current-commit" ]; then
        CURRENT_COMMIT=$(cat /app/.current-commit)
        if [ "$LATEST_COMMIT" != "$CURRENT_COMMIT" ]; then
            log "New commit detected: $LATEST_COMMIT"
            return 0  # Update available
        else
            return 1  # No update
        fi
    else
        # First run, save current commit
        echo "$LATEST_COMMIT" > /app/.current-commit
        return 1  # No update needed
    fi
}

# Function to perform update
perform_update() {
    log "Performing application update..."
    
    # Stop services gracefully
    if [ -f "/tmp/backend.pid" ]; then
        kill $(cat /tmp/backend.pid) 2>/dev/null || true
    fi
    if [ -f "/tmp/frontend.pid" ]; then
        kill $(cat /tmp/frontend.pid) 2>/dev/null || true
    fi
    
    # Backup current version
    cp -r "$BACKEND_DIR" "/tmp/backend-backup-$(date +%s)" || true
    
    # Update backend
    log "Updating backend..."
    cd /tmp/repo-check
    cp -r backend/* "$BACKEND_DIR/"
    
    # Install any new backend dependencies
    cd "$BACKEND_DIR"
    pip install --no-cache-dir -r requirements.txt >/dev/null 2>&1 || {
        error "Failed to install backend dependencies"
        return 1
    }
    
    # Update frontend build if needed
    if [ -d "/tmp/repo-check/frontend" ]; then
        log "Rebuilding frontend..."
        cd /tmp/repo-check/frontend
        
        # Install dependencies and build
        npm ci --only=production >/dev/null 2>&1 || {
            error "Failed to install frontend dependencies"
            return 1
        }
        
        # Build with production settings
        VITE_API_URL="" VITE_USE_MOCK=false npm run build >/dev/null 2>&1 || {
            error "Failed to build frontend"
            return 1
        }
        
        # Replace frontend build
        rm -rf "$FRONTEND_BUILD_DIR"
        mkdir -p "$FRONTEND_BUILD_DIR"
        cp -r build/* "$FRONTEND_BUILD_DIR/"
    fi
    
    # Update commit hash
    echo "$(cd /tmp/repo-check && git rev-parse HEAD)" > /app/.current-commit
    
    success "Update completed successfully"
    return 0
}

# Function to start services
start_services() {
    log "Starting DoR-Dash services..."
    
    # Start SSH service
    log "Starting SSH service..."
    service ssh start || warn "SSH service failed to start"
    
    # Apply database migrations
    cd "$BACKEND_DIR"
    log "Applying database migrations..."
    alembic upgrade head || warn "Database migration failed (this may be normal on first run)"
    
    # Start backend
    log "Starting backend server..."
    cd "$BACKEND_DIR"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --forwarded-allow-ips "*" > /app/logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/backend.pid
    
    # Start frontend server (serves the built files)
    log "Starting frontend server..."
    cd /app/frontend
    
    # Check if our custom Node.js server exists
    if [ -f "server.js" ] && [ -f "build/index.html" ]; then
        log "Using custom Node.js server with SPA routing support..."
        HOST=0.0.0.0 PORT=1717 node server.js > /app/logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > /tmp/frontend.pid
        log "Started custom Node.js server on port 1717"
        return
    fi
    
    # Fallback: Install serve if not present (with retries)
    if ! command -v serve &> /dev/null; then
        log "Installing serve package for SPA routing support..."
        for i in {1..3}; do
            if npm install -g serve >/dev/null 2>&1; then
                log "Successfully installed serve package"
                break
            else
                warn "Attempt $i to install serve failed, retrying..."
                sleep 2
            fi
        done
        
        # Final check after retries
        if ! command -v serve &> /dev/null; then
            error "Failed to install serve package after 3 attempts"
            error "Using Python fallback (SPA routing will not work)"
            cd "$FRONTEND_BUILD_DIR" 
            python3 -m http.server 1717 --bind 0.0.0.0 > /app/logs/frontend.log 2>&1 &
            FRONTEND_PID=$!
            echo $FRONTEND_PID > /tmp/frontend.pid
            return
        fi
    fi
    
    # Use serve for better SPA support
    cd /app/frontend
    serve -s build -l 1717 --host 0.0.0.0 > /app/logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/frontend.pid
    
    success "Services started - Backend: PID $BACKEND_PID, Frontend: PID $FRONTEND_PID"
}

# Function to monitor and auto-update
monitor_updates() {
    while true; do
        sleep "$UPDATE_CHECK_INTERVAL"
        
        if check_for_updates; then
            log "Update available, performing update..."
            if perform_update; then
                start_services
            else
                error "Update failed, continuing with current version"
            fi
        fi
    done
}

# Trap signals to ensure graceful shutdown
cleanup() {
    log "Shutting down services..."
    if [ -f "/tmp/backend.pid" ]; then
        kill $(cat /tmp/backend.pid) 2>/dev/null || true
    fi
    if [ -f "/tmp/frontend.pid" ]; then
        kill $(cat /tmp/frontend.pid) 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGTERM SIGINT

# Main execution
log "DoR-Dash Container Starting..."
log "Repository: $REPO_URL"
log "Branch: $BRANCH"
log "Auto-update interval: ${UPDATE_CHECK_INTERVAL}s"

# Create necessary directories
mkdir -p /app/logs /app/uploads /app/data

# Set default environment variables if not provided
export POSTGRES_SERVER="${POSTGRES_SERVER:-172.30.98.213}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_USER="${POSTGRES_USER:-DoRadmin}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-1232}"
export POSTGRES_DB="${POSTGRES_DB:-DoR}"
export REDIS_SERVER="${REDIS_SERVER:-172.30.98.214}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export SECRET_KEY="${SECRET_KEY:-insecure_default_key_for_development_only}"
export OLLAMA_API_URL="${OLLAMA_API_URL:-http://172.30.98.14:11434/api/generate}"

# Check for initial updates
if [ "$AUTO_UPDATE" = "true" ] || [ "$AUTO_UPDATE" = "restart_only" ]; then
    log "Checking for updates on startup..."
    if check_for_updates; then
        log "Updates found, applying..."
        if perform_update; then
            log "Update completed successfully"
        else
            warn "Update failed, continuing with current version"
        fi
    else
        log "No updates available"
    fi
fi

# Start services
start_services

# Start update monitoring in background if enabled (only for continuous mode)
if [ "$AUTO_UPDATE" = "true" ] && [ "$UPDATE_CHECK_INTERVAL" != "0" ]; then
    log "Starting continuous auto-update monitor (interval: ${UPDATE_CHECK_INTERVAL}s)..."
    monitor_updates &
elif [ "$AUTO_UPDATE" = "restart_only" ]; then
    log "Auto-update mode: restart_only (no continuous monitoring)"
fi

# Keep container running and wait for signals
log "DoR-Dash is running. Backend: http://0.0.0.0:8000, Frontend: http://0.0.0.0:1717"
wait