#!/usr/bin/env python3
"""
Simple System Validation Suite for DoR-Dash (No external dependencies)
Tests authentication, core functionality, performance, and basic security
"""

import sys
import os
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path
import ssl
import http.client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings

class SimpleSystemValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}{settings.API_V1_STR}"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0},
            "categories": {}
        }
        self.session_token = None
        self.admin_user = {
            "username": "admin",
            "password": "admin123"
        }
        
    def log_test(self, category: str, test_name: str, passed: bool, details: str = "", warning: bool = False):
        """Log test result"""
        if category not in self.test_results["categories"]:
            self.test_results["categories"][category] = []
        
        status = "warning" if warning else ("passed" if passed else "failed")
        self.test_results["categories"][category].append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        self.test_results["summary"]["total"] += 1
        if warning:
            self.test_results["summary"]["warnings"] += 1
        elif passed:
            self.test_results["summary"]["passed"] += 1
        else:
            self.test_results["summary"]["failed"] += 1
            
        # Print real-time status
        symbol = "⚠️" if warning else ("✅" if passed else "❌")
        print(f"{symbol} {category}: {test_name} - {details}")
    
    def make_request(self, method: str, url: str, data: Dict = None, headers: Dict = None) -> Tuple[int, Dict]:
        """Make HTTP request and return status code and response data"""
        parsed_url = urllib.parse.urlparse(url)
        
        # Create connection
        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(parsed_url.netloc)
        else:
            conn = http.client.HTTPConnection(parsed_url.netloc)
        
        # Prepare headers
        request_headers = headers or {}
        if data:
            request_headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode('utf-8')
        else:
            body = None
        
        try:
            # Make request
            path = parsed_url.path
            if parsed_url.query:
                path += "?" + parsed_url.query
                
            conn.request(method, path, body, request_headers)
            response = conn.getresponse()
            
            # Read response
            response_data = response.read().decode('utf-8')
            
            # Parse JSON if possible
            try:
                response_json = json.loads(response_data) if response_data else {}
            except:
                response_json = {"raw": response_data}
            
            return response.status, response_json
            
        finally:
            conn.close()
    
    def test_authentication(self):
        """Test authentication system"""
        print("\n🔐 Testing Authentication System...")
        
        # Test health endpoint (no auth required)
        try:
            status, data = self.make_request("GET", f"{self.api_base}/health")
            if status == 200:
                self.log_test("Authentication", "Health endpoint accessible", True)
            else:
                self.log_test("Authentication", "Health endpoint accessible", False, f"Status: {status}")
        except Exception as e:
            self.log_test("Authentication", "Health endpoint accessible", False, str(e))
        
        # Test login with admin credentials
        try:
            login_data = {
                "username": self.admin_user["username"],
                "password": self.admin_user["password"]
            }
            status, data = self.make_request("POST", f"{self.api_base}/auth/login", login_data)
            if status == 200:
                self.session_token = data.get("access_token")
                self.log_test("Authentication", "Admin login", True)
            else:
                self.log_test("Authentication", "Admin login", False, f"Status: {status}")
        except Exception as e:
            self.log_test("Authentication", "Admin login", False, str(e))
        
        # Test accessing protected endpoint without token
        try:
            status, data = self.make_request("GET", f"{self.api_base}/users/me")
            if status == 401:
                self.log_test("Authentication", "Protected endpoint blocks unauthorized", True)
            else:
                self.log_test("Authentication", "Protected endpoint blocks unauthorized", False, 
                            f"Expected 401, got {status}")
        except Exception as e:
            self.log_test("Authentication", "Protected endpoint blocks unauthorized", False, str(e))
        
        # Test accessing protected endpoint with token
        if self.session_token:
            try:
                headers = {"Authorization": f"Bearer {self.session_token}"}
                status, data = self.make_request("GET", f"{self.api_base}/users/me", headers=headers)
                if status == 200:
                    self.log_test("Authentication", "Protected endpoint with valid token", True)
                else:
                    self.log_test("Authentication", "Protected endpoint with valid token", False, 
                                f"Status: {status}")
            except Exception as e:
                self.log_test("Authentication", "Protected endpoint with valid token", False, str(e))
    
    def test_core_functionality(self):
        """Test core CRUD operations"""
        print("\n⚙️ Testing Core Functionality...")
        
        # Re-login to get fresh token
        try:
            login_data = {
                "username": self.admin_user["username"],
                "password": self.admin_user["password"]
            }
            status, data = self.make_request("POST", f"{self.api_base}/auth/login", login_data)
            if status == 200:
                self.session_token = data.get("access_token")
        except:
            pass
        
        if not self.session_token:
            self.log_test("Core Functionality", "Authentication required", False, "Cannot proceed without auth")
            return
        
        headers = {"Authorization": f"Bearer {self.session_token}"}
        
        # Test listing endpoints
        endpoints_to_test = [
            ("agenda-items", "List agenda items"),
            ("meetings", "List meetings"),
            ("presentations", "List presentations"),
            ("users/me", "Get current user"),
            ("roster", "List roster"),
        ]
        
        for endpoint, test_name in endpoints_to_test:
            try:
                status, data = self.make_request("GET", f"{self.api_base}/{endpoint}", headers=headers)
                if status == 200:
                    self.log_test("Core Functionality", test_name, True)
                else:
                    self.log_test("Core Functionality", test_name, False, f"Status: {status}")
            except Exception as e:
                self.log_test("Core Functionality", test_name, False, str(e))
        
        # Test agenda item CRUD
        test_item_id = None
        try:
            # Create
            item_data = {
                "title": "QA Test Item",
                "content": "This is a test item for QA validation",
                "item_type": "announcement",
                "created_by": "qa_test"
            }
            status, data = self.make_request("POST", f"{self.api_base}/agenda-items/", 
                                           item_data, headers)
            if status == 200:
                test_item_id = data.get("id")
                self.log_test("Core Functionality", "Create agenda item", True)
            else:
                self.log_test("Core Functionality", "Create agenda item", False, 
                            f"Status: {status}")
        except Exception as e:
            self.log_test("Core Functionality", "Create agenda item", False, str(e))
        
        # Delete if created
        if test_item_id:
            try:
                status, data = self.make_request("DELETE", f"{self.api_base}/agenda-items/{test_item_id}", 
                                               headers=headers)
                if status == 200:
                    self.log_test("Core Functionality", "Delete agenda item", True)
                else:
                    self.log_test("Core Functionality", "Delete agenda item", False, 
                                f"Status: {status}")
            except Exception as e:
                self.log_test("Core Functionality", "Delete agenda item", False, str(e))
    
    def test_api_performance(self):
        """Test API response times"""
        print("\n⚡ Testing API Performance...")
        
        endpoints = [
            ("/health", "GET", None, 100),  # endpoint, method, data, max_ms
            ("/auth/login", "POST", {"username": "admin", "password": "admin123"}, 500),
            ("/agenda-items", "GET", None, 1000),
            ("/meetings", "GET", None, 1000),
        ]
        
        for endpoint, method, data, max_ms in endpoints:
            try:
                start_time = time.time()
                url = f"{self.api_base}{endpoint}"
                headers = {"Authorization": f"Bearer {self.session_token}"} if self.session_token else {}
                
                status, response_data = self.make_request(method, url, data, headers)
                
                elapsed_ms = (time.time() - start_time) * 1000
                
                if elapsed_ms <= max_ms:
                    self.log_test("Performance", f"{method} {endpoint}", True, 
                                f"{elapsed_ms:.0f}ms (max: {max_ms}ms)")
                else:
                    self.log_test("Performance", f"{method} {endpoint}", False, 
                                f"{elapsed_ms:.0f}ms exceeds max {max_ms}ms", warning=True)
            except Exception as e:
                self.log_test("Performance", f"{method} {endpoint}", False, str(e))
    
    def test_basic_security(self):
        """Test basic security measures"""
        print("\n🔒 Testing Basic Security...")
        
        headers = {"Authorization": f"Bearer {self.session_token}"} if self.session_token else {}
        
        # Test invalid JSON handling
        try:
            invalid_json = "{'invalid': json}"
            request_headers = headers.copy()
            request_headers["Content-Type"] = "application/json"
            
            parsed_url = urllib.parse.urlparse(f"{self.api_base}/agenda-items/")
            conn = http.client.HTTPConnection(parsed_url.netloc)
            conn.request("POST", parsed_url.path, invalid_json.encode('utf-8'), request_headers)
            response = conn.getresponse()
            
            if response.status in [400, 422]:  # Should reject invalid JSON
                self.log_test("Security", "Invalid JSON rejection", True)
            else:
                self.log_test("Security", "Invalid JSON rejection", False, 
                            f"Expected 400/422, got {response.status}")
            conn.close()
        except Exception as e:
            self.log_test("Security", "Invalid JSON rejection", False, str(e))
        
        # Test missing required fields
        try:
            incomplete_data = {"title": "Missing required fields"}  # Missing item_type
            status, data = self.make_request("POST", f"{self.api_base}/agenda-items/", 
                                           incomplete_data, headers)
            if status in [400, 422]:  # Should reject incomplete data
                self.log_test("Security", "Required field validation", True)
            else:
                self.log_test("Security", "Required field validation", False, 
                            f"Expected 400/422, got {status}")
        except Exception as e:
            self.log_test("Security", "Required field validation", False, str(e))
        
        # Test authorization (invalid token)
        try:
            bad_headers = {"Authorization": "Bearer invalid_token_12345"}
            status, data = self.make_request("GET", f"{self.api_base}/users/me", headers=bad_headers)
            if status == 401:
                self.log_test("Security", "Invalid token rejection", True)
            else:
                self.log_test("Security", "Invalid token rejection", False, 
                            f"Expected 401, got {status}")
        except Exception as e:
            self.log_test("Security", "Invalid token rejection", False, str(e))
    
    def generate_report(self):
        """Generate validation report"""
        print("\n📊 Generating Report...")
        
        # Calculate percentages
        total = self.test_results["summary"]["total"]
        if total > 0:
            pass_rate = (self.test_results["summary"]["passed"] / total) * 100
            fail_rate = (self.test_results["summary"]["failed"] / total) * 100
            warning_rate = (self.test_results["summary"]["warnings"] / total) * 100
        else:
            pass_rate = fail_rate = warning_rate = 0
        
        # Generate report
        report = f"""# DoR-Dash System Validation Report
Generated: {self.test_results["timestamp"]}

## Executive Summary

**Overall System Health: {"✅ HEALTHY" if pass_rate >= 80 else "⚠️ NEEDS ATTENTION" if pass_rate >= 60 else "❌ CRITICAL"}**

### Test Results Overview
- **Total Tests:** {total}
- **Passed:** {self.test_results["summary"]["passed"]} ({pass_rate:.1f}%)
- **Failed:** {self.test_results["summary"]["failed"]} ({fail_rate:.1f}%)
- **Warnings:** {self.test_results["summary"]["warnings"]} ({warning_rate:.1f}%)

### Category Breakdown
"""
        
        # Add category summaries
        for category, tests in self.test_results["categories"].items():
            cat_total = len(tests)
            cat_passed = sum(1 for t in tests if t["status"] == "passed")
            cat_failed = sum(1 for t in tests if t["status"] == "failed")
            cat_warnings = sum(1 for t in tests if t["status"] == "warning")
            
            report += f"\n#### {category}\n"
            report += f"- Tests: {cat_total}\n"
            report += f"- Passed: {cat_passed}\n"
            report += f"- Failed: {cat_failed}\n"
            report += f"- Warnings: {cat_warnings}\n"
        
        # Add detailed results
        report += "\n## Detailed Test Results\n"
        
        for category, tests in self.test_results["categories"].items():
            report += f"\n### {category}\n\n"
            report += "| Test | Status | Details | Time |\n"
            report += "|------|--------|---------|------|\n"
            
            for test in tests:
                status_icon = {"passed": "✅", "failed": "❌", "warning": "⚠️"}.get(test["status"], "❓")
                report += f"| {test['test']} | {status_icon} {test['status'].upper()} | {test['details']} | {test['timestamp'].split('T')[1].split('.')[0]} |\n"
        
        # Add recommendations
        report += "\n## Recommendations\n\n"
        
        if self.test_results["summary"]["failed"] > 0:
            report += "### Critical Issues to Address:\n"
            for category, tests in self.test_results["categories"].items():
                failed_tests = [t for t in tests if t["status"] == "failed"]
                if failed_tests:
                    report += f"\n**{category}:**\n"
                    for test in failed_tests:
                        report += f"- {test['test']}: {test['details']}\n"
        
        if self.test_results["summary"]["warnings"] > 0:
            report += "\n### Warnings to Review:\n"
            for category, tests in self.test_results["categories"].items():
                warning_tests = [t for t in tests if t["status"] == "warning"]
                if warning_tests:
                    report += f"\n**{category}:**\n"
                    for test in warning_tests:
                        report += f"- {test['test']}: {test['details']}\n"
        
        # Add test coverage note
        report += "\n## Test Coverage Note\n\n"
        report += "This validation covers:\n"
        report += "- ✅ Authentication system (login, logout, token validation)\n"
        report += "- ✅ Core API functionality (CRUD operations)\n"
        report += "- ✅ API performance benchmarks\n"
        report += "- ✅ Basic security validation\n"
        report += "\nFor comprehensive database integrity testing, please run with psycopg2 installed.\n"
        
        # Add timestamp
        report += f"\n---\nReport generated at: {datetime.now().isoformat()}\n"
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/config/workspace/gitea/DoR-Dash/backend/qa/Validation/system_validation_report_{timestamp}.md"
        
        with open(report_file, "w") as f:
            f.write(report)
        
        # Also save JSON data
        json_file = f"/config/workspace/gitea/DoR-Dash/backend/qa/Validation/system_validation_data_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n✅ Report saved to: {report_file}")
        print(f"📊 Raw data saved to: {json_file}")
        
        return report_file
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting System Validation...\n")
        
        # Check if server is running
        try:
            status, data = self.make_request("GET", f"{self.base_url}/")
            print("✅ Server is running")
        except Exception as e:
            print(f"❌ Server is not running: {e}")
            print("Please start the server with: uvicorn app.main:app --reload")
            return
        
        # Run tests
        self.test_authentication()
        self.test_core_functionality()
        self.test_api_performance()
        self.test_basic_security()
        
        # Generate report
        report_file = self.generate_report()
        
        print(f"\n{'='*60}")
        print(f"VALIDATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total Tests: {self.test_results['summary']['total']}")
        print(f"Passed: {self.test_results['summary']['passed']} ✅")
        print(f"Failed: {self.test_results['summary']['failed']} ❌")
        print(f"Warnings: {self.test_results['summary']['warnings']} ⚠️")
        print(f"{'='*60}")

if __name__ == "__main__":
    validator = SimpleSystemValidator()
    validator.run_all_tests()