#!/bin/bash

# Cerebro-Stack Development Start Script
# This script starts all development services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle cleanup on exit
cleanup() {
    log_info "Shutting down services..."
    
    # Kill background processes
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Stop Docker services
    if [ -f "docker-compose.dev.yml" ]; then
        docker-compose -f docker-compose.dev.yml down
    elif [ -f "docker-compose.yml" ]; then
        docker-compose down
    fi
    
    log_success "Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Load environment variables
load_environment() {
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
        log_success "Environment variables loaded"
    else
        log_warning "No .env file found. Using default values."
    fi
}

# Start Docker services
start_docker_services() {
    log_info "Starting Docker services..."
    
    if [ -f "docker-compose.dev.yml" ]; then
        docker-compose -f docker-compose.dev.yml up -d postgres redis
        log_success "Docker services started (postgres, redis)"
    elif [ -f "docker-compose.yml" ]; then
        docker-compose up -d postgres redis
        log_success "Docker services started (postgres, redis)"
    else
        log_warning "No Docker Compose file found. Skipping Docker services."
        return
    fi
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 5
    
    # Check if services are healthy
    if command_exists docker-compose; then
        if [ -f "docker-compose.dev.yml" ]; then
            COMPOSE_FILE="docker-compose.dev.yml"
        else
            COMPOSE_FILE="docker-compose.yml"
        fi
        
        # Check PostgreSQL
        if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
            log_success "PostgreSQL is ready"
        else
            log_warning "PostgreSQL might not be ready yet"
        fi
        
        # Check Redis
        if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping >/dev/null 2>&1; then
            log_success "Redis is ready"
        else
            log_warning "Redis might not be ready yet"
        fi
    fi
}

# Start backend service
start_backend() {
    log_info "Starting backend service..."
    
    if [ ! -d "backend" ]; then
        log_warning "No backend directory found, skipping backend startup"
        return
    fi
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_error "Virtual environment not found. Please run ./scripts/setup.sh first"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run database migrations
    if [ -f "alembic.ini" ]; then
        log_info "Running database migrations..."
        alembic upgrade head
        log_success "Database migrations completed"
    fi
    
    # Start the backend server
    log_info "Starting FastAPI server..."
    
    # Check if uvicorn is available
    if command_exists uvicorn; then
        # Get port from environment or use default
        BACKEND_PORT=${PORT:-8000}
        BACKEND_HOST=${HOST:-127.0.0.1}
        
        # Start server in background
        uvicorn app.main:app --reload --host $BACKEND_HOST --port $BACKEND_PORT &
        BACKEND_PID=$!
        
        log_success "Backend started on http://$BACKEND_HOST:$BACKEND_PORT"
        log_info "API Documentation: http://$BACKEND_HOST:$BACKEND_PORT/docs"
    else
        log_error "uvicorn not found. Please install backend dependencies"
        exit 1
    fi
    
    deactivate
    cd ..
}

# Start frontend service
start_frontend() {
    log_info "Starting frontend service..."
    
    if [ ! -d "frontend" ]; then
        log_warning "No frontend directory found, skipping frontend startup"
        return
    fi
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_error "node_modules not found. Please run ./scripts/setup.sh first"
        exit 1
    fi
    
    # Start the frontend development server
    log_info "Starting development server..."
    
    # Determine which dev script to use
    if command_exists npm && [ -f "package.json" ]; then
        if npm run --silent 2>/dev/null | grep -q "dev"; then
            npm run dev &
            FRONTEND_PID=$!
            log_success "Frontend started with npm run dev"
        elif npm run --silent 2>/dev/null | grep -q "start"; then
            npm run start &
            FRONTEND_PID=$!
            log_success "Frontend started with npm run start"
        else
            log_error "No dev or start script found in package.json"
            exit 1
        fi
    elif command_exists yarn && [ -f "package.json" ]; then
        yarn dev &
        FRONTEND_PID=$!
        log_success "Frontend started with yarn dev"
    elif command_exists pnpm && [ -f "package.json" ]; then
        pnpm dev &
        FRONTEND_PID=$!
        log_success "Frontend started with pnpm dev"
    else
        log_error "No package manager found or package.json missing"
        exit 1
    fi
    
    cd ..
}

# Check service health
check_services() {
    log_info "Checking service health..."
    
    # Wait a moment for services to start
    sleep 3
    
    # Check backend health
    BACKEND_PORT=${PORT:-8000}
    BACKEND_HOST=${HOST:-127.0.0.1}
    
    if curl -s "http://$BACKEND_HOST:$BACKEND_PORT/health" >/dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_warning "Backend health check failed or backend not ready yet"
    fi
    
    # Check frontend (usually runs on port 3000 or 5173)
    for port in 3000 5173 4173; do
        if curl -s "http://localhost:$port" >/dev/null 2>&1; then
            log_success "Frontend accessible on port $port"
            break
        fi
    done
}

# Print service information
print_service_info() {
    echo ""
    echo "🎉 Development environment started successfully!"
    echo ""
    echo "Services:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Backend info
    BACKEND_PORT=${PORT:-8000}
    BACKEND_HOST=${HOST:-127.0.0.1}
    echo "🔗 Backend API:      http://$BACKEND_HOST:$BACKEND_PORT"
    echo "📚 API Docs:         http://$BACKEND_HOST:$BACKEND_PORT/docs"
    echo "🔍 Interactive API:  http://$BACKEND_HOST:$BACKEND_PORT/redoc"
    
    # Frontend info (try to detect port)
    for port in 3000 5173 4173; do
        if curl -s "http://localhost:$port" >/dev/null 2>&1; then
            echo "🌐 Frontend:         http://localhost:$port"
            break
        fi
    done
    
    # Database info
    if command_exists docker-compose; then
        if [ -f "docker-compose.dev.yml" ] || [ -f "docker-compose.yml" ]; then
            echo "🗄️  PostgreSQL:       localhost:5432"
            echo "🔴 Redis:            localhost:6379"
        fi
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 Logs:"
    echo "   - Backend logs will appear below"
    echo "   - Frontend logs in separate terminal if needed"
    echo ""
    echo "🛑 To stop all services, press Ctrl+C"
    echo ""
}

# Monitor services
monitor_services() {
    log_info "Monitoring services... Press Ctrl+C to stop"
    
    while true; do
        # Check if background processes are still running
        if [ ! -z "$BACKEND_PID" ] && ! kill -0 $BACKEND_PID 2>/dev/null; then
            log_error "Backend process died unexpectedly"
            break
        fi
        
        if [ ! -z "$FRONTEND_PID" ] && ! kill -0 $FRONTEND_PID 2>/dev/null; then
            log_error "Frontend process died unexpectedly"
            break
        fi
        
        sleep 5
    done
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                START_BACKEND_ONLY=true
                shift
                ;;
            --frontend-only)
                START_FRONTEND_ONLY=true
                shift
                ;;
            --no-docker)
                NO_DOCKER=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --backend-only    Start only the backend service"
                echo "  --frontend-only   Start only the frontend service"
                echo "  --no-docker       Skip starting Docker services"
                echo "  --help, -h        Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Main function
main() {
    echo "🚀 Starting Cerebro-Stack Development Environment..."
    echo ""
    
    # Parse command line arguments
    parse_args "$@"
    
    # Load environment
    load_environment
    
    # Start services based on arguments
    if [ "$NO_DOCKER" != "true" ]; then
        start_docker_services
    fi
    
    if [ "$START_FRONTEND_ONLY" == "true" ]; then
        start_frontend
    elif [ "$START_BACKEND_ONLY" == "true" ]; then
        start_backend
    else
        start_backend
        start_frontend
    fi
    
    # Check service health
    check_services
    
    # Print service information
    print_service_info
    
    # Monitor services
    monitor_services
}

# Run main function with all arguments
main "$@"