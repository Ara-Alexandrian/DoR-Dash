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
BACKEND_PORT="8000"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

# ASCII Art Functions
show_build_animation() {
    local frames=(
        "🔧 [    ] Building..."
        "🔧 [█   ] Building..."
        "🔧 [██  ] Building..."
        "🔧 [███ ] Building..."
        "🔧 [████] Building..."
        "🎉 [████] Complete!"
    )
    
    for frame in "${frames[@]}"; do
        echo -ne "\r${frame}"
        sleep 0.3
    done
    echo
}

show_docker_whale() {
    echo -e "${BLUE}"
    cat << 'EOF'
         ##         .
   ## ## ##        ==
## ## ## ## ##    ===
/"""""""""""""""""\___/ ===
{                       /  ===-
\______ O           __/
 \    \         __/
  \____\_______/
EOF
    echo -e "${NC}"
}

# Function to build image
build_image() {
    local BUILD_ARGS="$1"
    
    # Enable BuildKit for faster builds with parallel processing
    export DOCKER_BUILDKIT=1
    # Use auto progress for cleaner output (or plain for verbose)
    export BUILDKIT_PROGRESS=auto
    
    echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}     🐳 ${YELLOW}Docker Build Starting${NC}     ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
    
    if [ -n "$BUILD_ARGS" ]; then
        warn "🔥 Force rebuild mode (--no-cache)"
    else
        success "⚡ Smart build mode (using cache)"
    fi
    
    # Show Docker whale animation
    show_docker_whale
    
    # Build with suppressed output for cleaner display
    log "🔨 Building $IMAGE_NAME:latest..."
    if docker build $BUILD_ARGS -t "$IMAGE_NAME:latest" -f docker/Dockerfile . >/dev/null 2>&1; then
        show_build_animation
        success "✅ Docker image built successfully!"
    else
        error "❌ Docker build failed!"
        log "Re-running build with verbose output for debugging..."
        docker build $BUILD_ARGS -t "$IMAGE_NAME:latest" -f docker/Dockerfile .
        exit 1
    fi
}

# Container startup animation
show_startup_animation() {
    local spinner="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    local count=0
    
    while [ $count -lt 20 ]; do
        local i=$(($count % ${#spinner}))
        printf "\r🚀 Starting container... ${spinner:$i:1} "
        sleep 0.1
        count=$((count + 1))
    done
    printf "\r🚀 Starting container... ✅ \n"
}

show_dor_header() {
    echo -e "${GREEN}"
    cat << 'EOF'
 ____        ____        ____            _     
|  _ \  ___ |  _ \      |  _ \  __ _ ___| |__  
| | | |/ _ \| |_) |_____| | | |/ _` / __| '_ \ 
| |_| | (_) |  _ <______| |_| | (_| \__ \ | | |
|____/ \___/|_| \_\     |____/ \__,_|___/_| |_|
                                              
EOF
    echo -e "${NC}${YELLOW}     🏥 Mary Bird Perkins Research Dashboard${NC}"
    echo -e "${BLUE}     ═══════════════════════════════════════${NC}"
    echo
}

# Function to run container
run_container() {
    echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}    🚀 ${YELLOW}Container Deployment${NC}        ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
    
    # Use br0 network with dedicated IP for webapp
    log "🌐 Network: br0 bridge → $CONTAINER_IP"
    NETWORK_ARGS="--network br0 --ip $CONTAINER_IP"
    
    # Run container with suppressed output
    if docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        -p 22:22 \
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
        "$IMAGE_NAME:latest" >/dev/null 2>&1; then
        
        show_startup_animation
        success "✅ Container deployed successfully!"
    else
        error "❌ Container deployment failed!"
        exit 1
    fi
}

# Function to show status
show_status() {
    # Container status in a nice box
    echo -e "${BLUE}╭─────────────────────────────────────────────────╮${NC}"
    echo -e "${BLUE}│${NC}                📊 ${YELLOW}System Status${NC}                 ${BLUE}│${NC}"
    echo -e "${BLUE}╰─────────────────────────────────────────────────╯${NC}"
    
    # Check if container is running
    if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${GREEN}🟢 Container Status: ${NC}${GREEN}RUNNING${NC}"
        echo -e "${GREEN}📅 Started: ${NC}$(docker inspect --format='{{.State.StartedAt}}' $CONTAINER_NAME | cut -d'T' -f1)"
    else
        echo -e "${RED}🔴 Container Status: ${NC}${RED}STOPPED${NC}"
        return
    fi
    
    echo
    echo -e "${BLUE}╭─────────────────────────────────────────────────╮${NC}"
    echo -e "${BLUE}│${NC}                🌐 ${YELLOW}Access URLs${NC}                   ${BLUE}│${NC}"
    echo -e "${BLUE}╰─────────────────────────────────────────────────╯${NC}"
    echo -e "${GREEN}🌍 Production:${NC}  https://dd.kronisto.net"
    echo -e "${GREEN}🖥️  Frontend:${NC}   http://$CONTAINER_IP:1717"
    echo -e "${GREEN}⚡ Backend:${NC}    http://$CONTAINER_IP:8000"
    echo -e "${GREEN}💓 Health:${NC}     http://$CONTAINER_IP:8000/health"
    echo -e "${GREEN}🔐 SSH:${NC}       ssh root@$CONTAINER_IP"
    
    echo
    echo -e "${BLUE}╭─────────────────────────────────────────────────╮${NC}"
    echo -e "${BLUE}│${NC}                🎯 ${YELLOW}Quick Commands${NC}                ${BLUE}│${NC}"
    echo -e "${BLUE}╰─────────────────────────────────────────────────╯${NC}"
    echo -e "${YELLOW}dorlogs${NC}      - View live container logs"
    echo -e "${YELLOW}dorexec${NC}      - SSH into container"
    echo -e "${YELLOW}dorhealth${NC}    - Check health status"
    echo -e "${YELLOW}dorstatus${NC}    - Show this status"
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
            # Show cool header for deploy
            clear
            show_dor_header
            
            log "🚀 Starting DoR-Dash deployment..."
            check_unraid
            stop_existing
            build_image
            run_container
            sleep 3
            
            # Final success display
            echo
            echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║${NC}            🎉 ${YELLOW}Deployment Complete!${NC}           ${GREEN}║${NC}"
            echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
            echo
            show_status
            ;;
        "stop")
            echo -e "${RED}╔══════════════════════════════════════╗${NC}"
            echo -e "${RED}║${NC}      ⏹️  ${YELLOW}Stopping DoR-Dash${NC}        ${RED}║${NC}"
            echo -e "${RED}╚══════════════════════════════════════╝${NC}"
            
            stop_existing
            
            echo -e "${RED}🔴 Container stopped successfully${NC}"
            ;;
        "restart")
            echo -e "${YELLOW}╔══════════════════════════════════════╗${NC}"
            echo -e "${YELLOW}║${NC}      🔄 ${YELLOW}Restarting DoR-Dash${NC}       ${YELLOW}║${NC}"
            echo -e "${YELLOW}╚══════════════════════════════════════╝${NC}"
            
            stop_existing
            run_container
            sleep 3
            
            echo
            echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║${NC}            🎉 ${YELLOW}Restart Complete!${NC}            ${GREEN}║${NC}"
            echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
            echo
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            echo -e "${CYAN}╔══════════════════════════════════════╗${NC}"
            echo -e "${CYAN}║${NC}      📝 ${YELLOW}Container Logs${NC}           ${CYAN}║${NC}"
            echo -e "${CYAN}╚══════════════════════════════════════╝${NC}"
            echo
            
            # Check if container is running first
            if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
                log "📄 Showing last 50 lines of container logs..."
                echo -e "${BLUE}╭─────────────────────────────────────────────────╮${NC}"
                echo -e "${BLUE}│${NC}                    📊 ${YELLOW}Live Logs${NC}                    ${BLUE}│${NC}"
                echo -e "${BLUE}╰─────────────────────────────────────────────────╯${NC}"
                echo
                docker logs --tail 50 "$CONTAINER_NAME" 2>/dev/null || {
                    warn "❌ Unable to retrieve logs"
                }
            else
                echo -e "${RED}🔴 Container is not running${NC}"
                echo -e "${YELLOW}💡 Try running: ${NC}${GREEN}dorstart${NC} ${YELLOW}to start the container${NC}"
            fi
            ;;
        "rebuild")
            # Show cool header for rebuild
            clear
            show_dor_header
            
            log "🔄 Rebuilding and redeploying DoR-Dash..."
            stop_existing
            
            # Clean removal of old image
            log "🗑️  Removing existing Docker image..."
            docker rmi "$IMAGE_NAME:latest" >/dev/null 2>&1 || true
            
            # Check if --no-cache was passed as second argument
            if [ "$2" = "--no-cache" ]; then
                build_image "--no-cache"
            else
                build_image
            fi
            
            run_container
            sleep 3
            
            # Final success display
            echo
            echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║${NC}            🎉 ${YELLOW}Deployment Complete!${NC}           ${GREEN}║${NC}"
            echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
            echo
            show_status
            ;;
        *)
            clear
            show_dor_header
            
            echo -e "${RED}╔══════════════════════════════════════╗${NC}"
            echo -e "${RED}║${NC}        ❓ ${YELLOW}Command Help${NC}            ${RED}║${NC}"
            echo -e "${RED}╚══════════════════════════════════════╝${NC}"
            echo
            
            echo -e "${YELLOW}Usage:${NC} $0 {deploy|stop|restart|status|logs|rebuild}"
            echo
            
            echo -e "${BLUE}╭─────────────────────────────────────────────────╮${NC}"
            echo -e "${BLUE}│${NC}                 🛠️  ${YELLOW}Available Commands${NC}            ${BLUE}│${NC}"
            echo -e "${BLUE}╰─────────────────────────────────────────────────╯${NC}"
            
            commands=(
                "🚀 ${GREEN}deploy${NC}   - Deploy the application (default)"
                "⏹️  ${RED}stop${NC}     - Stop the running container"
                "🔄 ${YELLOW}restart${NC}  - Restart the container"
                "📊 ${BLUE}status${NC}   - Show container status and access URLs"
                "📝 ${CYAN}logs${NC}     - Show container logs"
                "🔧 ${PURPLE}rebuild${NC}  - Rebuild image and redeploy [--no-cache]"
            )
            
            for cmd in "${commands[@]}"; do
                echo -e "  ${cmd}"
                sleep 0.1
            done
            
            echo
            echo -e "${YELLOW}💡 Pro Tip:${NC} Use ${GREEN}dorhelp${NC} to see all available DoR-Dash aliases!"
            exit 1
            ;;
    esac
}

main "$@"