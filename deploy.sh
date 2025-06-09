#!/bin/bash

# DoR-Dash Deployment Script for Unraid
# This script builds and deploys the DoR-Dash application as a Docker container

set -e

# Configuration
IMAGE_NAME="dor-dash"
CONTAINER_NAME="dor-dash"
UNRAID_HOST="172.30.98.10"
CONTAINER_IP="172.30.98.177"
FRONTEND_PORT="1717"
BACKEND_PORT="1718"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Function to check if running on Unraid
check_unraid() {
    if [ ! -f "/etc/unraid-version" ]; then
        warn "This script is designed for Unraid. Continuing anyway..."
    else
        log "Unraid detected: $(cat /etc/unraid-version)"
    fi
}

# Function to stop existing container
stop_existing() {
    log "Stopping existing container if running..."
    if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
    
    if docker ps -aq --filter "name=$CONTAINER_NAME" | grep -q .; then
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
}

# Function to build image
build_image() {
    log "Building Docker image..."
    docker build -t "$IMAGE_NAME:latest" . || {
        error "Failed to build Docker image"
        exit 1
    }
    success "Docker image built successfully"
}

# Function to run container
run_container() {
    log "Starting DoR-Dash container..."
    
    # Use br0 network with dedicated IP for webapp
    log "Using br0 network with dedicated IP $CONTAINER_IP"
    NETWORK_ARGS="--network br0 --ip $CONTAINER_IP"
    
    docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        $NETWORK_ARGS \
        -e POSTGRES_SERVER="172.30.98.213" \
        -e POSTGRES_PORT="5432" \
        -e POSTGRES_USER="DoRadmin" \
        -e POSTGRES_PASSWORD="1232" \
        -e POSTGRES_DB="DoR" \
        -e REDIS_SERVER="172.30.98.214" \
        -e REDIS_PORT="6379" \
        -e SECRET_KEY="insecure_default_key_for_development_only" \
        -e OLLAMA_API_URL="http://172.30.98.14:11434/api/generate" \
        -e AUTO_UPDATE="restart_only" \
        -e REPO_URL="https://github.com/Ara-Alexandrian/DoR-Dash.git" \
        -e BRANCH="master" \
        -e UPDATE_CHECK_INTERVAL="0" \
        -e VITE_API_URL="" \
        -e VITE_USE_MOCK="false" \
        -v dor-dash-uploads:/app/uploads \
        -v dor-dash-logs:/app/logs \
        "$IMAGE_NAME:latest" || {
        error "Failed to start container"
        exit 1
    }
    
    success "Container started successfully"
}

# Function to show status
show_status() {
    log "Container status:"
    docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    log "Access URLs:"
    echo -e "${GREEN}Frontend:${NC} http://$CONTAINER_IP:7117"
    echo -e "${GREEN}Backend API:${NC} http://$CONTAINER_IP:8000"
    echo -e "${GREEN}Health Check:${NC} http://$CONTAINER_IP:8000/health"
    
    echo ""
    log "Nginx Reverse Proxy Configuration:"
    echo -e "${YELLOW}Frontend:${NC} http://$CONTAINER_IP:7117"
    echo -e "${YELLOW}Backend API:${NC} http://$CONTAINER_IP:8000/api/"
    echo ""
    echo -e "${BLUE}Use the nginx.conf file provided for reverse proxy setup${NC}"
}

# Function to show logs
show_logs() {
    log "Container logs (last 50 lines):"
    docker logs --tail 50 "$CONTAINER_NAME" 2>/dev/null || {
        warn "Container not running or no logs available"
    }
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            log "Starting DoR-Dash deployment..."
            check_unraid
            stop_existing
            build_image
            run_container
            sleep 5  # Give container time to start
            show_status
            ;;
        "stop")
            log "Stopping DoR-Dash..."
            stop_existing
            success "Container stopped"
            ;;
        "restart")
            log "Restarting DoR-Dash..."
            stop_existing
            run_container
            sleep 5
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "rebuild")
            log "Rebuilding and redeploying DoR-Dash..."
            stop_existing
            docker rmi "$IMAGE_NAME:latest" 2>/dev/null || true
            build_image
            run_container
            sleep 5
            show_status
            ;;
        *)
            echo "Usage: $0 {deploy|stop|restart|status|logs|rebuild}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy the application (default)"
            echo "  stop     - Stop the running container"
            echo "  restart  - Restart the container"
            echo "  status   - Show container status and access URLs"
            echo "  logs     - Show container logs"
            echo "  rebuild  - Rebuild image and redeploy"
            exit 1
            ;;
    esac
}

main "$@"