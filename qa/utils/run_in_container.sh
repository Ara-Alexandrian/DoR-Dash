#!/bin/bash
# Utility script to run commands in the DoR-Dash container

CONTAINER_HOST="172.30.98.177"
CONTAINER_USER="root"

# Function to run a command in the container
run_command() {
    ssh -q -o LogLevel=ERROR -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
        ${CONTAINER_USER}@${CONTAINER_HOST} "$@"
}

# Function to copy a file to the container
copy_to_container() {
    local source=$1
    local dest=$2
    cat "$source" | ssh -q -o LogLevel=ERROR -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
        ${CONTAINER_USER}@${CONTAINER_HOST} "cat > $dest"
}

# Main logic
case "$1" in
    "check-db")
        echo "Checking database state..."
        copy_to_container "qa/database/check_db_state.py" "/tmp/check_db_state.py"
        run_command "cd /app/backend && python /tmp/check_db_state.py"
        ;;
    "run")
        shift
        run_command "$@"
        ;;
    *)
        echo "Usage: $0 {check-db|run <command>}"
        exit 1
        ;;
esac