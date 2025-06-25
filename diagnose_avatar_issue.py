#!/usr/bin/env python3
"""
Comprehensive diagnostic script for avatar cropping issue.
This will help us understand exactly what's happening with soft-edged avatars.
"""

import requests
import json
from PIL import Image, ImageDraw, ImageFilter
import io
import base64
import hashlib

# Configuration
API_URL = "https://dd.kronisto.net/api/v1"

def create_diagnostic_avatar():
    """Create a 200x200 avatar with specific features to test preservation"""
    # Create RGBA image with transparency
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle with soft edges positioned off-center
    # This will help us detect if the image is re-centered
    center_x, center_y = 70, 70  # Intentionally off-center
    
    # Create soft edge circle using gradient
    for radius in range(80, 60, -1):
        alpha = int((80 - radius) * 12)  # Gradual fade
        color = (100, 150, 200, alpha)
        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius + 1, center_y + radius + 1],
            fill=color
        )
    
    # Add positioning markers
    draw.rectangle([0, 0, 10, 10], fill=(255, 0, 0, 255))  # Top-left red square
    draw.rectangle([190, 190, 200, 200], fill=(0, 255, 0, 255))  # Bottom-right green square
    draw.text((10, 180), "TEST", fill=(255, 255, 255, 200))
    
    return img

def image_to_base64(image, format='PNG'):
    """Convert PIL image to base64 string"""
    buffer = io.BytesIO()
    if format == 'JPEG' and image.mode == 'RGBA':
        # Convert RGBA to RGB for JPEG
        rgb_img = Image.new('RGB', image.size, (255, 255, 255))
        rgb_img.paste(image, (0, 0), image)
        rgb_img.save(buffer, format=format, quality=90)
    else:
        image.save(buffer, format=format, quality=90 if format == 'JPEG' else None)
    
    return base64.b64encode(buffer.getvalue()).decode()

def calculate_image_hash(image_data):
    """Calculate hash of image data for comparison"""
    return hashlib.md5(image_data).hexdigest()

def analyze_image_positioning(image_data):
    """Analyze if image positioning and soft edges are preserved"""
    img = Image.open(io.BytesIO(image_data))
    
    # Convert to RGBA for analysis
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    pixels = img.load()
    
    # Check corner markers
    top_left = pixels[5, 5]
    bottom_right = pixels[195, 195]
    
    # Check if red square is still in top-left
    has_top_left_marker = top_left[0] > 200 and top_left[1] < 50
    
    # Check if green square is still in bottom-right  
    has_bottom_right_marker = bottom_right[1] > 200 and bottom_right[0] < 50
    
    # Sample the edge of the circle to check for soft edges
    edge_samples = []
    center_x, center_y = 70, 70
    radius = 70
    
    for angle in range(0, 360, 30):
        import math
        x = int(center_x + radius * math.cos(math.radians(angle)))
        y = int(center_y + radius * math.sin(math.radians(angle)))
        
        if 0 <= x < 200 and 0 <= y < 200:
            pixel = pixels[x, y]
            # Check alpha channel or color variation
            edge_samples.append(pixel)
    
    # Calculate edge softness (variation in alpha/color values)
    if edge_samples:
        alpha_values = [p[3] if len(p) > 3 else 255 for p in edge_samples]
        alpha_variation = max(alpha_values) - min(alpha_values)
        has_soft_edges = alpha_variation > 50
    else:
        has_soft_edges = False
    
    return {
        'has_top_left_marker': has_top_left_marker,
        'has_bottom_right_marker': has_bottom_right_marker,
        'has_soft_edges': has_soft_edges,
        'markers_preserved': has_top_left_marker and has_bottom_right_marker,
        'positioning_preserved': has_top_left_marker,  # If top-left is still there, positioning wasn't changed
        'size': img.size,
        'mode': img.mode
    }

def test_avatar_flow(email, password):
    """Test the complete avatar upload and retrieval flow"""
    print("🔍 Avatar Cropping Diagnostic Test")
    print("=" * 50)
    
    # Create diagnostic avatar
    test_img = create_diagnostic_avatar()
    test_img.save('diagnostic_original.png')
    print("✅ Created diagnostic avatar (saved as diagnostic_original.png)")
    print("   - Off-center circle at (70, 70)")
    print("   - Red marker in top-left corner")
    print("   - Green marker in bottom-right corner")
    print("   - Soft edges with alpha gradient")
    
    # Convert to bytes for upload
    img_buffer = io.BytesIO()
    test_img.save(img_buffer, 'PNG')
    img_data = img_buffer.getvalue()
    original_hash = calculate_image_hash(img_data)
    
    # Login
    print(f"\n🔐 Logging in as {email}...")
    session = requests.Session()
    
    login_resp = session.post(f"{API_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    
    if login_resp.status_code != 200:
        print(f"❌ Login failed: {login_resp.status_code}")
        print(login_resp.text)
        return
    
    user_data = login_resp.json()
    user_id = user_data['id']
    print(f"✅ Logged in successfully (User ID: {user_id})")
    
    # Upload avatar
    print(f"\n📤 Uploading 200x200 PNG avatar...")
    files = {'file': ('avatar.png', img_data, 'image/png')}
    
    upload_resp = session.post(f"{API_URL}/users/{user_id}/avatar", files=files)
    
    if upload_resp.status_code != 200:
        print(f"❌ Upload failed: {upload_resp.status_code}")
        print(upload_resp.text)
        return
    
    upload_result = upload_resp.json()
    print("✅ Upload successful!")
    print(f"📋 Server response: {json.dumps(upload_result, indent=2)}")
    
    # Check processing field
    if 'processing' in upload_result:
        if upload_result['processing'] == 'preserved':
            print("✅ Backend reports: Image was PRESERVED")
        else:
            print("⚠️  Backend reports: Image was CROPPED")
    
    # Retrieve avatar
    print(f"\n📥 Retrieving processed avatar...")
    avatar_resp = session.get(f"{API_URL}/users/{user_id}/avatar/image")
    
    if avatar_resp.status_code != 200:
        print(f"❌ Retrieval failed: {avatar_resp.status_code}")
        return
    
    processed_data = avatar_resp.content
    processed_hash = calculate_image_hash(processed_data)
    
    # Save processed image
    with open('diagnostic_processed.jpg', 'wb') as f:
        f.write(processed_data)
    print("✅ Retrieved and saved as diagnostic_processed.jpg")
    
    # Analyze results
    print(f"\n📊 Analysis:")
    print(f"Original size: {len(img_data)} bytes (MD5: {original_hash[:8]}...)")
    print(f"Processed size: {len(processed_data)} bytes (MD5: {processed_hash[:8]}...)")
    
    analysis = analyze_image_positioning(processed_data)
    
    print(f"\n🔍 Image Analysis Results:")
    print(f"  - Size: {analysis['size']}")
    print(f"  - Mode: {analysis['mode']}")
    print(f"  - Top-left marker preserved: {'✅' if analysis['has_top_left_marker'] else '❌'}")
    print(f"  - Bottom-right marker preserved: {'✅' if analysis['has_bottom_right_marker'] else '❌'}")
    print(f"  - Soft edges detected: {'✅' if analysis['has_soft_edges'] else '❌'}")
    
    print(f"\n📋 Conclusions:")
    if analysis['positioning_preserved']:
        print("✅ Positioning was PRESERVED - avatar not re-centered")
    else:
        print("❌ Positioning was CHANGED - avatar was re-centered")
    
    if analysis['has_soft_edges']:
        print("✅ Soft edges were PRESERVED")
    else:
        print("❌ Soft edges were LOST - hard crop applied")
    
    if not analysis['markers_preserved']:
        print("⚠️  Corner markers lost - significant cropping occurred")
    
    # Test with JPEG upload too
    print(f"\n🔄 Testing with JPEG format...")
    jpeg_buffer = io.BytesIO()
    rgb_img = Image.new('RGB', (200, 200), (255, 255, 255))
    rgb_img.paste(test_img, (0, 0), test_img)
    rgb_img.save(jpeg_buffer, 'JPEG', quality=90)
    jpeg_data = jpeg_buffer.getvalue()
    
    files = {'file': ('avatar.jpg', jpeg_data, 'image/jpeg')}
    upload_resp2 = session.post(f"{API_URL}/users/{user_id}/avatar", files=files)
    
    if upload_resp2.status_code == 200:
        result2 = upload_resp2.json()
        print(f"✅ JPEG upload successful")
        print(f"   Processing mode: {result2.get('processing', 'unknown')}")
    
    print("\n" + "=" * 50)
    print("Diagnostic complete. Check diagnostic_original.png and diagnostic_processed.jpg")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        email = input("Email: ")
        password = input("Password: ")
    
    test_avatar_flow(email, password)