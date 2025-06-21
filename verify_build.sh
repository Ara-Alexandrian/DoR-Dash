#!/bin/bash

# Verify that dorfullrebuild installs all required dependencies

echo "🔍 Verifying DoR-Dash build includes all required dependencies..."

# Test if container is running
if ! docker ps | grep -q "dor-dash"; then
    echo "❌ DoR-Dash container is not running"
    echo "💡 Run 'dorfullrebuild' first"
    exit 1
fi

echo "✅ Container is running"

# Test if we can exec into container
echo "🧪 Testing dependencies inside container..."

docker exec dor-dash python3 -c "
import sys
missing = []
deps = ['fastapi', 'uvicorn', 'sqlalchemy', 'asyncpg', 'psycopg2', 'passlib', 'jose']

for dep in deps:
    try:
        __import__(dep)
        print(f'✅ {dep}')
    except ImportError:
        print(f'❌ {dep}')
        missing.append(dep)

if missing:
    print(f'\\n🚨 Missing dependencies: {missing}')
    print('💡 The container needs to be rebuilt with dependencies')
    sys.exit(1)
else:
    print('\\n🎉 All dependencies are available!')
    sys.exit(0)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🧪 Testing backend login endpoint..."
    
    # Test login endpoint
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=cerebro&password=123&grant_type=password" \
        http://172.30.98.177:8000/api/v1/auth/login)
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Login endpoint working! Received JWT token"
        echo "🎉 Build verification PASSED"
    elif [ "$http_code" = "500" ]; then
        echo "❌ Login endpoint still returning 500 error"
        echo "🔧 Dependencies are installed but there may be a database issue"
        echo "💡 Try running database initialization scripts"
    else
        echo "⚠️  Login endpoint returned HTTP $http_code"
        echo "📄 Response: $body"
    fi
else
    echo ""
    echo "❌ Build verification FAILED"
    echo "💡 Run 'dorfullrebuild --no-cache' to force a fresh build"
fi