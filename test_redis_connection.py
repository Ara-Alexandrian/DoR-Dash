#!/usr/bin/env python3
"""
Script to test Redis connection and avatar caching functionality
Using Redis credentials from config.py
"""

import redis
import base64
import json
from datetime import datetime

# Redis connection details from config.py
REDIS_CONFIG = {
    'host': '172.30.98.214',
    'port': 6379,
    'db': 0
}

def connect_to_redis():
    """Connect to Redis cache"""
    try:
        r = redis.Redis(**REDIS_CONFIG, decode_responses=False)
        # Test connection
        r.ping()
        print(f"✅ Connected to Redis at {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
        return r
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")
        return None

def test_avatar_caching(redis_client):
    """Test avatar caching functionality"""
    
    # Sample avatar data (small test image)
    test_avatar_data = b"fake_image_data_for_testing_purposes"
    content_type = "image/jpeg"
    user_id = 24  # Test user we created
    
    # Cache key format
    cache_key = f"avatar:{user_id}"
    
    print(f"\n🧪 Testing avatar caching for user {user_id}...")
    
    # Store avatar in cache
    avatar_cache_data = {
        'data': base64.b64encode(test_avatar_data).decode('utf-8'),
        'content_type': content_type,
        'cached_at': datetime.now().isoformat(),
        'size': len(test_avatar_data)
    }
    
    try:
        # Store in Redis with 1 hour expiration
        redis_client.setex(cache_key, 3600, json.dumps(avatar_cache_data))
        print(f"✅ Avatar cached with key: {cache_key}")
        
        # Retrieve from cache
        cached_data = redis_client.get(cache_key)
        if cached_data:
            cached_avatar = json.loads(cached_data)
            retrieved_data = base64.b64decode(cached_avatar['data'])
            
            print(f"✅ Avatar retrieved from cache:")
            print(f"   Content-Type: {cached_avatar['content_type']}")
            print(f"   Size: {cached_avatar['size']} bytes")
            print(f"   Cached at: {cached_avatar['cached_at']}")
            print(f"   Data matches: {retrieved_data == test_avatar_data}")
            
            # Test TTL
            ttl = redis_client.ttl(cache_key)
            print(f"   TTL: {ttl} seconds")
            
        else:
            print("❌ Failed to retrieve avatar from cache")
            
    except Exception as e:
        print(f"❌ Error testing avatar cache: {e}")

def test_cache_operations(redis_client):
    """Test basic Redis operations"""
    
    print("\n🧪 Testing basic Redis operations...")
    
    try:
        # Set and get a simple key
        redis_client.set("test:key", "test_value", ex=60)
        value = redis_client.get("test:key")
        print(f"✅ Basic set/get: {value.decode('utf-8') if value else 'None'}")
        
        # Test key expiration
        ttl = redis_client.ttl("test:key")
        print(f"✅ TTL test: {ttl} seconds")
        
        # Test key patterns
        redis_client.set("avatar:user:1", "data1", ex=60)
        redis_client.set("avatar:user:2", "data2", ex=60)
        
        avatar_keys = redis_client.keys("avatar:*")
        print(f"✅ Pattern matching: found {len(avatar_keys)} avatar keys")
        
        # Clean up test keys
        for key in avatar_keys:
            redis_client.delete(key)
        redis_client.delete("test:key")
        
        print("✅ Test cleanup completed")
        
    except Exception as e:
        print(f"❌ Error testing Redis operations: {e}")

def show_redis_info(redis_client):
    """Show Redis server information"""
    
    print("\n📊 Redis Server Information:")
    
    try:
        info = redis_client.info()
        
        print(f"   Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"   Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"   Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"   Total Keys: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")
        print(f"   Uptime: {info.get('uptime_in_seconds', 0)} seconds")
        
    except Exception as e:
        print(f"❌ Error getting Redis info: {e}")

def main():
    """Main function to test Redis connection and avatar caching"""
    
    print("🔧 Testing Redis connection and avatar caching...")
    print(f"Connecting to Redis at {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    
    redis_client = connect_to_redis()
    if not redis_client:
        print("❌ Failed to connect to Redis")
        return
    
    try:
        # Show Redis info
        show_redis_info(redis_client)
        
        # Test basic operations
        test_cache_operations(redis_client)
        
        # Test avatar caching
        test_avatar_caching(redis_client)
        
        print("\n✅ Redis testing completed successfully!")
        print("\nNext steps:")
        print("- Update backend avatar upload to store in PostgreSQL")
        print("- Create avatar serving endpoint with Redis caching")
        print("- Update frontend to use new avatar endpoint")
        
    except Exception as e:
        print(f"❌ Error during Redis testing: {e}")
    finally:
        redis_client.close()

if __name__ == "__main__":
    main()