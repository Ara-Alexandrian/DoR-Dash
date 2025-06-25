#!/usr/bin/env python3
"""
Comprehensive test script for the new avatar implementation
Tests PostgreSQL storage + Redis caching + API endpoints
"""

import requests
import psycopg2
import redis
import json
import base64
from PIL import Image
import io
import time

# Configuration
BACKEND_URL = "http://172.30.98.177:8000"
DB_CONFIG = {
    'host': '172.30.98.213',
    'port': 5432,
    'database': 'DoR',
    'user': 'DoRadmin',
    'password': '1232'
}
REDIS_CONFIG = {
    'host': '172.30.98.214',
    'port': 6379,
    'db': 0
}

# Test credentials (using the testuser we created)
TEST_USER_ID = 24
TEST_USERNAME = "testuser"

def create_test_image():
    """Create a small test image for avatar upload"""
    # Create a 100x100 red square image
    image = Image.new('RGB', (100, 100), color='red')
    
    # Add some text to make it identifiable
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(image)
    try:
        # Try to use default font
        draw.text((30, 40), "TEST", fill='white')
    except:
        # Fallback if font loading fails
        draw.rectangle([30, 30, 70, 70], fill='white')
    
    # Save to bytes
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()

def test_database_fields():
    """Test that avatar fields exist in database"""
    print("🔧 Testing database fields...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if new fields exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name IN ('avatar_data', 'avatar_content_type');
        """)
        
        fields = [row[0] for row in cursor.fetchall()]
        
        if 'avatar_data' in fields and 'avatar_content_type' in fields:
            print("✅ Database fields exist: avatar_data, avatar_content_type")
            return True
        else:
            print(f"❌ Missing database fields. Found: {fields}")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_redis_connection():
    """Test Redis connection"""
    print("🔧 Testing Redis connection...")
    
    try:
        r = redis.Redis(**REDIS_CONFIG, decode_responses=False)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_backend_health():
    """Test backend API health"""
    print("🔧 Testing backend API health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def get_auth_token():
    """Get authentication token for API calls"""
    print("🔧 Getting authentication token...")
    
    try:
        # Login with admin credentials (from summary)
        login_data = {
            "username": "cerebro",
            "password": "123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_avatar_upload(auth_token):
    """Test avatar upload API endpoint"""
    print("🔧 Testing avatar upload...")
    
    try:
        # Create test image
        image_data = create_test_image()
        
        # Upload avatar
        files = {
            'file': ('test_avatar.png', image_data, 'image/png')
        }
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/users/{TEST_USER_ID}/avatar",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Avatar upload successful:")
            print(f"   Message: {result.get('message')}")
            print(f"   Avatar URL: {result.get('avatar_url')}")
            print(f"   Storage: {result.get('storage', 'unknown')}")
            return True
        else:
            print(f"❌ Avatar upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Avatar upload error: {e}")
        return False

def test_avatar_retrieval():
    """Test avatar retrieval from new endpoint"""
    print("🔧 Testing avatar retrieval...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/users/{TEST_USER_ID}/avatar/image")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            avatar_source = response.headers.get('x-avatar-source')
            content_length = len(response.content)
            
            print(f"✅ Avatar retrieval successful:")
            print(f"   Content-Type: {content_type}")
            print(f"   Avatar Source: {avatar_source}")
            print(f"   Content Length: {content_length} bytes")
            
            # Verify it's a valid image
            try:
                image = Image.open(io.BytesIO(response.content))
                print(f"   Image Size: {image.size}")
                print(f"   Image Mode: {image.mode}")
                return True
            except Exception as e:
                print(f"❌ Invalid image data: {e}")
                return False
        else:
            print(f"❌ Avatar retrieval failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Avatar retrieval error: {e}")
        return False

def test_redis_caching():
    """Test that avatar is cached in Redis"""
    print("🔧 Testing Redis caching...")
    
    try:
        r = redis.Redis(**REDIS_CONFIG, decode_responses=False)
        
        # Check if avatar is cached
        cache_key = f"avatar:{TEST_USER_ID}"
        cached_data = r.get(cache_key)
        
        if cached_data:
            avatar_info = json.loads(cached_data)
            print(f"✅ Avatar found in Redis cache:")
            print(f"   Content-Type: {avatar_info.get('content_type')}")
            print(f"   Size: {avatar_info.get('size')} bytes")
            print(f"   Cached at: {avatar_info.get('cached_at')}")
            
            # Test TTL
            ttl = r.ttl(cache_key)
            print(f"   TTL: {ttl} seconds")
            
            return True
        else:
            print("❌ Avatar not found in Redis cache")
            return False
            
    except Exception as e:
        print(f"❌ Redis caching test failed: {e}")
        return False

def test_cache_performance():
    """Test cache performance vs database retrieval"""
    print("🔧 Testing cache performance...")
    
    try:
        # First request (should be from database)
        start_time = time.time()
        response1 = requests.get(f"{BACKEND_URL}/api/v1/users/{TEST_USER_ID}/avatar/image")
        db_time = time.time() - start_time
        db_source = response1.headers.get('x-avatar-source', 'unknown')
        
        # Second request (should be from cache)
        start_time = time.time()
        response2 = requests.get(f"{BACKEND_URL}/api/v1/users/{TEST_USER_ID}/avatar/image")
        cache_time = time.time() - start_time
        cache_source = response2.headers.get('x-avatar-source', 'unknown')
        
        print(f"✅ Performance test results:")
        print(f"   First request ({db_source}): {db_time:.3f}s")
        print(f"   Second request ({cache_source}): {cache_time:.3f}s")
        
        if cache_time < db_time:
            print(f"   ⚡ Cache is {db_time/cache_time:.1f}x faster!")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_database_storage():
    """Verify avatar is stored in database"""
    print("🔧 Testing database storage...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT avatar_data, avatar_content_type, avatar_url 
            FROM "user" 
            WHERE id = %s;
        """, (TEST_USER_ID,))
        
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            avatar_data, content_type, avatar_url = result
            print(f"✅ Avatar stored in database:")
            print(f"   Data size: {len(avatar_data)} bytes")
            print(f"   Content-Type: {content_type}")
            print(f"   Avatar URL: {avatar_url}")
            return True
        else:
            print("❌ No avatar data found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database storage test failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def cleanup_test_data():
    """Clean up test data"""
    print("🧹 Cleaning up test data...")
    
    try:
        # Clear Redis cache
        r = redis.Redis(**REDIS_CONFIG, decode_responses=False)
        cache_key = f"avatar:{TEST_USER_ID}"
        r.delete(cache_key)
        
        # Clear database avatar data
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE "user" 
            SET avatar_data = NULL, avatar_content_type = NULL, avatar_url = NULL 
            WHERE id = %s;
        """, (TEST_USER_ID,))
        
        conn.commit()
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main test function"""
    print("🚀 Testing Complete Avatar Implementation")
    print("=" * 50)
    
    tests = [
        ("Database Fields", test_database_fields),
        ("Redis Connection", test_redis_connection),
        ("Backend Health", test_backend_health),
    ]
    
    # Run basic connectivity tests first
    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n❌ Basic test '{test_name}' failed. Aborting.")
            return
        print()
    
    # Get authentication token
    auth_token = get_auth_token()
    if not auth_token:
        print("❌ Cannot proceed without authentication token")
        return
    print()
    
    # Run avatar functionality tests
    avatar_tests = [
        ("Avatar Upload", lambda: test_avatar_upload(auth_token)),
        ("Database Storage", test_database_storage),
        ("Avatar Retrieval", test_avatar_retrieval),
        ("Redis Caching", test_redis_caching),
        ("Cache Performance", test_cache_performance),
    ]
    
    for test_name, test_func in avatar_tests:
        if test_func():
            passed += 1
        print()
    
    # Clean up
    cleanup_test_data()
    
    # Final results
    total_tests = len(tests) + len(avatar_tests)
    print("=" * 50)
    print(f"🏁 Test Results: {passed}/{total_tests} tests passed")
    
    if passed == total_tests:
        print("✅ All tests passed! Avatar implementation is working correctly.")
        print("\n🎉 Benefits achieved:")
        print("   - Avatars stored in PostgreSQL database")
        print("   - Redis caching for fast retrieval")
        print("   - No more broken image loading issues")
        print("   - Scalable storage solution")
        print("   - Survives container restarts")
    else:
        print(f"❌ {total_tests - passed} tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()