#!/bin/bash

# Production DoR-Dash Startup Script for Port 1717

# Output styling
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}  Starting DoR-Dash (Production Mode)  ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Kill any existing processes on port 1717
echo -e "${YELLOW}Stopping any existing processes on port 1717...${NC}"
pkill -f "port.*1717" || true
sleep 2

# Ensure required directories exist
mkdir -p uploads logs
touch uploads/.gitkeep logs/.gitkeep

# Build the frontend for production
echo -e "${BLUE}Building frontend for production...${NC}"
cd frontend
npm run build

# Start the production frontend server on port 1717
echo -e "${BLUE}Starting production frontend server on port 1717...${NC}"
nohup npm run serve -- --host 172.30.98.21 --port 1717 > ../logs/frontend-prod.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > ./logs/frontend-prod.pid

echo -e "${GREEN}Production frontend started with PID $FRONTEND_PID${NC}"
echo -e "${GREEN}Frontend is now accessible at:${NC}"
echo -e "${GREEN}- http://172.30.98.21:1717${NC}"
echo -e "${GREEN}- https://dd.kronisto.net (via reverse proxy)${NC}"
echo -e "${YELLOW}Frontend logs: ./logs/frontend-prod.log${NC}"

echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}Production frontend is now running!${NC}"
echo -e "${BLUE}=======================================${NC}"
echo -e "Production Frontend: ${GREEN}http://172.30.98.21:1717${NC}"
echo -e "Backend API: ${GREEN}http://172.30.98.21:8000${NC}"
echo -e "Public URL: ${GREEN}https://dd.kronisto.net${NC}"
echo -e "${BLUE}=======================================${NC}"