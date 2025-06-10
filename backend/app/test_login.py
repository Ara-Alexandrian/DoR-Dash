#!/usr/bin/env python3

import os
import sys
import requests

# Test the login endpoint directly

def test_login():
    """Test the login endpoint"""
    url = "http://172.30.98.21:8000/api/v1/auth/login"
    
    # Login data
    data = {
        "username": "cerebro",
        "password": "123"
    }
    
    print(f"🔍 Testing login endpoint: {url}")
    print(f"📝 Login data: {data}")
    
    try:
        response = requests.post(url, data=data)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            print(f"🔑 Response: {response.json()}")
        else:
            print("❌ Login failed!")
            print(f"💥 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_login()