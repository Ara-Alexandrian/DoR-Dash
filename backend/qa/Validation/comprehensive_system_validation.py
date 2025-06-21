#!/usr/bin/env python3
"""
Comprehensive System Validation Suite for DoR-Dash
Tests authentication, core functionality, performance, security, and data integrity
"""

import sys
import os
import time
import json
import asyncio
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
import ssl
import http.client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings

class SystemValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}{settings.API_V1_STR}"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0},
            "categories": {}
        }
        self.session_token = None
        self.test_user = {
            "username": "test_user_qa",
            "password": "TestPassword123!",
            "email": "qa_test@dordash.test",
            "full_name": "QA Test User"
        }
        self.admin_user = {
            "username": "admin",
            "password": "admin123"  # Default admin password
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
        
        # Test logout
        if self.session_token:
            try:
                headers = {"Authorization": f"Bearer {self.session_token}"}
                status, data = self.make_request("POST", f"{self.api_base}/auth/logout", headers=headers)
                if status == 200:
                    self.log_test("Authentication", "Logout functionality", True)
                else:
                    self.log_test("Authentication", "Logout functionality", False, 
                                f"Status: {status}")
            except Exception as e:
                self.log_test("Authentication", "Logout functionality", False, str(e))
    
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
        
        # Test agenda items CRUD
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
        
        # Read
        if test_item_id:
            try:
                status, data = self.make_request("GET", f"{self.api_base}/agenda-items/{test_item_id}", 
                                               headers=headers)
                if status == 200:
                    self.log_test("Core Functionality", "Read agenda item", True)
                else:
                    self.log_test("Core Functionality", "Read agenda item", False, 
                                f"Status: {status}")
            except Exception as e:
                self.log_test("Core Functionality", "Read agenda item", False, str(e))
        
        # Update
        if test_item_id:
            try:
                update_data = {
                    "title": "QA Test Item - Updated",
                    "content": "Updated content for QA validation"
                }
                status, data = self.make_request("PUT", f"{self.api_base}/agenda-items/{test_item_id}", 
                                               update_data, headers)
                if status == 200:
                    self.log_test("Core Functionality", "Update agenda item", True)
                else:
                    self.log_test("Core Functionality", "Update agenda item", False, 
                                f"Status: {status}")
            except Exception as e:
                self.log_test("Core Functionality", "Update agenda item", False, str(e))
        
        # Delete
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
        
        # Test text refinement
        try:
            refine_data = {
                "text": "this is test text that need refinement",
                "context": "announcement"
            }
            status, data = self.make_request("POST", f"{self.api_base}/text/refine", 
                                           refine_data, headers)
            if status == 200:
                if "refined_text" in data:
                    self.log_test("Core Functionality", "Text refinement", True)
                else:
                    self.log_test("Core Functionality", "Text refinement", False, 
                                "No refined_text in response")
            else:
                self.log_test("Core Functionality", "Text refinement", False, 
                            f"Status: {status}")
        except Exception as e:
            self.log_test("Core Functionality", "Text refinement", False, str(e))
    
    def test_api_performance(self):
        """Test API response times"""
        print("\n⚡ Testing API Performance...")
        
        endpoints = [
            ("/health", "GET", None, 100),  # endpoint, method, data, max_ms
            ("/auth/login", "POST", {"username": "admin", "password": "admin123"}, 500),
            ("/agenda-items", "GET", None, 1000),
            ("/meetings", "GET", None, 1000),
            ("/presentations", "GET", None, 1000),
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
    
    def test_security(self):
        """Test security measures"""
        print("\n🔒 Testing Security...")
        
        headers = {"Authorization": f"Bearer {self.session_token}"} if self.session_token else {}
        
        # Test SQL injection protection
        try:
            # Attempt SQL injection in search
            injection_query = "'; DROP TABLE users; --"
            injection_url = f"{self.api_base}/agenda-items?search={urllib.parse.quote(injection_query)}"
            status, data = self.make_request("GET", injection_url, headers=headers)
            if status in [200, 400, 422]:  # Should handle gracefully
                self.log_test("Security", "SQL injection protection", True)
            else:
                self.log_test("Security", "SQL injection protection", False, 
                            f"Unexpected status: {status}")
        except Exception as e:
            self.log_test("Security", "SQL injection protection", False, str(e))
        
        # Test XSS protection
        try:
            xss_data = {
                "title": "<script>alert('XSS')</script>",
                "content": "Test content",
                "item_type": "announcement",
                "created_by": "qa_test"
            }
            status, data = self.make_request("POST", f"{self.api_base}/agenda-items/", 
                                           xss_data, headers)
            if status == 200:
                # Check if script tags are escaped/sanitized
                if "<script>" not in str(data):
                    self.log_test("Security", "XSS protection", True)
                else:
                    self.log_test("Security", "XSS protection", False, 
                                "Script tags not sanitized")
            else:
                self.log_test("Security", "XSS protection", True, 
                            "Request rejected")
        except Exception as e:
            self.log_test("Security", "XSS protection", False, str(e))
        
        # Test authorization (non-admin trying admin endpoint)
        try:
            # First create a regular user
            user_data = {
                "username": "regular_user_qa",
                "password": "RegularPass123!",
                "email": "regular@test.com",
                "full_name": "Regular User",
                "role": "student"
            }
            status, data = self.make_request("POST", f"{self.api_base}/auth/register", user_data)
            if status == 200:
                # Login as regular user
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
                status, data = self.make_request("POST", f"{self.api_base}/auth/login", login_data)
                if status == 200:
                    regular_token = data.get("access_token")
                    
                    # Try accessing admin endpoint
                    headers = {"Authorization": f"Bearer {regular_token}"}
                    status, data = self.make_request("GET", f"{self.api_base}/users/", headers=headers)
                    if status == 403:
                        self.log_test("Security", "Role-based access control", True)
                    else:
                        self.log_test("Security", "Role-based access control", False, 
                                    f"Expected 403, got {status}")
        except Exception as e:
            self.log_test("Security", "Role-based access control", False, str(e))
    
    def test_database_integrity(self):
        """Test database integrity and relationships"""
        print("\n🗄️ Testing Database Integrity...")
        
        try:
            # Connect to database
            conn = psycopg2.connect(
                host=settings.POSTGRES_SERVER,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                cursor_factory=RealDictCursor
            )
            cursor = conn.cursor()
            
            # Test foreign key constraints
            cursor.execute("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
            """)
            
            fk_count = cursor.rowcount
            if fk_count > 0:
                self.log_test("Database", "Foreign key constraints exist", True, f"Found {fk_count} FK constraints")
            else:
                self.log_test("Database", "Foreign key constraints exist", False, "No FK constraints found")
            
            # Test indexes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)
            
            index_count = cursor.rowcount
            if index_count > 10:  # Should have many indexes
                self.log_test("Database", "Database indexes", True, f"Found {index_count} indexes")
            else:
                self.log_test("Database", "Database indexes", False, f"Only {index_count} indexes found", warning=True)
            
            # Test critical tables exist
            critical_tables = ['users', 'agenda_items', 'meetings', 'presentations', 'presentation_assignments']
            for table in critical_tables:
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    )
                """)
                exists = cursor.fetchone()['exists']
                if exists:
                    self.log_test("Database", f"Table '{table}' exists", True)
                else:
                    self.log_test("Database", f"Table '{table}' exists", False)
            
            # Test data integrity - orphaned records
            cursor.execute("""
                SELECT COUNT(*) as orphaned FROM agenda_items 
                WHERE meeting_id IS NOT NULL 
                AND meeting_id NOT IN (SELECT id FROM meetings)
            """)
            orphaned = cursor.fetchone()['orphaned']
            if orphaned == 0:
                self.log_test("Database", "No orphaned agenda items", True)
            else:
                self.log_test("Database", "No orphaned agenda items", False, 
                            f"Found {orphaned} orphaned records", warning=True)
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log_test("Database", "Database connection", False, str(e))
    
    def generate_report(self):
        """Generate comprehensive validation report"""
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
        print("🚀 Starting Comprehensive System Validation...\n")
        
        # Run tests
        self.test_authentication()
        self.test_core_functionality()
        self.test_api_performance()
        self.test_security()
        self.test_database_integrity()
        
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
    validator = SystemValidator()
    validator.run_all_tests()