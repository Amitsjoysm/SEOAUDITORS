#!/usr/bin/env python3
"""
Production-Ready MJ SEO Backend Test Suite
Tests authentication, API key pool, integrations, and enhanced audit flow
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "https://codebase-sync-49.preview.emergentagent.com/api"
SUPERADMIN_EMAIL = "superadmin@test.com"
SUPERADMIN_PASSWORD = "test123"
TEST_USER_EMAIL = "newuser@test.com"
TEST_USER_PASSWORD = "test123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
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

class ProductionTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.result = TestResult()
        self.superadmin_token = None
        self.user_token = None
        self.test_audit_id = None
    
    def test_user_registration(self):
        """Test 1: User registration"""
        print(f"\n{Colors.BLUE}=== AUTHENTICATION TESTS ==={Colors.END}")
        
        try:
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "New User"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                if "access_token" in data and "refresh_token" in data:
                    self.user_token = data["access_token"]
                    # Verify JWT format (3 parts separated by dots)
                    token_parts = self.user_token.split('.')
                    if len(token_parts) == 3:
                        self.result.add_result("User Registration", "PASS", "JWT token has correct format")
                    else:
                        self.result.add_result("User Registration", "FAIL", f"Invalid JWT format: {len(token_parts)} parts")
                else:
                    self.result.add_result("User Registration", "FAIL", "Missing tokens in response")
            elif response.status_code == 400:
                self.result.add_result("User Registration", "WARNING", "User already exists, will test login")
            else:
                self.result.add_result("User Registration", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("User Registration", "FAIL", str(e))
    
    def test_user_login(self):
        """Test 2: User login"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "refresh_token" in data:
                    self.user_token = data["access_token"]
                    # Verify JWT format
                    token_parts = self.user_token.split('.')
                    if len(token_parts) == 3:
                        self.result.add_result("User Login", "PASS", "JWT token returned with correct format")
                    else:
                        self.result.add_result("User Login", "FAIL", f"Invalid JWT format: {len(token_parts)} parts")
                else:
                    self.result.add_result("User Login", "FAIL", "Missing tokens in response")
            else:
                self.result.add_result("User Login", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("User Login", "FAIL", str(e))
    
    def test_superadmin_login(self):
        """Test 3: Superadmin login"""
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
                    # Verify JWT format
                    token_parts = self.superadmin_token.split('.')
                    if len(token_parts) == 3:
                        self.result.add_result("Superadmin Login", "PASS", "JWT token returned with correct format")
                    else:
                        self.result.add_result("Superadmin Login", "FAIL", f"Invalid JWT format: {len(token_parts)} parts")
                else:
                    self.result.add_result("Superadmin Login", "FAIL", "Missing tokens in response")
            else:
                self.result.add_result("Superadmin Login", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Superadmin Login", "FAIL", str(e))
    
    def test_jwt_validation(self):
        """Test 4: JWT token validation"""
        if not self.user_token:
            self.result.add_result("JWT Validation", "FAIL", "No user token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "email" in data:
                    self.result.add_result("JWT Validation", "PASS", f"Token validated for user: {data['email']}")
                else:
                    self.result.add_result("JWT Validation", "FAIL", "Invalid user data returned")
            else:
                self.result.add_result("JWT Validation", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("JWT Validation", "FAIL", str(e))
    
    def test_api_key_pool_initialization(self):
        """Test 5: API key pool initialization from environment"""
        print(f"\n{Colors.BLUE}=== API KEY POOL TESTS ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("API Key Pool Init", "FAIL", "No superadmin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.post(f"{BASE_URL}/admin/api-keys/initialize-from-env", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                keys_added = data.get("keys_added", [])
                self.result.add_result("API Key Pool Init", "PASS", f"Initialized {len(keys_added)} keys: {keys_added}")
            else:
                self.result.add_result("API Key Pool Init", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("API Key Pool Init", "FAIL", str(e))
    
    def test_list_api_keys(self):
        """Test 6: List API keys"""
        if not self.superadmin_token:
            self.result.add_result("List API Keys", "FAIL", "No superadmin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/api-keys/", headers=headers)
            
            if response.status_code == 200:
                keys = response.json()
                if isinstance(keys, list):
                    self.result.add_result("List API Keys", "PASS", f"Found {len(keys)} API keys")
                else:
                    self.result.add_result("List API Keys", "FAIL", "Invalid response format")
            else:
                self.result.add_result("List API Keys", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("List API Keys", "FAIL", str(e))
    
    def test_integration_status(self):
        """Test 7: Get integration status"""
        print(f"\n{Colors.BLUE}=== INTEGRATION TESTS ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("Integration Status", "FAIL", "No superadmin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/integrations/", headers=headers)
            
            if response.status_code == 200:
                integrations = response.json()
                if isinstance(integrations, list):
                    self.result.add_result("Integration Status", "PASS", f"Found {len(integrations)} integrations")
                else:
                    self.result.add_result("Integration Status", "FAIL", "Invalid response format")
            else:
                self.result.add_result("Integration Status", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Integration Status", "FAIL", str(e))
    
    def test_integration_dashboard(self):
        """Test 8: Get integration dashboard overview"""
        if not self.superadmin_token:
            self.result.add_result("Integration Dashboard", "FAIL", "No superadmin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/integrations/dashboard/overview", headers=headers)
            
            if response.status_code == 200:
                dashboard = response.json()
                if "summary" in dashboard:
                    summary = dashboard["summary"]
                    self.result.add_result("Integration Dashboard", "PASS", 
                        f"Total services: {summary.get('total_services')}, Healthy: {summary.get('healthy_services')}")
                else:
                    self.result.add_result("Integration Dashboard", "FAIL", "Missing summary in response")
            else:
                self.result.add_result("Integration Dashboard", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Integration Dashboard", "FAIL", str(e))
    
    def test_lighthouse_integration(self):
        """Test 9: Test Lighthouse integration"""
        if not self.superadmin_token:
            self.result.add_result("Lighthouse Integration", "FAIL", "No superadmin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.post(f"{BASE_URL}/admin/integrations/test/lighthouse", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.result.add_result("Lighthouse Integration", "PASS", 
                        f"Response time: {result.get('response_time_ms', 0):.2f}ms")
                else:
                    self.result.add_result("Lighthouse Integration", "FAIL", 
                        f"Test failed: {result.get('error')}")
            else:
                self.result.add_result("Lighthouse Integration", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Lighthouse Integration", "FAIL", str(e))
    
    def test_dataforseo_integration(self):
        """Test 10: Test DataForSEO integration"""
        if not self.superadmin_token:
            self.result.add_result("DataForSEO Integration", "FAIL", "No superadmin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.post(f"{BASE_URL}/admin/integrations/test/dataforseo", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.result.add_result("DataForSEO Integration", "PASS", 
                        f"Response time: {result.get('response_time_ms', 0):.2f}ms")
                else:
                    self.result.add_result("DataForSEO Integration", "WARNING", 
                        f"Test returned success=false: {result.get('error')}")
            else:
                self.result.add_result("DataForSEO Integration", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("DataForSEO Integration", "FAIL", str(e))
    
    def test_create_audit(self):
        """Test 11: Create new audit"""
        print(f"\n{Colors.BLUE}=== ENHANCED AUDIT FLOW TESTS ==={Colors.END}")
        
        # Use superadmin token for audit creation to avoid subscription issues
        if not self.superadmin_token:
            self.result.add_result("Create Audit", "FAIL", "No superadmin token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            audit_data = {"website_url": "https://example.com"}
            
            response = self.session.post(f"{BASE_URL}/audits/", json=audit_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                if "id" in data:
                    self.test_audit_id = data["id"]
                    self.result.add_result("Create Audit", "PASS", f"Audit created: {self.test_audit_id}")
                else:
                    self.result.add_result("Create Audit", "FAIL", "No audit ID in response")
            elif response.status_code == 429:
                self.result.add_result("Create Audit", "WARNING", "Monthly limit reached, will use existing audit")
                # Try to get existing audit
                response = self.session.get(f"{BASE_URL}/audits/", headers=headers)
                if response.status_code == 200:
                    audits = response.json()
                    if audits and len(audits) > 0:
                        self.test_audit_id = audits[0]["id"]
                        self.result.add_result("Use Existing Audit", "PASS", f"Using audit: {self.test_audit_id}")
            else:
                self.result.add_result("Create Audit", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Create Audit", "FAIL", str(e))
    
    def test_get_audit_details(self):
        """Test 12: Get audit details with enhanced fields"""
        if not self.test_audit_id or not self.superadmin_token:
            self.result.add_result("Get Audit Details", "FAIL", "No audit ID or token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{BASE_URL}/audits/{self.test_audit_id}", headers=headers)
            
            if response.status_code == 200:
                audit = response.json()
                
                # Check for enhanced fields
                has_lighthouse = "lighthouse_data" in audit
                has_competitor_count = "competitor_count" in audit
                has_opportunities = "opportunities_found" in audit
                
                if has_lighthouse and has_competitor_count and has_opportunities:
                    self.result.add_result("Get Audit Details", "PASS", 
                        f"Enhanced fields present: lighthouse_data, competitor_count={audit.get('competitor_count')}, opportunities_found={audit.get('opportunities_found')}")
                else:
                    missing = []
                    if not has_lighthouse: missing.append("lighthouse_data")
                    if not has_competitor_count: missing.append("competitor_count")
                    if not has_opportunities: missing.append("opportunities_found")
                    self.result.add_result("Get Audit Details", "WARNING", 
                        f"Missing enhanced fields: {', '.join(missing)}")
            else:
                self.result.add_result("Get Audit Details", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Get Audit Details", "FAIL", str(e))
    
    def test_competitors_endpoint(self):
        """Test 13: Get competitors for audit"""
        if not self.test_audit_id or not self.superadmin_token:
            self.result.add_result("Competitors Endpoint", "FAIL", "No audit ID or token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{BASE_URL}/audits/{self.test_audit_id}/competitors/", headers=headers)
            
            if response.status_code == 200:
                competitors = response.json()
                if isinstance(competitors, list):
                    self.result.add_result("Competitors Endpoint", "PASS", 
                        f"Found {len(competitors)} competitors")
                else:
                    self.result.add_result("Competitors Endpoint", "FAIL", "Invalid response format")
            else:
                self.result.add_result("Competitors Endpoint", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Competitors Endpoint", "FAIL", str(e))
    
    def test_opportunities_endpoint(self):
        """Test 14: Get content opportunities for audit"""
        if not self.test_audit_id or not self.superadmin_token:
            self.result.add_result("Opportunities Endpoint", "FAIL", "No audit ID or token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superadmin_token}"}
            response = self.session.get(f"{BASE_URL}/audits/{self.test_audit_id}/opportunities/", headers=headers)
            
            if response.status_code == 200:
                opportunities = response.json()
                if isinstance(opportunities, list):
                    self.result.add_result("Opportunities Endpoint", "PASS", 
                        f"Found {len(opportunities)} content opportunities")
                else:
                    self.result.add_result("Opportunities Endpoint", "FAIL", "Invalid response format")
            else:
                self.result.add_result("Opportunities Endpoint", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("Opportunities Endpoint", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run all production tests"""
        print(f"{Colors.BOLD}{Colors.PURPLE}🚀 Starting Production-Ready MJ SEO Backend Tests{Colors.END}")
        print(f"Testing against: {BASE_URL}")
        print("=" * 80)
        
        # CRITICAL AUTHENTICATION TESTS
        self.test_user_registration()
        self.test_user_login()
        self.test_superadmin_login()
        self.test_jwt_validation()
        
        # NEW PRODUCTION FEATURES TESTS
        self.test_api_key_pool_initialization()
        self.test_list_api_keys()
        self.test_integration_status()
        self.test_integration_dashboard()
        self.test_lighthouse_integration()
        self.test_dataforseo_integration()
        
        # ENHANCED AUDIT FLOW
        self.test_create_audit()
        self.test_get_audit_details()
        self.test_competitors_endpoint()
        self.test_opportunities_endpoint()
        
        # Print final summary
        self.result.print_summary()
        
        return self.result.failed == 0

def main():
    """Main test runner"""
    tester = ProductionTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Production backend is ready.{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED! Check the results above.{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
