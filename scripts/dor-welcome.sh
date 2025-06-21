#!/bin/bash

# DoR-Dash Welcome Animation Script

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Animation function
typewriter() {
    local text="$1"
    local delay="${2:-0.05}"
    
    for ((i=0; i<${#text}; i++)); do
        printf "${text:$i:1}"
        sleep "$delay"
    done
    echo
}

# Animated DoR-Dash logo
show_animated_logo() {
    clear
    echo -e "${CYAN}"
    typewriter "     ____        ____        ____            _     " 0.02
    typewriter "    |  _ \  ___ |  _ \      |  _ \  __ _ ___| |__  " 0.02
    typewriter "    | | | |/ _ \| |_) |_____| | | |/ _` / __| '_ \ " 0.02
    typewriter "    | |_| | (_) |  _ <______| |_| | (_| \__ \ | | |" 0.02
    typewriter "    |____/ \___/|_| \_\     |____/ \__,_|___/_| |_|" 0.02
    echo -e "${NC}"
    
    sleep 1
    
    echo -e "${YELLOW}"
    typewriter "           🏥 Mary Bird Perkins Research Dashboard" 0.03
    echo -e "${NC}"
    
    sleep 1
    
    # Animated underline
    echo -ne "${BLUE}"
    for i in {1..50}; do
        echo -n "═"
        sleep 0.02
    done
    echo -e "${NC}"
    echo
}

# Command showcase
show_commands() {
    echo -e "${GREEN}🚀 Available Commands:${NC}"
    echo
    
    commands=(
        "dorsmartrebuild  - ⚡ Fast rebuild with cache (RECOMMENDED)"
        "dorforcebuild    - 🔥 Force rebuild (slow but thorough)"
        "dorupdate        - 🔄 Quick restart (for small changes)"
        "dorstatus        - 📊 Show system status"
        "dorlogs          - 📝 View live logs"
        "dorexec          - 🔧 SSH into container"
        "dorhealth        - 💓 Health check"
        "dorstop          - ⏹️  Stop container"
        "dorstart         - ▶️  Start container"
        "dorhelp          - ❓ Show all commands"
    )
    
    for cmd in "${commands[@]}"; do
        echo -e "${BLUE}  ${cmd}${NC}"
        sleep 0.2
    done
    
    echo
}

# Main welcome sequence
main() {
    show_animated_logo
    
    echo -e "${PURPLE}🎉 Welcome to DoR-Dash! 🎉${NC}"
    echo
    typewriter "The Mary Bird Perkins Research Management System is ready!" 0.04
    echo
    
    show_commands
    
    echo -e "${CYAN}╭────────────────────────────────────────────────╮${NC}"
    echo -e "${CYAN}│${NC}                🌟 ${YELLOW}Quick Start${NC}                  ${CYAN}│${NC}"
    echo -e "${CYAN}╰────────────────────────────────────────────────╯${NC}"
    echo -e "${GREEN}1.${NC} Run ${YELLOW}dorsmartrebuild${NC} to deploy the application"
    echo -e "${GREEN}2.${NC} Visit ${YELLOW}https://dd.kronisto.net${NC} to access the frontend"
    echo -e "${GREEN}3.${NC} Login with ${YELLOW}cerebro / 123${NC} (admin) or ${YELLOW}aalexandrian / 12345678${NC} (faculty)"
    echo
    
    echo -e "${BLUE}╭────────────────────────────────────────────────╮${NC}"
    echo -e "${BLUE}│${NC}               💡 ${YELLOW}Pro Tips${NC}                     ${BLUE}│${NC}"
    echo -e "${BLUE}╰────────────────────────────────────────────────╯${NC}"
    echo -e "${CYAN}•${NC} Use ${YELLOW}dorsmartrebuild${NC} for daily development (fastest)"
    echo -e "${CYAN}•${NC} Use ${YELLOW}dorforcebuild${NC} only when dependencies change"
    echo -e "${CYAN}•${NC} Run ${YELLOW}dorstatus${NC} anytime to check system health"
    echo -e "${CYAN}•${NC} Use ${YELLOW}dorlogs${NC} to monitor real-time activity"
    echo
    
    # Animated footer
    echo -ne "${GREEN}"
    for i in {1..50}; do
        echo -n "─"
        sleep 0.01
    done
    echo -e "${NC}"
    
    echo -e "${PURPLE}Ready to build something amazing! 🚀${NC}"
    echo
}

main "$@"