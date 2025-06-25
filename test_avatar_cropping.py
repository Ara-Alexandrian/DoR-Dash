#!/usr/bin/env python3
"""
Test script to diagnose avatar cropping issues.
This script will:
1. Create a 200x200 test image with soft edges
2. Upload it to the backend
3. Check what the backend does with it
"""

import requests
import io
from PIL import Image, ImageDraw
import base64
import json
import sys

# Backend URL
BASE_URL = "https://dd.kronisto.net/api/v1"

def create_test_avatar():
    """Create a 200x200 test image with soft edges and specific positioning"""
    # Create a transparent image
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle with soft edges (anti-aliasing)
    # Position it off-center to test if positioning is preserved
    center_x, center_y = 80, 80  # Off-center positioning
    radius = 60
    
    # Create soft edges using multiple circles with varying opacity
    for i in range(5):
        opacity = int(255 - (i * 50))
        draw.ellipse(
            [center_x - radius - i, center_y - radius - i,
             center_x + radius + i, center_y + radius + i],
            fill=(100, 150, 200, opacity)
        )
    
    # Add some text to make it identifiable
    draw.text((10, 170), "Test Avatar", fill=(255, 255, 255, 200))
    
    return img

def upload_avatar(session, user_id, image):
    """Upload avatar to the backend"""
    # Convert image to bytes
    img_buffer = io.BytesIO()
    image.save(img_buffer, 'PNG')
    img_buffer.seek(0)
    
    # Prepare the file for upload
    files = {
        'file': ('test_avatar.png', img_buffer, 'image/png')
    }
    
    # Upload the avatar
    response = session.post(
        f"{BASE_URL}/users/{user_id}/avatar",
        files=files
    )
    
    return response

def download_avatar(session, user_id):
    """Download the processed avatar from the backend"""
    response = session.get(f"{BASE_URL}/users/{user_id}/avatar/image")
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    return None

def main():
    # Get credentials from command line or use defaults
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ")
    password = sys.argv[2] if len(sys.argv) > 2 else input("Password: ")
    
    # Create session and login
    session = requests.Session()
    
    print("Logging in...")
    login_response = session.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    user_data = login_response.json()
    user_id = user_data['id']
    print(f"Logged in as user {user_id}")
    
    # Create test avatar
    print("\nCreating test avatar (200x200 with soft edges, off-center)...")
    test_avatar = create_test_avatar()
    test_avatar.save("test_avatar_original.png")
    print("Saved original as test_avatar_original.png")
    
    # Upload avatar
    print("\nUploading avatar...")
    upload_response = upload_avatar(session, user_id, test_avatar)
    print(f"Upload response: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        response_data = upload_response.json()
        print(f"Response data: {json.dumps(response_data, indent=2)}")
        
        # Check the processing field
        if 'processing' in response_data:
            print(f"\nProcessing mode: {response_data['processing']}")
            if response_data['processing'] == 'preserved':
                print("✓ Backend correctly detected 200x200 image and preserved it")
            else:
                print("✗ Backend re-processed the image instead of preserving it")
    else:
        print(f"Upload failed: {upload_response.text}")
        return
    
    # Download and check the processed avatar
    print("\nDownloading processed avatar...")
    processed_avatar = download_avatar(session, user_id)
    
    if processed_avatar:
        processed_avatar.save("test_avatar_processed.png")
        print("Saved processed avatar as test_avatar_processed.png")
        
        # Compare images
        print(f"\nOriginal size: {test_avatar.size}")
        print(f"Processed size: {processed_avatar.size}")
        
        # Check if the image was re-centered (compare pixel values at specific positions)
        orig_pixels = test_avatar.load()
        proc_pixels = processed_avatar.load()
        
        # Check a few key pixels to see if positioning was preserved
        test_positions = [(80, 80), (120, 120), (10, 170)]
        differences = 0
        
        for pos in test_positions:
            orig = orig_pixels[pos[0], pos[1]] if pos[0] < test_avatar.width and pos[1] < test_avatar.height else (0,0,0,0)
            proc = proc_pixels[pos[0], pos[1]] if pos[0] < processed_avatar.width and pos[1] < processed_avatar.height else (0,0,0)
            
            # Convert to comparable format
            if len(orig) == 4 and len(proc) == 3:
                orig = orig[:3]  # Remove alpha channel for comparison
            
            if orig[:3] != proc[:3]:
                differences += 1
                print(f"Pixel difference at {pos}: original={orig}, processed={proc}")
        
        if differences > 0:
            print(f"\n✗ Found {differences} pixel differences - image may have been re-processed")
        else:
            print("\n✓ No pixel differences found - positioning preserved")
    else:
        print("Failed to download processed avatar")

if __name__ == "__main__":
    main()