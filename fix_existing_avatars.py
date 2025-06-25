#!/usr/bin/env python3
"""
Fix existing avatar URLs to use the new database endpoint
Update users who have old file-based avatar URLs
"""

import psycopg2
import requests

# Database connection details
DB_CONFIG = {
    'host': '172.30.98.213',
    'port': 5432,
    'database': 'DoR',
    'user': 'DoRadmin',
    'password': '1232'
}

def fix_avatar_urls():
    """Update existing avatar URLs to use new database endpoint"""
    print("🔧 Fixing existing avatar URLs...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Find users with old avatar URLs (file-based)
        cursor.execute("""
            SELECT id, username, avatar_url 
            FROM "user" 
            WHERE avatar_url IS NOT NULL 
            AND avatar_url LIKE '%uploads/avatars/%';
        """)
        
        old_avatars = cursor.fetchall()
        
        if not old_avatars:
            print("✅ No old avatar URLs found to fix")
            return
        
        print(f"Found {len(old_avatars)} users with old avatar URLs:")
        
        for user_id, username, old_url in old_avatars:
            print(f"  User {user_id} ({username}): {old_url}")
            
            # Update to new database endpoint
            new_url = f"/api/v1/users/{user_id}/avatar/image"
            
            cursor.execute("""
                UPDATE "user" 
                SET avatar_url = %s 
                WHERE id = %s;
            """, (new_url, user_id))
            
            print(f"    ✅ Updated to: {new_url}")
        
        # For users who have avatar_data but wrong avatar_url, fix them too
        cursor.execute("""
            SELECT id, username 
            FROM "user" 
            WHERE avatar_data IS NOT NULL 
            AND (avatar_url IS NULL OR avatar_url NOT LIKE '/api/v1/users/%/avatar/image');
        """)
        
        missing_urls = cursor.fetchall()
        
        if missing_urls:
            print(f"\nFound {len(missing_urls)} users with avatar data but wrong URLs:")
            
            for user_id, username in missing_urls:
                new_url = f"/api/v1/users/{user_id}/avatar/image"
                
                cursor.execute("""
                    UPDATE "user" 
                    SET avatar_url = %s 
                    WHERE id = %s;
                """, (new_url, user_id))
                
                print(f"  User {user_id} ({username}): ✅ Set to {new_url}")
        
        conn.commit()
        
        print(f"\n✅ Successfully fixed avatar URLs!")
        print("Users should now see avatars loaded from the database.")
        
    except Exception as e:
        print(f"❌ Error fixing avatar URLs: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

def test_new_endpoints():
    """Test that the new avatar endpoints are working"""
    print("\n🧪 Testing new avatar endpoints...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Find users with avatar data
        cursor.execute("""
            SELECT id, username, avatar_url 
            FROM "user" 
            WHERE avatar_data IS NOT NULL 
            LIMIT 3;
        """)
        
        users_with_avatars = cursor.fetchall()
        
        if not users_with_avatars:
            print("❌ No users with avatar data found")
            return
        
        backend_url = "http://172.30.98.177:8000"
        
        for user_id, username, avatar_url in users_with_avatars:
            endpoint = f"{backend_url}/api/v1/users/{user_id}/avatar/image"
            
            try:
                response = requests.get(endpoint, timeout=5)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', 'unknown')
                    avatar_source = response.headers.get('x-avatar-source', 'unknown')
                    size = len(response.content)
                    
                    print(f"  ✅ User {user_id} ({username}):")
                    print(f"     Status: {response.status_code}")
                    print(f"     Content-Type: {content_type}")
                    print(f"     Source: {avatar_source}")
                    print(f"     Size: {size} bytes")
                else:
                    print(f"  ❌ User {user_id} ({username}): {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ User {user_id} ({username}): {e}")
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def show_avatar_summary():
    """Show summary of avatar storage"""
    print("\n📊 Avatar Storage Summary:")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Count avatars by storage type
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(avatar_url) as users_with_url,
                COUNT(avatar_data) as users_with_data,
                COUNT(CASE WHEN avatar_url LIKE '/api/v1/users/%/avatar/image' THEN 1 END) as users_with_new_url,
                COUNT(CASE WHEN avatar_url LIKE '%uploads/avatars/%' THEN 1 END) as users_with_old_url
            FROM "user";
        """)
        
        result = cursor.fetchone()
        total, with_url, with_data, new_url, old_url = result
        
        print(f"  Total users: {total}")
        print(f"  Users with avatar URL: {with_url}")
        print(f"  Users with avatar data: {with_data}")
        print(f"  Users with new database URL: {new_url}")
        print(f"  Users with old file URL: {old_url}")
        
        if old_url > 0:
            print(f"  ⚠️  {old_url} users still have old file URLs")
        else:
            print(f"  ✅ All avatar URLs updated to database endpoints")
        
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    print("🚀 Fixing Avatar URLs After Rebuild")
    print("=" * 40)
    
    # Show current state
    show_avatar_summary()
    
    # Fix URLs
    fix_avatar_urls()
    
    # Test endpoints
    test_new_endpoints()
    
    # Show final state
    show_avatar_summary()
    
    print("\n✅ Avatar URL fix complete!")
    print("Users should now see avatars loading from database instead of broken file links.")

if __name__ == "__main__":
    main()