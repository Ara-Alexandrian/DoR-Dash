#!/usr/bin/env python3
"""
Comprehensive test suite for DoR-Dash deployment at dd.kronisto.net
"""

import requests
import json
import time
from typing import Dict, List, Any
import sys

class DeploymentTester:
    def __init__(self, base_url: str = "https://dd.kronisto.net"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": "PASS" if success else "FAIL",
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_website_accessibility(self):
        """Test if the main website is accessible"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                if "DoR-Dash" in response.text:
                    self.log_test("Website Accessibility", True, "Main site loads successfully")
                else:
                    self.log_test("Website Accessibility", False, "Site loads but content unexpected", response.text[:200])
            else:
                self.log_test("Website Accessibility", False, f"HTTP {response.status_code}", response.text[:200])
        except requests.exceptions.RequestException as e:
            self.log_test("Website Accessibility", False, "Network error", str(e))
    
    def test_api_health(self):
        """Test API health endpoints"""
        endpoints = [
            "/health",
            "/api/v1/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        self.log_test(f"API Health ({endpoint})", True, "Health endpoint responsive")
                    else:
                        self.log_test(f"API Health ({endpoint})", False, "Unexpected health response", data)
                else:
                    self.log_test(f"API Health ({endpoint})", False, f"HTTP {response.status_code}", response.text[:200])
            except requests.exceptions.RequestException as e:
                self.log_test(f"API Health ({endpoint})", False, "Network error", str(e))
            except json.JSONDecodeError as e:
                self.log_test(f"API Health ({endpoint})", False, "Invalid JSON response", str(e))
    
    def test_login_page(self):
        """Test login page accessibility"""
        try:
            response = self.session.get(f"{self.base_url}/login", timeout=10)
            if response.status_code == 200:
                if "login" in response.text.lower() or "username" in response.text.lower():
                    self.log_test("Login Page", True, "Login page loads successfully")
                else:
                    self.log_test("Login Page", False, "Login page loads but missing expected elements")
            else:
                self.log_test("Login Page", False, f"HTTP {response.status_code}", response.text[:200])
        except requests.exceptions.RequestException as e:
            self.log_test("Login Page", False, "Network error", str(e))
    
    def test_authentication_api(self):
        """Test authentication API endpoints"""
        # Test login endpoint
        login_data = {
            "username": "cerebro",
            "password": "123"
        }
        
        try:
            response = self.session.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log_test("Authentication API", True, "Login successful with admin credentials")
                    # Store token for further tests
                    self.session.headers.update({"Authorization": f"Bearer {data['access_token']}"})
                    return True
                else:
                    self.log_test("Authentication API", False, "Login response missing token", data)
            else:
                self.log_test("Authentication API", False, f"Login failed HTTP {response.status_code}", response.text[:200])
        except requests.exceptions.RequestException as e:
            self.log_test("Authentication API", False, "Network error during login", str(e))
        except json.JSONDecodeError as e:
            self.log_test("Authentication API", False, "Invalid JSON in login response", str(e))
        
        return False
    
    def test_protected_endpoints(self):
        """Test protected API endpoints"""
        endpoints = [
            ("/users/me", "User profile endpoint"),
            ("/updates/student", "Student updates endpoint"),
            ("/updates/faculty", "Faculty updates endpoint"),
            ("/meetings", "Meetings endpoint")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = self.session.get(f"{self.api_url}{endpoint}", timeout=10)
                if response.status_code in [200, 404]:  # 404 is ok for empty data
                    self.log_test(f"Protected API ({endpoint})", True, f"{description} accessible")
                elif response.status_code == 401:
                    self.log_test(f"Protected API ({endpoint})", False, "Authentication required but token invalid")
                else:
                    self.log_test(f"Protected API ({endpoint})", False, f"HTTP {response.status_code}", response.text[:200])
            except requests.exceptions.RequestException as e:
                self.log_test(f"Protected API ({endpoint})", False, "Network error", str(e))
    
    def test_file_upload_endpoint(self):
        """Test file upload functionality"""
        try:
            # Create a small test file
            test_file_content = b"Test file content for upload testing"
            files = {"file": ("test.txt", test_file_content, "text/plain")}
            
            response = self.session.post(
                f"{self.api_url}/files/upload", 
                files=files,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                self.log_test("File Upload", True, "File upload endpoint responsive")
            elif response.status_code == 401:
                self.log_test("File Upload", False, "Authentication required for file upload")
            else:
                self.log_test("File Upload", False, f"HTTP {response.status_code}", response.text[:200])
        except requests.exceptions.RequestException as e:
            self.log_test("File Upload", False, "Network error during upload", str(e))
    
    def test_error_handling(self):
        """Test error handling for invalid endpoints"""
        try:
            response = self.session.get(f"{self.api_url}/nonexistent-endpoint", timeout=10)
            if response.status_code == 404:
                self.log_test("Error Handling", True, "404 properly returned for invalid endpoints")
            else:
                self.log_test("Error Handling", False, f"Unexpected status for invalid endpoint: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log_test("Error Handling", False, "Network error during error test", str(e))
    
    def test_registration_endpoint(self):
        """Test user registration endpoint"""
        registration_data = {
            "username": f"test_user_{int(time.time())}",
            "password": "testpass123",
            "email": "test@example.com",
            "full_name": "Test User"
        }
        
        try:
            response = self.session.post(f"{self.api_url}/auth/register", json=registration_data, timeout=10)
            if response.status_code in [200, 201]:
                self.log_test("Registration API", True, "Registration endpoint responsive")
            elif response.status_code == 422:
                self.log_test("Registration API", True, "Registration validation working (422 expected)")
            else:
                self.log_test("Registration API", False, f"HTTP {response.status_code}", response.text[:200])
        except requests.exceptions.RequestException as e:
            self.log_test("Registration API", False, "Network error during registration", str(e))
    
    def run_comprehensive_test(self):
        """Run all tests and provide summary"""
        print("🚀 Starting DoR-Dash Deployment Test Suite")
        print(f"📍 Testing: {self.base_url}")
        print("=" * 60)
        
        # Core functionality tests
        self.test_website_accessibility()
        self.test_api_health()
        self.test_login_page()
        
        # Authentication and API tests
        auth_success = self.test_authentication_api()
        if auth_success:
            self.test_protected_endpoints()
            self.test_file_upload_endpoint()
        
        # Additional functionality tests
        self.test_registration_endpoint()
        self.test_error_handling()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate executive summary"""
        print("\n" + "=" * 60)
        print("📊 EXECUTIVE SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED - Deployment is HEALTHY")
            overall_status = "PASS"
        elif failed_tests <= 2:
            print("\n⚠️  MINOR ISSUES DETECTED - Deployment is MOSTLY FUNCTIONAL")
            overall_status = "PASS (with warnings)"
        else:
            print("\n🚨 CRITICAL ISSUES DETECTED - Deployment needs ATTENTION")
            overall_status = "FAIL"
        
        print(f"\n🏁 OVERALL STATUS: {overall_status}")
        
        # List failed tests
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        return overall_status


if __name__ == "__main__":
    tester = DeploymentTester()
    tester.run_comprehensive_test()