# MCP SSH Quick Reference

## Container Access

### DoR-Dash Application
```bash
ssh root@172.30.98.177
# Password: dor-ssh-password-2024

ssh dor-user@172.30.98.177
# Password: dor-user-password-2024
```

### PostgreSQL Database
```bash
ssh root@172.30.98.213
# Note: SSH may need to be enabled first
```

### Redis Cache
```bash
ssh root@172.30.98.214
# Note: SSH may need to be enabled first
```

### Ollama AI Server
```bash
ssh root@172.30.98.14
# Note: SSH may need to be enabled first
```

## Common Commands

### Check Application Status
```bash
# On DoR-Dash container
ps aux | grep -E "(uvicorn|serve|node)"
tail -f /app/logs/backend.log
curl -f http://localhost:8000/health
```

### Database Operations
```bash
# Connect to PostgreSQL
psql -h 172.30.98.213 -U postgres -d dor_dash_db
```

### Cache Operations
```bash
# Connect to Redis
redis-cli -h 172.30.98.214
```

### AI Model Status
```bash
# Check Ollama models
curl http://172.30.98.14:11434/api/tags
```

## File Locations

- **Backend**: `/app/backend/`
- **Frontend**: `/app/frontend/build/`
- **Logs**: `/app/logs/`
- **Uploads**: `/app/uploads/`

## Security Reminder
**⚠️ CHANGE DEFAULT PASSWORDS IN PRODUCTION!**