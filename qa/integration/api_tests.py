#!/usr/bin/env python3
"""
Basic API integration tests for DoR-Dash system
Tests basic endpoint availability and response codes
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://172.30.98.177:8000"
FRONTEND_URL = "http://172.30.98.177:1717"

def test_endpoint(url, expected_status=200, method="GET", data=None, headers=None):
    """Test a single endpoint and return results"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        result = {
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "success": response.status_code == expected_status,
            "response_time": response.elapsed.total_seconds(),
            "error": None
        }
        
        # Try to parse JSON response
        try:
            result["response_body"] = response.json()
        except:
            result["response_body"] = response.text[:200] if response.text else ""
            
        return result
        
    except Exception as e:
        return {
            "url": url,
            "method": method,
            "status_code": None,
            "expected_status": expected_status,
            "success": False,
            "response_time": None,
            "error": str(e),
            "response_body": None
        }

def run_api_tests():
    """Run comprehensive API tests"""
    print("DoR-Dash API Integration Tests")
    print("=" * 50)
    print(f"Backend URL: {BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Test Time: {datetime.now()}")
    print()
    
    # Define test cases
    test_cases = [
        # Health and basic endpoints
        {"url": f"{BASE_URL}/health", "expected_status": 200},
        {"url": f"{BASE_URL}/", "expected_status": 200},
        {"url": f"{BASE_URL}/docs", "expected_status": 200},
        
        # Frontend
        {"url": FRONTEND_URL, "expected_status": 200},
        
        # API endpoints (without auth - should return 401/403)
        {"url": f"{BASE_URL}/api/v1/meetings/", "expected_status": 401},
        {"url": f"{BASE_URL}/api/v1/users/me", "expected_status": 401},
        {"url": f"{BASE_URL}/api/v1/updates/", "expected_status": 401},
        {"url": f"{BASE_URL}/api/v1/faculty-updates/", "expected_status": 401},
        {"url": f"{BASE_URL}/api/v1/meetings/updates", "expected_status": 401},
        
        # Public/registration endpoints
        {"url": f"{BASE_URL}/api/v1/auth/register", "method": "POST", "expected_status": 422, 
         "data": {}},  # Should fail validation with empty data
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"Testing {test_case['method'] if 'method' in test_case else 'GET'} {test_case['url']}")
        result = test_endpoint(**test_case)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ PASS - {result['status_code']} ({result['response_time']:.3f}s)")
            passed += 1
        else:
            print(f"  ❌ FAIL - Expected {result['expected_status']}, got {result['status_code']}")
            if result["error"]:
                print(f"     Error: {result['error']}")
            failed += 1
        print()
    
    # Summary
    print("=" * 50)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print(f"Success rate: {(passed/(passed+failed)*100):.1f}%")
    
    return {
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    try:
        results = run_api_tests()
        sys.exit(0 if results["failed"] == 0 else 1)
    except Exception as e:
        print(f"Test runner failed: {e}")
        sys.exit(1)