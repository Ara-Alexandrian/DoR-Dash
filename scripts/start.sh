#!/bin/bash

# Simple DoR-Dash Startup Script

# Output styling
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}    Starting DoR-Dash Dashboard        ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Stop any running instances first
if [ -f "stop.sh" ]; then
    echo -e "${YELLOW}Stopping any existing instances...${NC}"
    ./stop.sh
    # Give processes time to terminate
    sleep 2
fi

# Ensure required directories exist
mkdir -p uploads logs
touch uploads/.gitkeep logs/.gitkeep

# Create appropriate .env file
echo -e "${YELLOW}Creating/updating configuration...${NC}"
cat > .env << EOF
# Database Configuration
POSTGRES_SERVER=172.30.98.213
POSTGRES_PORT=5432
POSTGRES_USER=DoRadmin
POSTGRES_PASSWORD=1232
POSTGRES_DB=DoR

# Redis Configuration
REDIS_SERVER=172.30.98.214
REDIS_PORT=6379

# JWT Settings
SECRET_KEY=insecure_default_key_for_development_only
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama API Configuration
OLLAMA_API_URL=http://172.30.98.14:11434/api/generate

# Application Configuration
BACKEND_HOST=172.30.98.21
BACKEND_PORT=8000
FRONTEND_HOST=172.30.98.21
FRONTEND_PORT=7117
EOF

# Copy .env to backend directory as well
cp .env backend/.env

# Create Python virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv $VENV_DIR
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

# Install backend requirements
echo -e "${BLUE}Installing backend requirements...${NC}"
cd backend
pip install -r requirements.txt
cd ..

# Start backend process - use 0.0.0.0 to bind to all interfaces
echo -e "${BLUE}Starting backend...${NC}"
cd backend
# Export PYTHONPATH to ensure imports work properly
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m uvicorn app.main:app --host 172.30.98.21 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo $BACKEND_PID > ./logs/backend.pid
echo -e "${GREEN}Backend started with PID $BACKEND_PID${NC}"
echo -e "${GREEN}Backend API is accessible at:${NC}"
echo -e "${GREEN}- http://172.30.98.21:8000${NC}"
echo -e "${YELLOW}Backend logs: ./logs/backend.log${NC}"

# Apply migrations (with better error handling)
echo -e "${YELLOW}Applying database migrations...${NC}"
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
alembic upgrade head || echo -e "${RED}Database migration failed. This is expected on first run.${NC}"
cd ..

# Start frontend server
echo -e "${BLUE}Starting frontend...${NC}"
cd frontend

# Create frontend .env file if it doesn't exist
cat > .env << EOF
VITE_API_URL=http://172.30.98.21:8000
EOF

# Install frontend dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    # Use --no-cache option to avoid npm cache permission issues
    npm install --no-cache || echo -e "${YELLOW}Failed to install dependencies, but continuing...${NC}"
fi

# Start the frontend development server
npm run dev -- --host 172.30.98.21 --port 7117 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > ./logs/frontend.pid
echo -e "${GREEN}Frontend started with PID $FRONTEND_PID${NC}"
echo -e "${GREEN}Frontend is accessible at:${NC}"
echo -e "${GREEN}- http://172.30.98.21:7117${NC}"
echo -e "${YELLOW}Frontend logs: ./logs/frontend.log${NC}"

echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}DoR-Dash is now running!${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "Backend API: ${GREEN}http://172.30.98.21:8000${NC}"
echo -e "Frontend App: ${GREEN}http://172.30.98.21:7117${NC}"
echo -e "To stop the application: ${YELLOW}./stop.sh${NC}"
echo -e "${BLUE}=======================================${NC}"

# Show instructions for connecting to PostgreSQL
echo -e "${YELLOW}PostgreSQL Connection Information:${NC}"
echo -e "Server: ${GREEN}172.30.98.213:5432${NC}"
echo -e "Database: ${GREEN}DoR${NC}"
echo -e "Username: ${GREEN}DoRadmin${NC}"
echo -e "Password: ${GREEN}1232${NC}"

# Keep the script running to maintain the environment variables
echo -e "${YELLOW}Press Ctrl+C to exit this script (services will keep running)${NC}"