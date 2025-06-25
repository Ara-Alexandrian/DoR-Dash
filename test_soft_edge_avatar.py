#!/usr/bin/env python3
"""
Test script to specifically test soft edge preservation in avatar uploads.
This will create an avatar with soft edges and verify if they're preserved.
"""

import requests
import json
from PIL import Image, ImageDraw
import io
import numpy as np

# Configuration
BACKEND_URL = "https://dd.kronisto.net"

def create_soft_edge_avatar():
    """Create a 200x200 test image with soft edges"""
    # Create a transparent RGBA image
    image = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle with soft edges using a radial gradient
    center_x, center_y = 100, 100
    radius = 80
    
    # Create multiple circles with decreasing opacity for soft edges
    for i in range(10):
        current_radius = radius + (9 - i) * 2
        opacity = int(255 * (i + 1) / 10)
        color = (100, 150, 200, opacity)
        
        # Draw filled circle
        draw.ellipse(
            [center_x - current_radius, center_y - current_radius,
             center_x + current_radius, center_y + current_radius],
            fill=color
        )
    
    # Add some text to verify positioning
    draw.text((50, 170), "SOFT EDGE TEST", fill=(255, 255, 255, 200))
    
    # Save as PNG to preserve alpha channel
    png_buffer = io.BytesIO()
    image.save(png_buffer, format='PNG')
    png_data = png_buffer.getvalue()
    
    # Also create JPEG version (what backend converts to)
    # Convert RGBA to RGB with white background
    rgb_image = Image.new('RGB', (200, 200), (255, 255, 255))
    rgb_image.paste(image, (0, 0), image)
    
    jpeg_buffer = io.BytesIO()
    rgb_image.save(jpeg_buffer, format='JPEG', quality=90)
    jpeg_data = jpeg_buffer.getvalue()
    
    return png_data, jpeg_data, image

def analyze_soft_edges(image_data):
    """Analyze if soft edges are preserved in the image"""
    image = Image.open(io.BytesIO(image_data))
    
    # Convert to numpy array for analysis
    arr = np.array(image)
    
    # Check edges - sample pixels at the border of the circle
    center_x, center_y = 100, 100
    radius = 80
    
    # Sample points around the edge
    edge_samples = []
    for angle in range(0, 360, 45):
        x = int(center_x + radius * np.cos(np.radians(angle)))
        y = int(center_y + radius * np.sin(np.radians(angle)))
        
        # Get a small region around the edge point
        if 5 <= x < 195 and 5 <= y < 195:
            region = arr[y-5:y+5, x-5:x+5]
            # Calculate the variance in pixel values (soft edges have gradual transitions)
            variance = np.var(region)
            edge_samples.append(variance)
    
    avg_variance = np.mean(edge_samples) if edge_samples else 0
    
    # High variance indicates soft edges (gradual color transitions)
    has_soft_edges = avg_variance > 100
    
    return {
        'has_soft_edges': has_soft_edges,
        'avg_edge_variance': float(avg_variance),
        'size': image.size,
        'mode': image.mode
    }

def test_avatar_upload_with_analysis(email, password):
    """Test avatar upload and analyze soft edge preservation"""
    print("🔧 Testing avatar upload with soft edge analysis...")
    
    # Login
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        user_data = login_response.json()
        user_id = user_data['id']
        token = login_response.json().get('access_token') or login_response.cookies.get('access_token')
        
        print(f"✅ Logged in as user {user_id}")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Create test avatar with soft edges
    png_data, jpeg_data, original_image = create_soft_edge_avatar()
    print(f"✅ Created test avatar: PNG={len(png_data)} bytes, JPEG={len(jpeg_data)} bytes")
    
    # Save original for comparison
    original_image.save('test_avatar_original.png')
    print("📁 Saved original as test_avatar_original.png")
    
    # Analyze original
    original_analysis = analyze_soft_edges(png_data)
    print(f"\n📊 Original image analysis:")
    print(f"  - Size: {original_analysis['size']}")
    print(f"  - Mode: {original_analysis['mode']}")
    print(f"  - Has soft edges: {original_analysis['has_soft_edges']}")
    print(f"  - Edge variance: {original_analysis['avg_edge_variance']:.2f}")
    
    # Upload avatar
    files = {
        'file': ('test_avatar.png', png_data, 'image/png')
    }
    headers = {
        'Authorization': f'Bearer {token}'
    } if token else {}
    
    cookies = {'access_token': token} if not headers.get('Authorization') and token else {}
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/users/{user_id}/avatar",
            files=files,
            headers=headers,
            cookies=cookies
        )
        
        print(f"\n📤 Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            
            # Check if backend reports processing mode
            if 'processing' in result:
                if result['processing'] == 'preserved':
                    print("✅ Backend reports: Image was PRESERVED (not re-cropped)")
                else:
                    print("⚠️  Backend reports: Image was RE-CROPPED")
            
            # Retrieve and analyze processed avatar
            print("\n📥 Retrieving processed avatar...")
            avatar_response = requests.get(
                f"{BACKEND_URL}/api/v1/users/{user_id}/avatar/image",
                headers=headers,
                cookies=cookies
            )
            
            if avatar_response.status_code == 200:
                processed_data = avatar_response.content
                print(f"✅ Retrieved avatar: {len(processed_data)} bytes")
                
                # Save processed image
                with open('test_avatar_processed.jpg', 'wb') as f:
                    f.write(processed_data)
                print("📁 Saved processed as test_avatar_processed.jpg")
                
                # Analyze processed image
                processed_analysis = analyze_soft_edges(processed_data)
                print(f"\n📊 Processed image analysis:")
                print(f"  - Size: {processed_analysis['size']}")
                print(f"  - Mode: {processed_analysis['mode']}")
                print(f"  - Has soft edges: {processed_analysis['has_soft_edges']}")
                print(f"  - Edge variance: {processed_analysis['avg_edge_variance']:.2f}")
                
                # Compare results
                print("\n🔍 Comparison:")
                if processed_analysis['has_soft_edges']:
                    print("✅ Soft edges PRESERVED!")
                else:
                    print("❌ Soft edges LOST - image may have been re-processed")
                
                variance_change = abs(original_analysis['avg_edge_variance'] - processed_analysis['avg_edge_variance'])
                if variance_change < 50:
                    print("✅ Edge characteristics similar to original")
                else:
                    print(f"⚠️  Edge characteristics changed significantly (Δ={variance_change:.2f})")
                
                return True
            else:
                print(f"❌ Avatar retrieval failed: {avatar_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
    
    return False

def main():
    """Main test function"""
    print("🚀 Soft Edge Avatar Preservation Test")
    print("=" * 50)
    
    # Get credentials
    email = input("Email: ")
    password = input("Password: ")
    
    success = test_avatar_upload_with_analysis(email, password)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test completed successfully")
        print("\n📌 Next steps:")
        print("1. Compare test_avatar_original.png with test_avatar_processed.jpg")
        print("2. Look for differences in edge softness and positioning")
        print("3. Check if the circle is centered differently")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    main()