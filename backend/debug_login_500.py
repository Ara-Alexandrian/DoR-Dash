#!/usr/bin/env python3
"""
Debug script for 500 login errors
Tests database connectivity and user authentication step by step
"""
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test basic database connectivity"""
    try:
        import psycopg2
        logger.info("✅ psycopg2 library available")
        
        # Database connection parameters
        conn_params = {
            'host': '172.30.98.213',
            'port': 5432,
            'user': 'DoRadmin',
            'password': '1232',
            'database': 'DoR'
        }
        
        logger.info(f"🔗 Connecting to database at {conn_params['host']}:{conn_params['port']}")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"✅ Database connected successfully: {version[0]}")
        
        # Check if user table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("✅ 'user' table exists")
            
            # Check if cerebro user exists
            cursor.execute("SELECT id, username, hashed_password, role, is_active FROM \"user\" WHERE username = %s", ('cerebro',))
            user_data = cursor.fetchone()
            
            if user_data:
                logger.info(f"✅ cerebro user found: ID={user_data[0]}, role={user_data[3]}, active={user_data[4]}")
                logger.info(f"📝 Password hash: {user_data[2][:20]}...")
                
                # Test password verification
                try:
                    from passlib.context import CryptContext
                    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                    
                    is_valid = pwd_context.verify("123", user_data[2])
                    if is_valid:
                        logger.info("✅ Password '123' verification successful")
                    else:
                        logger.error("❌ Password '123' verification failed")
                        return False
                except ImportError:
                    logger.warning("⚠️ passlib not available - cannot test password verification")
                
            else:
                logger.error("❌ cerebro user not found in database")
                return False
                
        else:
            logger.error("❌ 'user' table does not exist")
            return False
            
        cursor.close()
        conn.close()
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_fastapi_dependencies():
    """Test if FastAPI and related dependencies are available"""
    dependencies = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'asyncpg',
        'psycopg2',
        'passlib',
        'python-jose'
    ]
    
    missing = []
    available = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            available.append(dep)
        except ImportError:
            missing.append(dep)
    
    logger.info(f"✅ Available dependencies: {', '.join(available)}")
    if missing:
        logger.error(f"❌ Missing dependencies: {', '.join(missing)}")
        return False
    
    return True

def test_auth_endpoint():
    """Test the auth endpoint logic manually"""
    try:
        # Import the authentication logic
        sys.path.append('/config/workspace/gitea/DoR-Dash/backend')
        from app.core.config import settings
        from app.api.endpoints.auth import get_user_by_username, verify_password
        
        logger.info("✅ Auth endpoint imports successful")
        logger.info(f"📊 Database URI: {settings.SQLALCHEMY_DATABASE_URI_SYNC}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Auth endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting DoR-Dash login debug...")
    
    tests = [
        ("FastAPI Dependencies", test_fastapi_dependencies),
        ("Database Connection", test_database_connection),
        ("Auth Endpoint Logic", test_auth_endpoint)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        results[test_name] = test_func()
    
    # Summary
    logger.info(f"\n📊 Test Results Summary:")
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        logger.info("🎉 All tests passed! Login should be working.")
    else:
        logger.info("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()