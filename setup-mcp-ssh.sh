#!/bin/bash

# Setup script for MCP SSH servers
# This script installs the necessary dependencies and configures MCP SSH servers

echo "Setting up MCP SSH servers for DoR-Dash containers..."

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# Install MCP server packages
echo "Installing MCP server packages..."
npm install -g @modelcontextprotocol/server-ssh
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-redis
npm install -g @modelcontextprotocol/server-mermaid
npm install -g @modelcontextprotocol/server-github

# Create SSH key directory if it doesn't exist
mkdir -p ~/.ssh

# Generate SSH keys for passwordless authentication (optional)
echo "Generating SSH keys for containers..."
for container in dor-dash postgres-db redis-cache ollama-server; do
    if [ ! -f ~/.ssh/id_rsa_${container} ]; then
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_${container} -N "" -C "mcp-${container}@localhost"
        echo "Generated SSH key for ${container}"
    fi
done

# Create known_hosts entries
echo "Adding containers to known_hosts..."
ssh-keyscan -H 172.30.98.177 >> ~/.ssh/known_hosts 2>/dev/null
ssh-keyscan -H 172.30.98.213 >> ~/.ssh/known_hosts 2>/dev/null
ssh-keyscan -H 172.30.98.214 >> ~/.ssh/known_hosts 2>/dev/null
ssh-keyscan -H 172.30.98.14 >> ~/.ssh/known_hosts 2>/dev/null

echo "MCP SSH server setup complete!"
echo ""
echo "To use the MCP SSH servers:"
echo "1. Make sure Claude Code has access to the mcp-servers.json file"
echo "2. The SSH configurations are in:"
echo "   - ssh-config.json (DoR-Dash container)"
echo "   - ssh-postgres-config.json (PostgreSQL container)"
echo "   - ssh-redis-config.json (Redis container)"
echo "   - ssh-ollama-config.json (Ollama container)"
echo ""
echo "To test SSH connectivity:"
echo "ssh root@172.30.98.177  # DoR-Dash container"
echo ""
echo "Note: Other containers may need SSH server installation first."