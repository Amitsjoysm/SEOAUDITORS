#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for MJ SEO Application
Tests all API endpoints with authentication, authorization, and functionality
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://seoauditor-2.preview.emergentagent.com/api"
SUPERADMIN_EMAIL = "superadmin@test.com"
SUPERADMIN_PASSWORD = "test123"
TEST_USER_EMAIL = "testuser@mjseo.com"
TEST_USER_PASSWORD = "testpass123"
TEST_WEBSITE_URL = "https://example.com"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []
    
    def add_result(self, test_name: str, status: str, message: str = "", details: Any = None):
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details
        }
        self.results.append(result)
        
        if status == "PASS":
            self.passed += 1
            print(f"{Colors.GREEN}✅ {test_name}: PASSED{Colors.END}")
        elif status == "FAIL":
            self.failed += 1
            print(f"{Colors.RED}❌ {test_name}: FAILED - {message}{Colors.END}")
        elif status == "WARNING":
            self.warnings += 1
            print(f"{Colors.YELLOW}⚠️  {test_name}: WARNING - {message}{Colors.END}")
        
        if details:
            print(f"   Details: {details}")
    
    def print_summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n{Colors.BOLD}=== TEST SUMMARY ==={Colors.END}")
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.END}")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}FAILED TESTS:{Colors.END}")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")

class MJSEOTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.result = TestResult()
        self.superadmin_token = None
        self.user_token = None
        self.test_user_id = None
        self.test_audit_id = None
        self.test_api_token_id = None
    
    def test_health_check(self):
        """Test basic health endpoints"""
        print(f"\n{Colors.BLUE}=== HEALTH CHECK TESTS ==={Colors.END}")
        
        try:
            # Test root endpoint
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "MJ SEO API":
                    self.result.add_result("Root Endpoint", "PASS")
                else:
                    self.result.add_result("Root Endpoint", "FAIL", "Unexpected response format")
            else:
                self.result.add_result("Root Endpoint", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Root Endpoint", "FAIL", str(e))
        
        try:
            # Test health endpoint
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.result.add_result("Health Check", "PASS")
                else:
                    self.result.add_result("Health Check", "FAIL", "Service not healthy")
            else:
                self.result.add_result("Health Check", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Health Check", "FAIL", str(e))
    
    def test_user_registration(self):
        """Test user registration"""
        print(f"\n{Colors.BLUE}=== USER REGISTRATION TESTS ==={Colors.END}")
        
        try:
            # Register new test user
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "Test User"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                if "access_token" in data and "refresh_token" in data:
                    self.user_token = data["access_token"]
                    self.result.add_result("User Registration", "PASS")
                else:
                    self.result.add_result("User Registration", "FAIL", "Missing tokens in response")
            elif response.status_code == 400:
                # User might already exist, try to login instead
                self.result.add_result("User Registration", "WARNING", "User already exists, will test login")
            else:
                self.result.add_result("User Registration", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("User Registration", "FAIL", str(e))
    
    def test_user_login(self):
        """Test user login"""
        print(f"\n{Colors.BLUE}=== USER LOGIN TESTS ==={Colors.END}")
        
        try:
            # Login with test user
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "refresh_token" in data:
                    self.user_token = data["access_token"]
                    self.result.add_result("User Login", "PASS")
                else:
                    self.result.add_result("User Login", "FAIL", "Missing tokens in response")
            else:
                self.result.add_result("User Login", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("User Login", "FAIL", str(e))
    
    def test_superadmin_login(self):
        """Test superadmin login"""
        print(f"\n{Colors.BLUE}=== SUPERADMIN LOGIN TESTS ==={Colors.END}")
        
        try:
            login_data = {
                "email": SUPERADMIN_EMAIL,
                "password": SUPERADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "refresh_token" in data:
                    self.superadmin_token = data["access_token"]
                    self.result.add_result("Superadmin Login", "PASS")
                else:
                    self.result.add_result("Superadmin Login", "FAIL", "Missing tokens in response")
            else:
                self.result.add_result("Superadmin Login", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("Superadmin Login", "FAIL", str(e))
    
    def test_jwt_validation(self):
        """Test JWT token validation"""
        print(f"\n{Colors.BLUE}=== JWT VALIDATION TESTS ==={Colors.END}")
        
        if not self.user_token:
            self.result.add_result("JWT Validation", "FAIL", "No user token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "email" in data and data["email"] == TEST_USER_EMAIL:
                    self.result.add_result("JWT Validation", "PASS")
                else:
                    self.result.add_result("JWT Validation", "FAIL", "Invalid user data returned")
            else:
                self.result.add_result("JWT Validation", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("JWT Validation", "FAIL", str(e))
    
    def test_theme_system(self):
        """Test theme management system"""
        print(f"\n{Colors.BLUE}=== THEME SYSTEM TESTS ==={Colors.END}")
        
        try:
            # Test public active theme endpoint
            response = self.session.get(f"{BASE_URL}/themes/active")
            if response.status_code == 200:
                data = response.json()
                if "name" in data and "primary_color" in data:
                    self.result.add_result("Get Active Theme (Public)", "PASS")
                else:
                    self.result.add_result("Get Active Theme (Public)", "FAIL", "Invalid theme data")
            else:
                self.result.add_result("Get Active Theme (Public)", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Get Active Theme (Public)", "FAIL", str(e))
        
        if not self.superadmin_token:
            self.result.add_result("Theme Management (Admin)", "FAIL", "No superadmin token available")
            return
        
        try:
            # Test admin theme list
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{BASE_URL}/themes/", headers=headers)
            
            if response.status_code == 200:
                themes = response.json()
                if isinstance(themes, list):
                    self.result.add_result("List Themes (Admin)", "PASS", f"Found {len(themes)} themes")
                    
                    # Test theme activation if themes exist
                    if themes:
                        theme_id = themes[0]["id"]
                        response = self.session.post(f"{BASE_URL}/themes/{theme_id}/activate", headers=headers)
                        if response.status_code == 200:
                            self.result.add_result("Activate Theme (Admin)", "PASS")
                        else:
                            self.result.add_result("Activate Theme (Admin)", "FAIL", f"Status: {response.status_code}")
                else:
                    self.result.add_result("List Themes (Admin)", "FAIL", "Invalid response format")
            else:
                self.result.add_result("List Themes (Admin)", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("List Themes (Admin)", "FAIL", str(e))
        
        # Test unauthorized access
        try:
            if self.user_token:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/themes/", headers=headers)
                if response.status_code == 403:
                    self.result.add_result("Theme Access Control", "PASS", "Regular user correctly denied access")
                else:
                    self.result.add_result("Theme Access Control", "FAIL", f"Regular user should be denied, got: {response.status_code}")
        except Exception as e:
            self.result.add_result("Theme Access Control", "FAIL", str(e))
    
    def test_plans_system(self):
        """Test plans and subscriptions"""
        print(f"\n{Colors.BLUE}=== PLANS SYSTEM TESTS ==={Colors.END}")
        
        try:
            # Test public plans endpoint
            response = self.session.get(f"{BASE_URL}/plans/")
            if response.status_code == 200:
                plans = response.json()
                if isinstance(plans, list) and len(plans) >= 4:
                    plan_names = [plan.get("name", "").lower() for plan in plans]
                    expected_plans = ["free", "basic", "pro", "enterprise"]
                    
                    if all(expected in plan_names for expected in expected_plans):
                        self.result.add_result("Get Plans", "PASS", f"Found all 4 expected plans: {plan_names}")
                    else:
                        self.result.add_result("Get Plans", "WARNING", f"Expected plans not found. Got: {plan_names}")
                else:
                    self.result.add_result("Get Plans", "FAIL", f"Expected at least 4 plans, got {len(plans) if isinstance(plans, list) else 'invalid format'}")
            else:
                self.result.add_result("Get Plans", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Get Plans", "FAIL", str(e))
    
    def test_audit_system(self):
        """Test audit creation and management"""
        print(f"\n{Colors.BLUE}=== AUDIT SYSTEM TESTS ==={Colors.END}")
        
        if not self.user_token:
            self.result.add_result("Audit System", "FAIL", "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # Test audit creation
            audit_data = {
                "website_url": TEST_WEBSITE_URL
            }
            
            response = self.session.post(f"{BASE_URL}/audits/", json=audit_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                if "id" in data and "website_url" in data:
                    self.test_audit_id = data["id"]
                    self.result.add_result("Create Audit", "PASS", f"Audit ID: {self.test_audit_id}")
                else:
                    self.result.add_result("Create Audit", "FAIL", "Invalid audit response format")
            else:
                self.result.add_result("Create Audit", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("Create Audit", "FAIL", str(e))
        
        try:
            # Test list user audits
            response = self.session.get(f"{BASE_URL}/audits/", headers=headers)
            
            if response.status_code == 200:
                audits = response.json()
                if isinstance(audits, list):
                    self.result.add_result("List User Audits", "PASS", f"Found {len(audits)} audits")
                else:
                    self.result.add_result("List User Audits", "FAIL", "Invalid response format")
            else:
                self.result.add_result("List User Audits", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("List User Audits", "FAIL", str(e))
        
        if self.test_audit_id:
            try:
                # Test get specific audit
                response = self.session.get(f"{BASE_URL}/audits/{self.test_audit_id}", headers=headers)
                
                if response.status_code == 200:
                    audit = response.json()
                    if "id" in audit and audit["id"] == self.test_audit_id:
                        self.result.add_result("Get Specific Audit", "PASS")
                    else:
                        self.result.add_result("Get Specific Audit", "FAIL", "Audit ID mismatch")
                else:
                    self.result.add_result("Get Specific Audit", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("Get Specific Audit", "FAIL", str(e))
    
    def test_api_tokens(self):
        """Test API token management"""
        print(f"\n{Colors.BLUE}=== API TOKEN TESTS ==={Colors.END}")
        
        if not self.user_token:
            self.result.add_result("API Token System", "FAIL", "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # Test create API token
            token_data = {
                "name": "Test MCP Token"
            }
            
            response = self.session.post(f"{BASE_URL}/api-tokens/", json=token_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                if "id" in data and "token" in data and data["token"].startswith("mjseo_"):
                    self.test_api_token_id = data["id"]
                    self.result.add_result("Create API Token", "PASS", f"Token format correct: {data['token'][:15]}...")
                else:
                    self.result.add_result("Create API Token", "FAIL", "Invalid token response format")
            else:
                self.result.add_result("Create API Token", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Create API Token", "FAIL", str(e))
        
        try:
            # Test list API tokens
            response = self.session.get(f"{BASE_URL}/api-tokens/", headers=headers)
            
            if response.status_code == 200:
                tokens = response.json()
                if isinstance(tokens, list):
                    self.result.add_result("List API Tokens", "PASS", f"Found {len(tokens)} tokens")
                else:
                    self.result.add_result("List API Tokens", "FAIL", "Invalid response format")
            else:
                self.result.add_result("List API Tokens", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("List API Tokens", "FAIL", str(e))
        
        if self.test_api_token_id:
            try:
                # Test delete API token
                response = self.session.delete(f"{BASE_URL}/api-tokens/{self.test_api_token_id}", headers=headers)
                
                if response.status_code == 200:
                    self.result.add_result("Delete API Token", "PASS")
                else:
                    self.result.add_result("Delete API Token", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("Delete API Token", "FAIL", str(e))
    
    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        print(f"\n{Colors.BLUE}=== ADMIN ENDPOINTS TESTS ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("Admin Endpoints", "FAIL", "No superadmin token available")
            return
        
        admin_headers = {"Authorization": f"Bearer {self.superadmin_token}"}
        
        try:
            # Test admin dashboard stats
            response = self.session.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_users", "active_users", "total_audits", "audits_this_month"]
                if all(field in stats for field in required_fields):
                    self.result.add_result("Admin Dashboard Stats", "PASS", f"Stats: {stats}")
                else:
                    self.result.add_result("Admin Dashboard Stats", "FAIL", "Missing required stats fields")
            else:
                self.result.add_result("Admin Dashboard Stats", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Admin Dashboard Stats", "FAIL", str(e))
        
        try:
            # Test admin users list
            response = self.session.get(f"{BASE_URL}/admin/users", headers=admin_headers)
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.result.add_result("Admin Users List", "PASS", f"Found {len(users)} users")
                else:
                    self.result.add_result("Admin Users List", "FAIL", "Invalid response format")
            else:
                self.result.add_result("Admin Users List", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Admin Users List", "FAIL", str(e))
        
        try:
            # Test admin audits list
            response = self.session.get(f"{BASE_URL}/admin/audits", headers=admin_headers)
            
            if response.status_code == 200:
                audits = response.json()
                if isinstance(audits, list):
                    self.result.add_result("Admin Audits List", "PASS", f"Found {len(audits)} audits")
                else:
                    self.result.add_result("Admin Audits List", "FAIL", "Invalid response format")
            else:
                self.result.add_result("Admin Audits List", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Admin Audits List", "FAIL", str(e))
        
        # Test unauthorized access to admin endpoints
        if self.user_token:
            try:
                user_headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/admin/dashboard", headers=user_headers)
                
                if response.status_code == 403:
                    self.result.add_result("Admin Access Control", "PASS", "Regular user correctly denied admin access")
                else:
                    self.result.add_result("Admin Access Control", "FAIL", f"Regular user should be denied admin access, got: {response.status_code}")
            except Exception as e:
                self.result.add_result("Admin Access Control", "FAIL", str(e))
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print(f"\n{Colors.BLUE}=== CORS CONFIGURATION TESTS ==={Colors.END}")
        
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://seoauditor-2.preview.emergentagent.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
            
            response = self.session.options(f"{BASE_URL}/auth/login", headers=headers)
            
            # Check if CORS headers are present
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            present_headers = [h for h in cors_headers if h in response.headers]
            
            if len(present_headers) >= 2:  # At least some CORS headers present
                self.result.add_result("CORS Configuration", "PASS", f"CORS headers present: {present_headers}")
            else:
                self.result.add_result("CORS Configuration", "WARNING", "Limited CORS headers detected")
                
        except Exception as e:
            self.result.add_result("CORS Configuration", "WARNING", f"Could not test CORS: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"{Colors.BOLD}{Colors.PURPLE}🚀 Starting MJ SEO Backend Comprehensive Tests{Colors.END}")
        print(f"Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Run tests in logical order
        self.test_health_check()
        self.test_user_registration()
        self.test_user_login()
        self.test_superadmin_login()
        self.test_jwt_validation()
        self.test_theme_system()
        self.test_plans_system()
        self.test_audit_system()
        self.test_api_tokens()
        self.test_admin_endpoints()
        self.test_cors_configuration()
        
        # Print final summary
        self.result.print_summary()
        
        return self.result.failed == 0

def main():
    """Main test runner"""
    tester = MJSEOTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Backend is working correctly.{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED! Check the results above.{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()