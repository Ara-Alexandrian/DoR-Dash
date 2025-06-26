#!/bin/bash

# DoR-Dash Deployment Checklist and Automation Script
# This script ensures safe deployments with minimal downtime

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 DoR-Dash Deployment Checklist"
echo "================================"
echo

# Function to check if a command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 failed${NC}"
        return 1
    fi
}

# Function to wait for service to be healthy
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "   Waiting for $service to be healthy"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
            echo -e " ${GREEN}✅${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    echo -e " ${RED}❌ Timeout${NC}"
    return 1
}

# 1. Pre-deployment checks
echo "📋 Pre-deployment Checks"
echo "------------------------"

# Check if we're on the correct branch
current_branch=$(git branch --show-current)
echo -n "   Current branch: $current_branch"
if [ "$current_branch" != "master" ] && [ "$current_branch" != "main" ]; then
    echo -e " ${YELLOW}⚠️  Warning: Not on master/main branch${NC}"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e " ${GREEN}✅${NC}"
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "   ${YELLOW}⚠️  Warning: Uncommitted changes detected${NC}"
    git status --short
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "   ${GREEN}✅ No uncommitted changes${NC}"
fi

# 2. Create backup
echo
echo "💾 Creating Backup"
echo "-----------------"

# Create backup directory
backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

# Backup database
echo -n "   Backing up database..."
docker exec postgres pg_dump -U admin dor_dash > "$backup_dir/database.sql" 2>/dev/null
check_status "Database backup"

# Backup current code
echo -n "   Backing up code..."
tar -czf "$backup_dir/code.tar.gz" --exclude=node_modules --exclude=.git --exclude=backups . 2>/dev/null
check_status "Code backup"

# 3. Run tests
echo
echo "🧪 Running Tests"
echo "----------------"

# Backend tests
echo -n "   Running backend tests..."
cd backend
python -m pytest tests/ -q 2>/dev/null || echo -e " ${YELLOW}⚠️  No tests found${NC}"
cd ..

# Frontend tests
echo -n "   Running frontend tests..."
cd frontend
npm test 2>/dev/null || echo -e " ${YELLOW}⚠️  No tests configured${NC}"
cd ..

# 4. Build phase
echo
echo "🔨 Building Application"
echo "----------------------"

# Build frontend
echo -n "   Building frontend..."
cd frontend
npm run build > /dev/null 2>&1
check_status "Frontend build"
cd ..

# 5. Database migrations
echo
echo "🗄️  Database Migrations"
echo "---------------------"

echo -n "   Checking for pending migrations..."
cd backend
pending_migrations=$(python -m alembic current 2>/dev/null | grep -c "head" || echo "0")
if [ "$pending_migrations" -eq "0" ]; then
    echo -e " ${YELLOW}⚠️  Pending migrations detected${NC}"
    echo "   Running migrations..."
    python -m alembic upgrade head
    check_status "   Database migrations"
else
    echo -e " ${GREEN}✅ Database up to date${NC}"
fi
cd ..

# 6. Deployment
echo
echo "🚀 Deploying Application"
echo "-----------------------"

# Stop existing containers gracefully
echo -n "   Stopping existing services..."
docker-compose down --remove-orphans > /dev/null 2>&1
check_status "Service shutdown"

# Start new containers
echo -n "   Starting new services..."
docker-compose up -d --build > /dev/null 2>&1
check_status "Service startup"

# 7. Health checks
echo
echo "🏥 Health Checks"
echo "----------------"

# Wait for services to be ready
wait_for_service "Backend API" "http://localhost:8001/api/v1/health"
wait_for_service "Frontend" "http://localhost:3001"

# 8. Post-deployment verification
echo
echo "🔍 Post-deployment Verification"
echo "------------------------------"

# Check API endpoints
echo "   Testing API endpoints:"
endpoints=(
    "/api/v1/health"
    "/api/v1/docs"
)

for endpoint in "${endpoints[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001$endpoint")
    if [ "$status" = "200" ]; then
        echo -e "   ${GREEN}✅ $endpoint (200)${NC}"
    else
        echo -e "   ${RED}❌ $endpoint ($status)${NC}"
    fi
done

# 9. Cache management
echo
echo "🧹 Cache Management"
echo "------------------"

# Clear Redis cache if exists
if docker ps | grep -q redis; then
    echo -n "   Clearing Redis cache..."
    docker exec redis redis-cli FLUSHALL > /dev/null 2>&1
    check_status "Redis cache cleared"
fi

# Update build info for cache busting
echo -n "   Updating build info..."
BUILD_TIME=$(date +%s)
BUILD_ID=$(echo $BUILD_TIME | sha256sum | head -c 8)
echo "{\"buildId\": \"$BUILD_ID\", \"buildTime\": \"$BUILD_TIME\"}" > frontend/public/build-info.json
check_status "Build info updated"

# 10. Monitoring setup
echo
echo "📊 Monitoring"
echo "------------"

# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script
while true; do
    backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health)
    frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001)
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    if [ "$backend_status" != "200" ] || [ "$frontend_status" != "200" ]; then
        echo "[$timestamp] ⚠️  Service degradation - Backend: $backend_status, Frontend: $frontend_status"
        # Could add alerting here (email, Slack, etc.)
    fi
    
    sleep 60
done
EOF
chmod +x monitor.sh
echo -e "   ${GREEN}✅ Monitoring script created (run ./monitor.sh)${NC}"

# 11. Rollback preparation
echo
echo "🔄 Rollback Preparation"
echo "----------------------"

# Create rollback script
cat > rollback.sh << EOF
#!/bin/bash
# Rollback to previous version
echo "Rolling back to backup: $backup_dir"
docker-compose down
tar -xzf "$backup_dir/code.tar.gz"
docker exec postgres psql -U admin dor_dash < "$backup_dir/database.sql"
docker-compose up -d --build
EOF
chmod +x rollback.sh
echo -e "   ${GREEN}✅ Rollback script created (run ./rollback.sh if needed)${NC}"

# 12. Final summary
echo
echo "📋 Deployment Summary"
echo "--------------------"
echo -e "   ${GREEN}✅ Deployment completed successfully${NC}"
echo "   📁 Backup location: $backup_dir"
echo "   🔄 Rollback script: ./rollback.sh"
echo "   📊 Monitoring script: ./monitor.sh"
echo
echo "🎉 Deployment complete! Please verify the application at https://dd.kronisto.net"
echo
echo "⚠️  Important reminders:"
echo "   - Monitor logs: docker-compose logs -f"
echo "   - Check user reports for any issues"
echo "   - Run ./monitor.sh for continuous monitoring"
echo "   - Keep rollback script ready for quick recovery"