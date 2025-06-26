# MCP SSH Server Setup for DoR-Dash Containers

## Overview
This guide explains how to set up Model Context Protocol (MCP) SSH servers to access containers on the same subnet (172.30.98.0/24) as the DoR-Dash application.

## Container Network Architecture

The DoR-Dash infrastructure runs on the following containers:

| Container | IP Address | Port | Purpose |
|-----------|------------|------|---------|
| DoR-Dash | 172.30.98.177 | 22 | Main application container (SSH enabled) |
| PostgreSQL | 172.30.98.213 | 5432 | Database server |
| Redis | 172.30.98.214 | 6379 | Cache server |
| Ollama | 172.30.98.14 | 11434 | AI/LLM server |

## MCP Configuration Files

### 1. Main MCP Server Configuration (`mcp-servers.json`)
This file defines all MCP servers available for the DoR-Dash project:

**SSH Servers:**
- `ssh-dor-dash`: SSH access to the main DoR-Dash container
- `ssh-postgres`: SSH access to PostgreSQL container (if SSH is enabled)
- `ssh-redis`: SSH access to Redis container (if SSH is enabled)
- `ssh-ollama`: SSH access to Ollama container (if SSH is enabled)

**Direct Connection Servers:**
- `postgres`: Direct PostgreSQL database connection for queries
- `redis`: Direct Redis cache connection for monitoring
- `puppeteer`: Visual testing and UI validation server (NEW)
- `mermaid`: Diagram generation and validation server
- `github`: GitHub repository integration for code management

### 2. SSH Configuration Files
Each container has its own SSH configuration file:
- `ssh-config.json`: DoR-Dash container (root and dor-user access)
- `ssh-postgres-config.json`: PostgreSQL container configuration
- `ssh-redis-config.json`: Redis container configuration
- `ssh-ollama-config.json`: Ollama container configuration

## Setup Instructions

### Prerequisites
1. Node.js and npm installed
2. SSH client available
3. Network access to 172.30.98.0/24 subnet

### Installation Steps

1. **Run the setup script**:
   ```bash
   ./setup-mcp-ssh.sh
   ```

2. **Configure Claude Code**:
   - Ensure Claude Code has access to the `mcp-servers.json` file
   - The MCP servers will be automatically available in Claude Code

3. **Test SSH connectivity**:
   ```bash
   # Test DoR-Dash container
   ssh root@172.30.98.177
   # Password: dor-ssh-password-2024
   
   # Or as regular user
   ssh dor-user@172.30.98.177
   # Password: dor-user-password-2024
   ```

## Usage in Claude Code

Once configured, you can use the MCP SSH servers in Claude Code:

1. **Access DoR-Dash container**:
   - Use the `ssh-dor-dash` MCP server
   - Execute commands, check logs, manage services

2. **Database operations** (if SSH enabled on PostgreSQL):
   - Use the `ssh-postgres` MCP server
   - Run database queries, check connections

3. **Cache operations** (if SSH enabled on Redis):
   - Use the `ssh-redis` MCP server
   - Monitor cache performance, clear cache

4. **AI/LLM operations** (if SSH enabled on Ollama):
   - Use the `ssh-ollama` MCP server
   - Check model status, test prompts

## Security Considerations

### Important Security Notes
1. **Change default passwords immediately** in production
2. **Use SSH keys** instead of passwords for better security
3. **Restrict SSH access** to specific IP addresses if possible
4. **Disable root SSH** after initial setup

### Setting up SSH Key Authentication

1. **Generate SSH keys** (done by setup script):
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_dor-dash
   ```

2. **Copy keys to containers**:
   ```bash
   ssh-copy-id -i ~/.ssh/id_rsa_dor-dash root@172.30.98.177
   ```

3. **Update SSH config** to use key authentication:
   ```json
   {
     "hosts": [{
       "name": "dor-dash",
       "hostname": "172.30.98.177",
       "port": 22,
       "username": "root",
       "identityFile": "~/.ssh/id_rsa_dor-dash"
     }]
   }
   ```

## Troubleshooting

### Common Issues

1. **Connection refused**:
   - Verify container is running: `docker ps`
   - Check if SSH is installed in the container
   - Verify firewall rules allow SSH (port 22)

2. **Authentication failed**:
   - Verify username and password
   - Check if password authentication is enabled
   - Try using SSH keys instead

3. **MCP server not found**:
   - Ensure `@modelcontextprotocol/server-ssh` is installed
   - Check the path to configuration files
   - Verify JSON syntax in configuration files

### Enabling SSH on Other Containers

For containers without SSH (PostgreSQL, Redis, Ollama), you'll need to:

1. **Install SSH server** in the container:
   ```bash
   docker exec -it <container-name> /bin/bash
   apt-get update && apt-get install -y openssh-server
   ```

2. **Configure SSH**:
   ```bash
   # Set root password
   passwd root
   
   # Enable root login (for development only)
   sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
   
   # Start SSH service
   service ssh start
   ```

3. **Make SSH persistent** by adding to container startup

## Advanced Configuration

### Custom SSH Options
You can add custom SSH options to the configuration:

```json
{
  "hosts": [{
    "name": "dor-dash",
    "hostname": "172.30.98.177",
    "port": 22,
    "username": "root",
    "strictHostKeyChecking": "no",
    "compression": true,
    "serverAliveInterval": 60
  }]
}
```

### Multiple Environments
Create separate configuration files for different environments:
- `ssh-config-dev.json`: Development containers
- `ssh-config-prod.json`: Production containers
- `ssh-config-test.json`: Test containers

## Integration with DoR-Dash Agents

The MCP SSH servers can be used by DoR-Dash agents for:
- **QA Agent**: Run tests directly on containers
- **Database Agent**: Execute SQL queries via SSH
- **Website Testing Agent**: Check application health
- **Repository Agent**: Manage git operations

Example agent usage:
```bash
# In QA Agent
Task(description="SSH test", prompt="Use ssh-dor-dash MCP to check application health")
```

## Maintenance

### Regular Tasks
1. **Update passwords** quarterly
2. **Rotate SSH keys** annually
3. **Review access logs** monthly
4. **Update MCP server package** as needed

### Backup Configuration
Keep backups of:
- SSH keys
- Configuration files
- Known hosts entries
- Custom scripts

## References
- [MCP Documentation](https://modelcontextprotocol.io)
- [SSH Best Practices](https://www.ssh.com/academy/ssh/best-practices)
- [DoR-Dash SSH Access Guide](SSH_ACCESS.md)