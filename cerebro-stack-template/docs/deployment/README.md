# Deployment Guide

This guide covers all aspects of deploying the application to various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- Network: 100Mbps

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- Network: 1Gbps

### Required Software

- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **Node.js**: 18+ (for local development)
- **Python**: 3.11+ (for local development)
- **PostgreSQL**: 15+
- **Redis**: 7+

## Environment Setup

### Environment Variables

Create `.env` files for each environment:

#### Production (.env.production)
```bash
# Application
NODE_ENV=production
DEBUG=false
PORT=8000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/production_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_CREDENTIALS=true

# File Storage
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,jpg,jpeg,png,gif

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
METRICS_ENABLED=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

#### Staging (.env.staging)
```bash
# Similar to production but with staging-specific values
NODE_ENV=staging
DEBUG=true
DATABASE_URL=postgresql://user:password@localhost:5432/staging_db
CORS_ORIGINS=https://staging.yourdomain.com
LOG_LEVEL=DEBUG
```

#### Development (.env.development)
```bash
NODE_ENV=development
DEBUG=true
PORT=8000
DATABASE_URL=postgresql://user:password@localhost:5432/development_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=development-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LOG_LEVEL=DEBUG
```

## Local Development

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/yourproject.git
cd yourproject

# Run setup script
./scripts/setup.sh

# Start all services
./scripts/start.sh
```

### Manual Setup

1. **Install Dependencies**:
   ```bash
   # Frontend
   cd frontend
   npm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

2. **Database Setup**:
   ```bash
   # Start PostgreSQL and Redis
   docker-compose -f docker-compose.dev.yml up -d postgres redis
   
   # Run migrations
   cd backend
   alembic upgrade head
   ```

3. **Start Services**:
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## Staging Deployment

### Using Docker Compose

1. **Prepare Environment**:
   ```bash
   # Copy environment file
   cp .env.example .env.staging
   # Edit .env.staging with staging values
   ```

2. **Deploy**:
   ```bash
   # Pull latest images
   docker-compose -f docker-compose.staging.yml pull
   
   # Deploy with zero downtime
   docker-compose -f docker-compose.staging.yml up -d
   
   # Run database migrations
   docker-compose -f docker-compose.staging.yml exec backend alembic upgrade head
   ```

3. **Verify Deployment**:
   ```bash
   # Check service health
   curl https://staging.yourdomain.com/health
   
   # Check logs
   docker-compose -f docker-compose.staging.yml logs -f
   ```

## Production Deployment

### Option 1: Docker Compose (Simple)

```bash
# 1. Prepare production environment
cp .env.example .env.production
# Edit .env.production with production values

# 2. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 4. Create admin user (if needed)
docker-compose -f docker-compose.prod.yml exec backend python -m app.cli create-admin

# 5. Verify deployment
curl https://api.yourdomain.com/health
```

### Option 2: Kubernetes (Advanced)

See [kubernetes/](../kubernetes/) directory for Kubernetes manifests.

```bash
# Apply configurations
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml

# Check deployment status
kubectl get pods -n yourproject
kubectl get services -n yourproject
```

### Option 3: Cloud Platforms

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker build -t yourproject .
docker tag yourproject:latest <account>.dkr.ecr.<region>.amazonaws.com/yourproject:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/yourproject:latest

# Deploy using ECS CLI or AWS Console
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/yourproject
gcloud run deploy --image gcr.io/PROJECT-ID/yourproject --platform managed
```

#### Heroku
```bash
# Add Heroku remote
heroku git:remote -a your-app

# Deploy
git push heroku main

# Run migrations
heroku run python -m alembic upgrade head
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Automatic SSL Renewal

```bash
# Add to crontab
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

## Database Management

### Backup Strategy

```bash
#!/bin/bash
# backup-database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="production_db"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 sync $BACKUP_DIR s3://your-backup-bucket/database/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Review migration file before applying
cat alembic/versions/xxx_add_new_table.py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Monitoring and Health Checks

### Health Check Endpoint

The application provides a comprehensive health check at `/health`:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "database": true,
    "redis": true,
    "external_api": true
  },
  "version": "1.0.0",
  "uptime": 3600
}
```

### Monitoring Setup

#### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  grafana-data:
```

#### Application Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Log Management

#### Centralized Logging with ELK Stack

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logging/logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose exec backend python -c "
from app.database import engine
print('Database connection:', engine.url)
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Connection successful:', result.fetchone())
"
```

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

#### SSL Certificate Issues
```bash
# Check certificate status
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout

# Renew certificate
certbot renew --nginx
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f backend frontend

# Search for errors
docker-compose logs backend | grep ERROR

# Follow real-time logs
docker-compose logs -f --tail=100 backend
```

### Performance Debugging

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s "https://yourdomain.com/api/health"

# Monitor database queries
docker-compose exec postgres psql -U user -d production_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

## Rollback Procedures

### Application Rollback

```bash
# Using Docker tags
docker-compose -f docker-compose.prod.yml pull yourapp:previous-version
docker-compose -f docker-compose.prod.yml up -d

# Using git
git checkout previous-stable-commit
./scripts/deploy.sh production
```

### Database Rollback

```bash
# Rollback migration
alembic downgrade -1

# Restore from backup
pg_restore -d production_db backup_20240101_120000.sql
```

## Security Checklist

- [ ] SSL/TLS certificates installed and auto-renewing
- [ ] Firewall configured (only necessary ports open)
- [ ] Database credentials rotated
- [ ] Application secrets in environment variables
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting set up
- [ ] Backup and recovery tested
- [ ] Dependency scanning enabled
- [ ] Container security scanning enabled

---

*Last updated: [Date]*
*Deployment Version: 1.0.0*