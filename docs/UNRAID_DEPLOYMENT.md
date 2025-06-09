# DoR-Dash Unraid Deployment Guide

This guide explains how to deploy DoR-Dash as a Docker container on Unraid with auto-update functionality and nginx reverse proxy setup.

## 🚀 Quick Start

1. **Clone the repository on your Unraid server:**
   ```bash
   cd /mnt/user/appdata/
   git clone https://git.kronisto.net/test-host/DoR-Dash.git
   cd DoR-Dash
   git checkout revision
   ```

2. **Deploy the application:**
   ```bash
   ./deploy.sh deploy
   ```

3. **Access the application:**
   - Frontend: `http://172.30.98.177:1717`
   - Backend API: `http://172.30.98.177:1718`
   - Health Check: `http://172.30.98.177:1718/health`

## 📋 System Requirements

- **Unraid 6.8+** or any Docker-compatible system
- **Docker Engine** with BuildKit support
- **Network Access** to:
  - PostgreSQL: `172.30.98.213:5432`
  - Redis: `172.30.98.214:6379`
  - Ollama API: `172.30.98.14:11434`
  - Git Repository: `git.kronisto.net`

## 🔧 Configuration

### Environment Variables

The container accepts the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_SERVER` | `172.30.98.213` | PostgreSQL server IP |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `DoRadmin` | Database username |
| `POSTGRES_PASSWORD` | `1232` | Database password |
| `POSTGRES_DB` | `DoR` | Database name |
| `REDIS_SERVER` | `172.30.98.214` | Redis server IP |
| `REDIS_PORT` | `6379` | Redis port |
| `SECRET_KEY` | `insecure_default_key_for_development_only` | JWT secret |
| `OLLAMA_API_URL` | `http://172.30.98.14:11434/api/generate` | Ollama API endpoint |
| `AUTO_UPDATE` | `true` | Enable auto-updates |
| `REPO_URL` | `https://git.kronisto.net/test-host/DoR-Dash.git` | Git repository URL |
| `BRANCH` | `master` | Git branch to track |
| `UPDATE_CHECK_INTERVAL` | `300` | Update check interval (seconds) |

### Ports

- **1717**: Frontend application
- **1718**: Backend API (for nginx reverse proxy)

### Volumes

- `dor-dash-uploads:/app/uploads` - File uploads storage
- `dor-dash-logs:/app/logs` - Application logs

## 🔄 Auto-Update Feature

The container includes an intelligent auto-update system:

1. **Monitors** the specified Git repository every 5 minutes (configurable)
2. **Detects** new commits on the tracked branch
3. **Downloads** and applies updates automatically
4. **Rebuilds** frontend if needed
5. **Restarts** services gracefully
6. **Maintains** data persistence during updates

### Disabling Auto-Updates

Set `AUTO_UPDATE=false` when running the container:

```bash
docker run -d --name dor-dash -e AUTO_UPDATE=false ...
```

## 🌐 Nginx Reverse Proxy Setup

### Nginx Proxy Manager Configuration

1. **Create a new Proxy Host** in Nginx Proxy Manager
2. **Set the following:**
   - **Domain Names**: `dd.kronisto.net`
   - **Scheme**: `http`
   - **Forward Hostname/IP**: `172.30.98.177`
   - **Forward Port**: `1717`
   - **Cache Assets**: ✅ Enabled
   - **Block Common Exploits**: ✅ Enabled
   - **Websockets Support**: ✅ Enabled

3. **Add Custom Configuration** in the Advanced tab:
   ```nginx
   # Backend API proxy
   location /api/ {
       proxy_pass http://172.30.98.177:1718/api/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Forwarded-Host $host;
       
       # Handle preflight requests
       if ($request_method = 'OPTIONS') {
           add_header 'Access-Control-Allow-Origin' '$http_origin';
           add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE';
           add_header 'Access-Control-Allow-Headers' 'Origin, X-Requested-With, Content-Type, Accept, Authorization';
           add_header 'Access-Control-Allow-Credentials' 'true';
           add_header 'Access-Control-Max-Age' 86400;
           add_header 'Content-Length' 0;
           add_header 'Content-Type' 'text/plain';
           return 204;
       }
   }
   
   # Health check
   location /health {
       proxy_pass http://172.30.98.177:1718/health;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       access_log off;
   }
   
   # File upload size limit
   client_max_body_size 50M;
   ```

4. **Configure SSL** as needed (Let's Encrypt recommended)

### Manual Nginx Configuration

If using a custom nginx setup, use the provided `nginx.conf` file:

```bash
# Copy configuration
cp nginx.conf /etc/nginx/sites-available/dor-dash
ln -s /etc/nginx/sites-available/dor-dash /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

## 🛠️ Management Commands

### Using the deploy script:

```bash
# Deploy application
./deploy.sh deploy

# Stop application
./deploy.sh stop

# Restart application
./deploy.sh restart

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Rebuild and redeploy
./deploy.sh rebuild
```

### Direct Docker commands:

```bash
# View logs
docker logs -f dor-dash

# Execute shell in container
docker exec -it dor-dash /bin/bash

# Restart container
docker restart dor-dash

# View container stats
docker stats dor-dash
```

## 📊 Monitoring and Health Checks

### Health Check Endpoints

- **Backend Health**: `http://172.30.98.177:1718/health`
- **Frontend**: `http://172.30.98.177:1717`

### Log Locations

Inside the container:
- Backend logs: `/app/logs/backend.log`
- Frontend logs: `/app/logs/frontend.log`
- Container logs: `docker logs dor-dash`

### Monitoring Auto-Updates

Watch for update activity in the container logs:
```bash
docker logs -f dor-dash | grep -E "(UPDATE|ERROR|SUCCESS)"
```

## 🔒 Security Considerations

1. **Change default passwords** in production
2. **Use proper SSL certificates** for HTTPS
3. **Restrict network access** to required services only
4. **Regular backups** of uploaded files and database
5. **Monitor container logs** for suspicious activity

## 🐛 Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker logs dor-dash
   ```

2. **Database connection issues**
   - Verify PostgreSQL is accessible from container
   - Check environment variables

3. **Redis connection issues**
   - Verify Redis is accessible from container
   - Check Redis configuration

4. **Auto-update failures**
   - Check git repository access
   - Verify network connectivity
   - Review update logs in container

5. **Reverse proxy issues**
   - Verify nginx configuration
   - Check port accessibility
   - Test direct container access first

### Debug Mode

Run container with debug output:
```bash
docker run -it --rm -e AUTO_UPDATE=false dor-dash /bin/bash
```

## 📝 File Structure

```
DoR-Dash/
├── Dockerfile                 # Multi-stage container build
├── docker-compose.prod.yml    # Production compose file
├── docker-entrypoint.sh       # Container startup script
├── deploy.sh                  # Deployment automation
├── nginx.conf                 # Nginx reverse proxy config
├── UNRAID_DEPLOYMENT.md       # This documentation
├── backend/                   # FastAPI backend
├── frontend/                  # SvelteKit frontend
└── uploads/                   # File uploads (volume)
```

## 🆘 Support

For issues and questions:
1. Check container logs: `docker logs dor-dash`
2. Review this documentation
3. Check network connectivity to external services
4. Verify all environment variables are correctly set

## 🔄 Updates and Maintenance

The auto-update feature handles most maintenance automatically. For manual updates:

1. **Pull latest changes:**
   ```bash
   git pull origin master
   ```

2. **Rebuild and redeploy:**
   ```bash
   ./deploy.sh rebuild
   ```

3. **Backup important data** before major updates

---

**Note**: This deployment is designed for the specific network configuration described. Adjust IP addresses and ports as needed for your environment.