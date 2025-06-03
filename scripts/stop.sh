#!/bin/bash

# Simple DoR-Dash Stop Script
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}      Stopping DoR-Dash Dashboard      ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Stop backend (if running)
if [ -f "./logs/backend.pid" ]; then
    BACKEND_PID=$(cat ./logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}Backend stopped (PID $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}Backend process not found${NC}"
    fi
    rm -f ./logs/backend.pid
fi

# Stop frontend (if running)
if [ -f "./logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat ./logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo -e "${GREEN}Frontend stopped (PID $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}Frontend process not found${NC}"
    fi
    rm -f ./logs/frontend.pid
fi

# Kill any lingering processes
echo -e "${YELLOW}Checking for lingering processes...${NC}"

# Find and kill uvicorn processes
UVICORN_PIDS=$(pgrep -f "uvicorn app.main:app")
if [ ! -z "$UVICORN_PIDS" ]; then
    echo -e "${YELLOW}Killing uvicorn processes...${NC}"
    kill $UVICORN_PIDS 2>/dev/null
fi

# Find and kill vite/frontend processes
VITE_PIDS=$(pgrep -f "vite.*--host")
if [ ! -z "$VITE_PIDS" ]; then
    echo -e "${YELLOW}Killing vite/frontend processes...${NC}"
    kill $VITE_PIDS 2>/dev/null
fi

echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}DoR-Dash stopped successfully${NC}"
echo -e "${BLUE}=======================================${NC}"

exit 0