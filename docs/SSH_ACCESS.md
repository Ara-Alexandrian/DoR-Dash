# SSH Access to DoR-Dash Container

## Overview
The DoR-Dash Docker container now includes SSH access for remote management and debugging.

## Connection Details
- **Host**: 172.30.98.177
- **Port**: 22
- **Users**: 
  - `root` (full access)
  - `dor-user` (sudo access)

## Default Credentials
⚠️ **SECURITY NOTE**: Change these passwords immediately in production!

- **Root user**: 
  - Username: `root`
  - Password: `dor-ssh-password-2024`

- **Regular user**:
  - Username: `dor-user` 
  - Password: `dor-user-password-2024`

## Connecting via SSH

### From command line:
```bash
# Connect as root
ssh root@172.30.98.177

# Connect as regular user
ssh dor-user@172.30.98.177
```

### From SSH client:
- Host: 172.30.98.177
- Port: 22
- Username: root or dor-user
- Password: (see above)

## Security Recommendations

### 1. Change Default Passwords
After first login, change the passwords:
```bash
# Change root password
passwd

# Change dor-user password (as root)
passwd dor-user
```

### 2. Setup SSH Key Authentication (Recommended)
```bash
# On your local machine, generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key to container
ssh-copy-id root@172.30.98.177
ssh-copy-id dor-user@172.30.98.177

# Disable password authentication (optional, for security)
# Edit /etc/ssh/sshd_config and set:
# PasswordAuthentication no
# Then restart SSH: service ssh restart
```

### 3. Firewall Configuration
Ensure your firewall allows SSH connections to 172.30.98.177:22

## Container Management via SSH

### Check Application Status
```bash
# Check running processes
ps aux | grep -E "(uvicorn|serve|node)"

# Check application logs
tail -f /app/logs/backend.log
tail -f /app/logs/frontend.log

# Check container health
curl -f http://localhost:8000/health
```

### Application File Locations
- **Backend**: `/app/backend/`
- **Frontend**: `/app/frontend/build/`
- **Logs**: `/app/logs/`
- **Uploads**: `/app/uploads/`
- **Entry Script**: `/app/docker-entrypoint.sh`

### Restart Services
```bash
# Full container restart
exit  # then restart container from host

# Individual service restart (advanced)
# Find PIDs: cat /tmp/backend.pid /tmp/frontend.pid
# Kill processes and restart manually
```

## Troubleshooting

### SSH Connection Issues
1. Verify container is running: `docker ps`
2. Check port mapping: `docker port dor-dash`
3. Test connectivity: `telnet 172.30.98.177 22`
4. Check SSH service: `docker exec dor-dash service ssh status`

### Application Issues
1. Check logs: `tail -f /app/logs/*.log`
2. Check process status: `ps aux`
3. Check network connectivity: `curl localhost:8000/health`

## Building with SSH Support

The SSH functionality is automatically included when building the container:

```bash
# Build the container
docker-compose -f docker/docker-compose.prod.yml build

# Start with SSH access
docker-compose -f docker/docker-compose.prod.yml up -d
```

## Notes
- SSH service starts automatically with the container
- SSH access is bound specifically to IP 172.30.98.177
- Both root and sudo access are available
- Container includes standard Linux tools (git, curl, etc.)