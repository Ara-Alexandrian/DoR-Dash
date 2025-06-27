# DoR-Dash Deployment Guide

This guide provides comprehensive instructions for safe, reliable deployments of DoR-Dash.

## 🚀 Quick Deployment

For quick deployments when you're confident in the changes:

```bash
# Run the automated deployment script
chmod +x scripts/deployment-checklist.sh
./scripts/deployment-checklist.sh
```

## 📋 Manual Deployment Steps

For more control or when troubleshooting:

### 1. Pre-Deployment Checklist

- [ ] All changes committed and pushed to repository
- [ ] Tests passing locally
- [ ] No active user sessions if possible (notify users)
- [ ] Database backup ready
- [ ] Rollback plan prepared

### 2. Environment Preparation

```bash
# Navigate to project root
cd /config/workspace/gitea/DoR-Dash

# Pull latest changes
git pull origin master

# Check for any conflicts or issues
git status
```

### 3. Database Migration

```bash
# Navigate to backend
cd backend

# Check migration status
python -m alembic current

# Run any pending migrations
python -m alembic upgrade head

# Verify migration success
python -m alembic current
```

### 4. Application Build

```bash
# Build frontend
cd ../frontend
npm install
npm run build

# Return to root
cd ..
```

### 5. Deployment

```bash
# Stop existing services
docker-compose down --remove-orphans

# Build and start new services
docker-compose up -d --build

# Wait for services to be ready
sleep 30
```

### 6. Health Verification

```bash
# Check service status
docker-compose ps

# Test API health
curl http://localhost:8001/api/v1/health

# Test frontend
curl http://localhost:3001

# Check application health
curl https://dd.kronisto.net/api/v1/health
```

## 🔧 Common Issues and Solutions

### Issue: 500 Internal Server Errors

**Symptoms:** API endpoints returning 500 errors, especially after deployment

**Likely Causes:**
- Datetime deprecated function usage (`datetime.utcnow()`)
- Database migration not applied
- Environment variables missing
- Container resource constraints

**Solutions:**
1. Check backend logs: `docker-compose logs backend`
2. Verify database connection: `curl http://localhost:8001/api/v1/health/database`
3. Run migration check: `curl http://localhost:8001/api/v1/health/migrations`
4. Check for datetime issues in models

### Issue: Authentication Failures

**Symptoms:** Users showing as undefined, 401 errors, login loops

**Likely Causes:**
- JWT secret changed
- Session storage cleared
- Token expiration issues
- Auth model datetime issues

**Solutions:**
1. Check JWT configuration in environment
2. Clear browser localStorage: `localStorage.clear()`
3. Verify user model datetime fields
4. Check auth endpoint logs

### Issue: Frontend Not Loading

**Symptoms:** White screen, build errors, asset loading failures

**Likely Causes:**
- Build process failed
- Static files not served correctly
- Cache issues
- Node.js version mismatch

**Solutions:**
1. Clear build cache: `rm -rf frontend/.svelte-kit`
2. Rebuild: `cd frontend && npm run build`
3. Check nginx/proxy configuration
4. Clear browser cache

### Issue: Database Connection Errors

**Symptoms:** Cannot connect to database, migration failures

**Likely Causes:**
- PostgreSQL not running
- Connection string incorrect
- Database locked
- Network issues

**Solutions:**
1. Check PostgreSQL status: `docker-compose ps postgres`
2. Verify DATABASE_URL environment variable
3. Test connection: `docker exec postgres psql -U admin -d dor_dash -c "SELECT 1;"`
4. Restart database if needed: `docker-compose restart postgres`

## 🛡️ Safety Measures

### Automatic Rollback

If deployment fails, run the generated rollback script:

```bash
./rollback.sh
```

### Manual Rollback

1. **Stop new services:**
   ```bash
   docker-compose down
   ```

2. **Restore from backup:**
   ```bash
   # Restore code
   git reset --hard HEAD~1  # Or specific commit
   
   # Restore database
   docker exec postgres psql -U admin dor_dash < backups/BACKUP_FILE.sql
   ```

3. **Restart services:**
   ```bash
   docker-compose up -d --build
   ```

### Health Monitoring

After deployment, monitor:

```bash
# Run continuous monitoring
./monitor.sh

# Or check manually
watch -n 30 'curl -s http://localhost:8001/api/v1/health | jq .status'
```

## 📊 Deployment Verification

### Automated Tests

Run post-deployment tests:

```bash
# API tests
./test-api.sh

# Health checks
curl https://dd.kronisto.net/api/v1/health/ready
curl https://dd.kronisto.net/api/v1/health/database
curl https://dd.kronisto.net/api/v1/health/migrations
```

### Manual Verification

1. **Login Process:**
   - Navigate to https://dd.kronisto.net
   - Test login with faculty credentials
   - Verify profile loads correctly

2. **Core Functionality:**
   - Access dashboard
   - Navigate to presentation assignments
   - Verify meeting filtering (only future meetings)
   - Test form creation (don't submit)

3. **Updates Page:**
   - Navigate to updates page
   - Verify no 500 errors
   - Check user authentication state

## 🔄 Continuous Deployment

### GitHub Actions Integration

For automated deployments, consider setting up GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ master ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /config/workspace/gitea/DoR-Dash && ./scripts/deployment-checklist.sh'
```

### Blue-Green Deployment

For zero-downtime deployments:

1. Set up second environment
2. Deploy to inactive environment
3. Run health checks
4. Switch traffic to new environment
5. Keep old environment as backup

## 📝 Troubleshooting Commands

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs backend --tail 50
docker-compose logs frontend --tail 50

# Check resource usage
docker stats

# Database operations
docker exec postgres psql -U admin dor_dash

# Clear caches
docker exec redis redis-cli FLUSHALL

# Restart specific service
docker-compose restart backend

# Force rebuild
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

## 🚨 Emergency Procedures

### Complete System Recovery

If everything is broken:

1. **Stop all services:**
   ```bash
   docker-compose down -v
   ```

2. **Reset to known good state:**
   ```bash
   git reset --hard KNOWN_GOOD_COMMIT
   ```

3. **Restore database:**
   ```bash
   # Import fresh database
   docker-compose up -d postgres
   sleep 10
   docker exec postgres psql -U admin -c "DROP DATABASE IF EXISTS dor_dash;"
   docker exec postgres psql -U admin -c "CREATE DATABASE dor_dash;"
   docker exec postgres psql -U admin dor_dash < backup_file.sql
   ```

4. **Rebuild everything:**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Contact Information

For deployment emergencies:
- Check GitHub Issues: https://github.com/Ara-Alexandrian/DoR-Dash/issues
- Review logs in `/var/log/dor-dash/`
- Check system resources: `htop`, `df -h`

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Backup/Restore](https://www.postgresql.org/docs/current/backup.html)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [SvelteKit Deployment](https://kit.svelte.dev/docs/adapters)