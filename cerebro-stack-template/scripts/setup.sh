#!/bin/bash

# Cerebro-Stack Project Setup Script
# This script sets up the development environment for the project

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

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version | sed 's/v//')
        REQUIRED_NODE_VERSION="18.0.0"
        if [ "$(printf '%s\n' "$REQUIRED_NODE_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_NODE_VERSION" ]; then
            log_success "Node.js $NODE_VERSION is installed"
        else
            log_error "Node.js $REQUIRED_NODE_VERSION or higher is required. Found: $NODE_VERSION"
            exit 1
        fi
    else
        log_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        REQUIRED_PYTHON_VERSION="3.11.0"
        if [ "$(printf '%s\n' "$REQUIRED_PYTHON_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_PYTHON_VERSION" ]; then
            log_success "Python $PYTHON_VERSION is installed"
        else
            log_error "Python $REQUIRED_PYTHON_VERSION or higher is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 is not installed. Please install Python 3.11+ from https://python.org/"
        exit 1
    fi
    
    # Check Docker
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
        log_success "Docker $DOCKER_VERSION is installed"
    else
        log_warning "Docker is not installed. Some features may not work without Docker."
        log_info "You can install Docker from https://docker.com/"
    fi
    
    # Check Docker Compose
    if command_exists docker-compose || command_exists "docker compose"; then
        log_success "Docker Compose is available"
    else
        log_warning "Docker Compose is not installed. Some features may not work without Docker Compose."
    fi
    
    # Check Git
    if command_exists git; then
        GIT_VERSION=$(git --version | awk '{print $3}')
        log_success "Git $GIT_VERSION is installed"
    else
        log_error "Git is not installed. Please install Git from https://git-scm.com/"
        exit 1
    fi
}

# Setup environment files
setup_environment() {
    log_info "Setting up environment files..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env file from .env.example"
            log_warning "Please edit .env file with your specific configuration"
        else
            log_info "Creating basic .env file..."
            cat > .env << 'EOF'
# Application Environment
NODE_ENV=development
DEBUG=true
PORT=8000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/development_db
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=development-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_CREDENTIALS=true

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,jpg,jpeg,png,gif

# Logging
LOG_LEVEL=DEBUG
EOF
            log_success "Created basic .env file"
            log_warning "Please edit .env file with your specific configuration"
        fi
    else
        log_info ".env file already exists"
    fi
}

# Install frontend dependencies
setup_frontend() {
    log_info "Setting up frontend dependencies..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        # Check if package.json exists
        if [ -f "package.json" ]; then
            # Install dependencies
            if command_exists npm; then
                npm install
                log_success "Frontend dependencies installed with npm"
            elif command_exists yarn; then
                yarn install
                log_success "Frontend dependencies installed with yarn"
            elif command_exists pnpm; then
                pnpm install
                log_success "Frontend dependencies installed with pnpm"
            else
                log_error "No package manager found. Please install npm, yarn, or pnpm"
                exit 1
            fi
        else
            log_warning "No package.json found in frontend directory"
        fi
        
        cd ..
    else
        log_info "No frontend directory found, skipping frontend setup"
    fi
}

# Install backend dependencies
setup_backend() {
    log_info "Setting up backend dependencies..."
    
    if [ -d "backend" ]; then
        cd backend
        
        # Create virtual environment
        if [ ! -d "venv" ]; then
            log_info "Creating Python virtual environment..."
            python3 -m venv venv
            log_success "Virtual environment created"
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Upgrade pip
        pip install --upgrade pip
        
        # Install dependencies
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
            log_success "Backend dependencies installed"
        elif [ -f "pyproject.toml" ]; then
            pip install -e .
            log_success "Backend dependencies installed from pyproject.toml"
        else
            log_warning "No requirements.txt or pyproject.toml found in backend directory"
        fi
        
        # Install development dependencies
        if [ -f "requirements-dev.txt" ]; then
            pip install -r requirements-dev.txt
            log_success "Development dependencies installed"
        fi
        
        deactivate
        cd ..
    else
        log_info "No backend directory found, skipping backend setup"
    fi
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    if command_exists docker && command_exists docker-compose; then
        # Start database services
        if [ -f "docker-compose.dev.yml" ]; then
            docker-compose -f docker-compose.dev.yml up -d postgres redis
            log_success "Database services started"
            
            # Wait for database to be ready
            log_info "Waiting for database to be ready..."
            sleep 5
            
            # Run migrations if backend exists
            if [ -d "backend" ]; then
                cd backend
                source venv/bin/activate
                
                # Check if Alembic is configured
                if [ -f "alembic.ini" ]; then
                    alembic upgrade head
                    log_success "Database migrations applied"
                else
                    log_info "No Alembic configuration found, skipping migrations"
                fi
                
                deactivate
                cd ..
            fi
        elif [ -f "docker-compose.yml" ]; then
            docker-compose up -d postgres redis
            log_success "Database services started"
        else
            log_warning "No Docker Compose file found. Please set up database manually."
        fi
    else
        log_warning "Docker not available. Please set up PostgreSQL and Redis manually."
        log_info "PostgreSQL: https://postgresql.org/download/"
        log_info "Redis: https://redis.io/download"
    fi
}

# Setup Git hooks
setup_git_hooks() {
    log_info "Setting up Git hooks..."
    
    # Install pre-commit if available
    if [ -f ".pre-commit-config.yaml" ]; then
        if command_exists pre-commit; then
            pre-commit install
            log_success "Pre-commit hooks installed"
        else
            log_info "Installing pre-commit..."
            if command_exists pip; then
                pip install pre-commit
                pre-commit install
                log_success "Pre-commit installed and hooks configured"
            else
                log_warning "Cannot install pre-commit. Please install manually: pip install pre-commit"
            fi
        fi
    else
        log_info "No pre-commit configuration found"
    fi
    
    # Setup commit message template
    if [ -f ".gitmessage" ]; then
        git config commit.template .gitmessage
        log_success "Git commit message template configured"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    # Create upload directory
    mkdir -p uploads
    log_success "Upload directory created"
    
    # Create logs directory
    mkdir -p logs
    log_success "Logs directory created"
    
    # Create temp directory
    mkdir -p temp
    log_success "Temp directory created"
}

# Verify setup
verify_setup() {
    log_info "Verifying setup..."
    
    # Check if services are running
    if command_exists docker && [ -f "docker-compose.dev.yml" ]; then
        if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
            log_success "Services are running"
        else
            log_warning "Some services might not be running properly"
        fi
    fi
    
    # Check if we can connect to database
    if [ -d "backend" ]; then
        cd backend
        if [ -d "venv" ]; then
            source venv/bin/activate
            
            # Try to run a simple database check
            if python -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/development_db'))
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️  Database connection failed: {e}')
" 2>/dev/null; then
                :
            fi
            
            deactivate
        fi
        cd ..
    fi
}

# Print next steps
print_next_steps() {
    log_success "Setup completed successfully! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Review and update the .env file with your configuration"
    echo "2. Start the development servers:"
    echo "   ./scripts/start.sh"
    echo ""
    echo "3. Visit your application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "4. Run tests:"
    echo "   ./scripts/run-tests.sh"
    echo ""
    echo "For more information, see the documentation in the docs/ directory."
}

# Main setup function
main() {
    echo "🚀 Setting up Cerebro-Stack Project..."
    echo ""
    
    check_requirements
    setup_environment
    create_directories
    setup_frontend
    setup_backend
    setup_database
    setup_git_hooks
    verify_setup
    
    echo ""
    print_next_steps
}

# Run main function
main "$@"