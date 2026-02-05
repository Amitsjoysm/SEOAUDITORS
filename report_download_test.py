#!/usr/bin/env python3
"""
MJ SEO Audit Report Download Test Suite
Tests PDF and DOCX report download functionality for specific audit ID
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
TEST_AUDIT_ID = "7a353d36-09df-4acb-9bcf-31cf25dc6934"

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
        
        if details and isinstance(details, dict):
            for key, value in details.items():
                print(f"   {key}: {value}")
        elif details:
            print(f"   Details: {details}")
    
    def print_summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n{Colors.BOLD}=== REPORT DOWNLOAD TEST SUMMARY ==={Colors.END}")
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.END}")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}FAILED TESTS:{Colors.END}")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")

class ReportDownloadTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json'
        })
        self.result = TestResult()
        self.superadmin_token = None
    
    def test_superadmin_login(self):
        """Test 1: Login as superadmin"""
        print(f"\n{Colors.BLUE}=== AUTHENTICATION TEST ==={Colors.END}")
        
        try:
            login_data = {
                "email": SUPERADMIN_EMAIL,
                "password": SUPERADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.superadmin_token = data["access_token"]
                    self.result.add_result("Superadmin Login", "PASS", 
                        f"Successfully logged in as {SUPERADMIN_EMAIL}")
                else:
                    self.result.add_result("Superadmin Login", "FAIL", "No access token in response")
            else:
                self.result.add_result("Superadmin Login", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("Superadmin Login", "FAIL", str(e))
    
    def test_audit_exists(self):
        """Test 2: Check if the specified audit exists and is completed"""
        print(f"\n{Colors.BLUE}=== AUDIT VERIFICATION TEST ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("Audit Existence Check", "FAIL", "No superladmin token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superladmin_token}"}
            response = self.session.get(f"{BASE_URL}/audits/{TEST_AUDIT_ID}", headers=headers)
            
            if response.status_code == 200:
                audit = response.json()
                status = audit.get("status", "unknown")
                website_url = audit.get("website_url", "N/A")
                
                details = {
                    "Audit ID": TEST_AUDIT_ID,
                    "Status": status,
                    "Website URL": website_url,
                    "Score": audit.get("score", "N/A")
                }
                
                if status == "completed":
                    self.result.add_result("Audit Existence Check", "PASS", 
                        "Audit found and completed", details)
                else:
                    self.result.add_result("Audit Existence Check", "WARNING", 
                        f"Audit found but status is '{status}' (not completed)", details)
            elif response.status_code == 404:
                self.result.add_result("Audit Existence Check", "FAIL", 
                    f"Audit with ID {TEST_AUDIT_ID} not found")
            else:
                self.result.add_result("Audit Existence Check", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("Audit Existence Check", "FAIL", str(e))
    
    def test_pdf_download(self):
        """Test 3: Test PDF report download"""
        print(f"\n{Colors.BLUE}=== PDF DOWNLOAD TEST ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("PDF Download", "FAIL", "No superladmin token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superladmin_token}"}
            response = self.session.get(f"{BASE_URL}/reports/{TEST_AUDIT_ID}/pdf", headers=headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                # Check content type
                expected_pdf_type = "application/pdf"
                content_type_ok = expected_pdf_type in content_type.lower()
                
                # Check content length
                content_size_ok = content_length > 0
                
                details = {
                    "Status Code": response.status_code,
                    "Content-Type": content_type,
                    "Content Size": f"{content_length} bytes",
                    "Content-Type OK": content_type_ok,
                    "Content Size OK": content_size_ok
                }
                
                if content_type_ok and content_size_ok:
                    self.result.add_result("PDF Download", "PASS", 
                        f"PDF downloaded successfully ({content_length} bytes)", details)
                else:
                    issues = []
                    if not content_type_ok:
                        issues.append(f"Wrong content-type: {content_type} (expected {expected_pdf_type})")
                    if not content_size_ok:
                        issues.append("Empty content")
                    
                    self.result.add_result("PDF Download", "FAIL", 
                        f"Issues: {', '.join(issues)}", details)
            else:
                self.result.add_result("PDF Download", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text[:200]}...")
        except Exception as e:
            self.result.add_result("PDF Download", "FAIL", str(e))
    
    def test_docx_download(self):
        """Test 4: Test DOCX report download"""
        print(f"\n{Colors.BLUE}=== DOCX DOWNLOAD TEST ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("DOCX Download", "FAIL", "No superladmin token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.superladmin_token}"}
            response = self.session.get(f"{BASE_URL}/reports/{TEST_AUDIT_ID}/docx", headers=headers)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                # Check content type
                expected_docx_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                content_type_ok = expected_docx_type in content_type.lower()
                
                # Check content length
                content_size_ok = content_length > 0
                
                details = {
                    "Status Code": response.status_code,
                    "Content-Type": content_type,
                    "Content Size": f"{content_length} bytes",
                    "Content-Type OK": content_type_ok,
                    "Content Size OK": content_size_ok
                }
                
                if content_type_ok and content_size_ok:
                    self.result.add_result("DOCX Download", "PASS", 
                        f"DOCX downloaded successfully ({content_length} bytes)", details)
                else:
                    issues = []
                    if not content_type_ok:
                        issues.append(f"Wrong content-type: {content_type} (expected {expected_docx_type})")
                    if not content_size_ok:
                        issues.append("Empty content")
                    
                    self.result.add_result("DOCX Download", "FAIL", 
                        f"Issues: {', '.join(issues)}", details)
            else:
                self.result.add_result("DOCX Download", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text[:200]}...")
        except Exception as e:
            self.result.add_result("DOCX Download", "FAIL", str(e))
    
    def test_download_authentication(self):
        """Test 5: Test download endpoints require authentication"""
        print(f"\n{Colors.BLUE}=== AUTHENTICATION REQUIREMENT TEST ==={Colors.END}")
        
        try:
            # Test without token
            response_pdf = self.session.get(f"{BASE_URL}/reports/{TEST_AUDIT_ID}/pdf")
            response_docx = self.session.get(f"{BASE_URL}/reports/{TEST_AUDIT_ID}/docx")
            
            # Both should return 401 (Unauthorized) without token
            pdf_auth_ok = response_pdf.status_code == 401
            docx_auth_ok = response_docx.status_code == 401
            
            details = {
                "PDF without auth status": response_pdf.status_code,
                "DOCX without auth status": response_docx.status_code,
                "PDF auth required": pdf_auth_ok,
                "DOCX auth required": docx_auth_ok
            }
            
            if pdf_auth_ok and docx_auth_ok:
                self.result.add_result("Download Authentication", "PASS", 
                    "Both endpoints properly require authentication", details)
            else:
                self.result.add_result("Download Authentication", "FAIL", 
                    "One or both endpoints don't require authentication", details)
                    
        except Exception as e:
            self.result.add_result("Download Authentication", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run all report download tests"""
        print(f"{Colors.BOLD}{Colors.PURPLE}🚀 Starting Audit Report Download Tests{Colors.END}")
        print(f"Testing against: {BASE_URL}")
        print(f"Target Audit ID: {TEST_AUDIT_ID}")
        print("=" * 80)
        
        # Run tests in order
        self.test_superadmin_login()
        self.test_audit_exists()
        self.test_pdf_download()
        self.test_docx_download()
        self.test_download_authentication()
        
        # Print final summary
        self.result.print_summary()
        
        return self.result.failed == 0

def main():
    """Main test runner"""
    tester = ReportDownloadTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL REPORT DOWNLOAD TESTS PASSED!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED! Check the results above.{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()