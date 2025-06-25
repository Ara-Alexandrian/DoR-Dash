#!/usr/bin/env python3
"""
Debug script to test avatar upload and see what's actually happening
"""

import requests
import json
from PIL import Image
import io

# Configuration
BACKEND_URL = "http://172.30.98.177:8000"
TEST_USER_ID = 2  # Cerebro user

def create_test_avatar():
    """Create a 200x200 test image with visible positioning"""
    # Create a 200x200 image with a gradient and text to show positioning
    image = Image.new('RGB', (200, 200), color='lightblue')
    
    # Add some visual elements to show if positioning is preserved
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    
    # Draw a red circle in the top-left to test positioning
    draw.ellipse([10, 10, 50, 50], fill='red')
    
    # Draw text in bottom-right
    try:
        draw.text((120, 160), "TEST", fill='black')
    except:
        # Fallback if font fails
        draw.rectangle([120, 160, 180, 190], fill='black')
    
    # Convert to bytes
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=90)
    return buffer.getvalue()

def get_auth_token():
    """Get authentication token"""
    try:
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
            return token_data.get("access_token")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_avatar_upload():
    """Test avatar upload with debug info"""
    print("🔧 Testing avatar upload with debug info...")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return False
    
    # Create test image
    image_data = create_test_avatar()
    print(f"Created test image: {len(image_data)} bytes")
    
    # Upload avatar
    files = {
        'file': ('test_avatar.jpg', image_data, 'image/jpeg')
    }
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/users/{TEST_USER_ID}/avatar",
            files=files,
            headers=headers
        )
        
        print(f"Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Test retrieval
            print("\n🔧 Testing avatar retrieval...")
            avatar_response = requests.get(f"{BACKEND_URL}/api/v1/users/{TEST_USER_ID}/avatar/image")
            
            if avatar_response.status_code == 200:
                avatar_data = avatar_response.content
                print(f"✅ Retrieved avatar: {len(avatar_data)} bytes")
                print(f"Content-Type: {avatar_response.headers.get('content-type')}")
                print(f"Avatar Source: {avatar_response.headers.get('x-avatar-source', 'unknown')}")
                
                # Check if the retrieved image matches our test pattern
                try:
                    retrieved_image = Image.open(io.BytesIO(avatar_data))
                    print(f"Retrieved image size: {retrieved_image.size}")
                    print(f"Retrieved image mode: {retrieved_image.mode}")
                    
                    # Save for manual inspection
                    retrieved_image.save('/tmp/retrieved_avatar.jpg')
                    print("Saved retrieved avatar to /tmp/retrieved_avatar.jpg for inspection")
                    
                    return True
                except Exception as e:
                    print(f"❌ Error analyzing retrieved image: {e}")
            else:
                print(f"❌ Avatar retrieval failed: {avatar_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
    
    return False

def check_backend_logs():
    """Check backend logs for debug messages"""
    print("\n🔧 Checking backend logs...")
    
    try:
        # Try to read recent backend logs
        with open('/config/workspace/gitea/DoR-Dash/logs/backend.log', 'r') as f:
            lines = f.readlines()
            
        # Get last 20 lines
        recent_lines = lines[-20:]
        
        print("Recent backend log entries:")
        for line in recent_lines:
            if 'avatar' in line.lower() or 'user' in line.lower():
                print(f"  {line.strip()}")
                
    except Exception as e:
        print(f"❌ Could not read backend logs: {e}")

def main():
    """Main test function"""
    print("🚀 Debug Avatar Upload Test")
    print("=" * 40)
    
    success = test_avatar_upload()
    
    if success:
        check_backend_logs()
    
    print("\n" + "=" * 40)
    print("Test completed. Check the results above.")

if __name__ == "__main__":
    main()