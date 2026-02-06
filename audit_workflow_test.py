#!/usr/bin/env python3
"""
Complete End-to-End Audit Workflow Test with Report Generation
Tests the exact workflow specified in the review request
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "https://api-sync-1.preview.emergentagent.com/api"
SUPERADMIN_EMAIL = "superadmin@test.com"
SUPERADMIN_PASSWORD = "test123"
TEST_WEBSITE = "https://example.com"

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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def print_summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}=== AUDIT WORKFLOW TEST SUMMARY ==={Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}✅ Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {self.warnings}{Colors.END}")
        
        if self.failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}FAILED TESTS:{Colors.END}")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")

class AuditWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.result = TestResult()
        self.jwt_token = None
        self.audit_id = None
    
    def test_superadmin_login(self):
        """Step 1: Login as superadmin"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 1: SUPERADMIN LOGIN ==={Colors.END}")
        
        try:
            login_data = {
                "email": SUPERADMIN_EMAIL,
                "password": SUPERADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.jwt_token = data["access_token"]
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.jwt_token}'
                    })
                    self.result.add_result(
                        "Superadmin Login",
                        "PASS",
                        f"Successfully logged in as {SUPERADMIN_EMAIL}",
                        {"token_length": len(self.jwt_token)}
                    )
                else:
                    self.result.add_result(
                        "Superadmin Login",
                        "FAIL",
                        "No access_token in response"
                    )
            else:
                self.result.add_result(
                    "Superadmin Login",
                    "FAIL",
                    f"Status code: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            self.result.add_result(
                "Superadmin Login",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_create_audit(self):
        """Step 3: Create audit for https://example.com"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 3: CREATE AUDIT ==={Colors.END}")
        
        if not self.jwt_token:
            self.result.add_result(
                "Create Audit",
                "FAIL",
                "No JWT token available (login failed)"
            )
            return
        
        try:
            audit_data = {
                "website_url": TEST_WEBSITE
            }
            
            response = self.session.post(f"{BASE_URL}/audits/", json=audit_data)
            
            if response.status_code == 201:
                data = response.json()
                if "id" in data:
                    self.audit_id = data["id"]
                    self.result.add_result(
                        "Create Audit",
                        "PASS",
                        f"Audit created successfully for {TEST_WEBSITE}",
                        {
                            "audit_id": self.audit_id,
                            "status": data.get("status"),
                            "website_url": data.get("website_url")
                        }
                    )
                else:
                    self.result.add_result(
                        "Create Audit",
                        "FAIL",
                        "No audit ID in response"
                    )
            else:
                self.result.add_result(
                    "Create Audit",
                    "FAIL",
                    f"Status code: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            self.result.add_result(
                "Create Audit",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_wait_and_check_status_first(self):
        """Step 5-6: Wait 25 seconds and check audit status"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 5-6: WAIT 25s AND CHECK STATUS ==={Colors.END}")
        
        if not self.audit_id:
            self.result.add_result(
                "First Status Check",
                "FAIL",
                "No audit ID available (audit creation failed)"
            )
            return
        
        print(f"{Colors.CYAN}⏳ Waiting 25 seconds for audit processing to start...{Colors.END}")
        time.sleep(25)
        
        try:
            response = self.session.get(f"{BASE_URL}/audits/{self.audit_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status in ["analyzing", "completed"]:
                    self.result.add_result(
                        "First Status Check (after 25s)",
                        "PASS",
                        f"Audit status is '{status}' as expected",
                        {
                            "status": status,
                            "pages_crawled": data.get("pages_crawled"),
                            "total_checks_run": data.get("total_checks_run"),
                            "overall_score": data.get("overall_score")
                        }
                    )
                else:
                    self.result.add_result(
                        "First Status Check (after 25s)",
                        "WARNING",
                        f"Status is '{status}', expected 'analyzing' or 'completed'",
                        {"current_status": status}
                    )
            else:
                self.result.add_result(
                    "First Status Check (after 25s)",
                    "FAIL",
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.result.add_result(
                "First Status Check (after 25s)",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_wait_and_verify_completion(self):
        """Step 7-8: Wait another 25 seconds and verify final status"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 7-8: WAIT 25s MORE AND VERIFY COMPLETION ==={Colors.END}")
        
        if not self.audit_id:
            self.result.add_result(
                "Final Status Verification",
                "FAIL",
                "No audit ID available"
            )
            return
        
        print(f"{Colors.CYAN}⏳ Waiting another 25 seconds for audit completion...{Colors.END}")
        time.sleep(25)
        
        try:
            response = self.session.get(f"{BASE_URL}/audits/{self.audit_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                overall_score = data.get("overall_score")
                pages_crawled = data.get("pages_crawled")
                total_checks_run = data.get("total_checks_run")
                
                # Check all expected conditions
                checks = []
                
                if status == "completed":
                    checks.append(("Status is 'completed'", True))
                else:
                    checks.append((f"Status is '{status}' (expected 'completed')", False))
                
                if overall_score is not None:
                    checks.append((f"Overall score is {overall_score}", True))
                else:
                    checks.append(("Overall score is null", False))
                
                if pages_crawled and pages_crawled > 0:
                    checks.append((f"Pages crawled: {pages_crawled}", True))
                else:
                    checks.append((f"Pages crawled: {pages_crawled} (expected > 0)", False))
                
                if total_checks_run and total_checks_run > 100:
                    checks.append((f"Total checks run: {total_checks_run}", True))
                else:
                    checks.append((f"Total checks run: {total_checks_run} (expected > 100)", False))
                
                all_passed = all(check[1] for check in checks)
                
                if all_passed:
                    self.result.add_result(
                        "Final Status Verification",
                        "PASS",
                        "All completion criteria met",
                        {
                            "status": status,
                            "overall_score": overall_score,
                            "pages_crawled": pages_crawled,
                            "total_checks_run": total_checks_run,
                            "checks_passed": data.get("checks_passed"),
                            "checks_failed": data.get("checks_failed"),
                            "checks_warning": data.get("checks_warning")
                        }
                    )
                else:
                    failed_checks = [check[0] for check in checks if not check[1]]
                    self.result.add_result(
                        "Final Status Verification",
                        "FAIL",
                        f"Some criteria not met: {', '.join(failed_checks)}",
                        {
                            "status": status,
                            "overall_score": overall_score,
                            "pages_crawled": pages_crawled,
                            "total_checks_run": total_checks_run
                        }
                    )
            else:
                self.result.add_result(
                    "Final Status Verification",
                    "FAIL",
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.result.add_result(
                "Final Status Verification",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_download_pdf(self):
        """Step 9: Download PDF report"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 9: DOWNLOAD PDF REPORT ==={Colors.END}")
        
        if not self.audit_id:
            self.result.add_result(
                "Download PDF",
                "FAIL",
                "No audit ID available"
            )
            return
        
        try:
            response = self.session.get(f"{BASE_URL}/reports/{self.audit_id}/pdf")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                content_length = len(response.content)
                
                checks = []
                
                if 'application/pdf' in content_type:
                    checks.append(("Content-Type is application/pdf", True))
                else:
                    checks.append((f"Content-Type is '{content_type}' (expected application/pdf)", False))
                
                if content_length > 10240:  # > 10KB
                    checks.append((f"Content size is {content_length} bytes (> 10KB)", True))
                else:
                    checks.append((f"Content size is {content_length} bytes (expected > 10KB)", False))
                
                all_passed = all(check[1] for check in checks)
                
                if all_passed:
                    self.result.add_result(
                        "Download PDF",
                        "PASS",
                        "PDF report downloaded successfully",
                        {
                            "content_type": content_type,
                            "size_bytes": content_length,
                            "size_kb": round(content_length / 1024, 2)
                        }
                    )
                else:
                    failed_checks = [check[0] for check in checks if not check[1]]
                    self.result.add_result(
                        "Download PDF",
                        "FAIL",
                        f"Verification failed: {', '.join(failed_checks)}",
                        {
                            "content_type": content_type,
                            "size_bytes": content_length
                        }
                    )
            else:
                self.result.add_result(
                    "Download PDF",
                    "FAIL",
                    f"Status code: {response.status_code}, Response: {response.text[:200]}"
                )
        except Exception as e:
            self.result.add_result(
                "Download PDF",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_download_docx(self):
        """Step 10: Download DOCX report"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 10: DOWNLOAD DOCX REPORT ==={Colors.END}")
        
        if not self.audit_id:
            self.result.add_result(
                "Download DOCX",
                "FAIL",
                "No audit ID available"
            )
            return
        
        try:
            response = self.session.get(f"{BASE_URL}/reports/{self.audit_id}/docx")
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                content_length = len(response.content)
                
                checks = []
                
                expected_docx_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                if expected_docx_type in content_type:
                    checks.append(("Content-Type is correct DOCX type", True))
                else:
                    checks.append((f"Content-Type is '{content_type}' (expected {expected_docx_type})", False))
                
                if content_length > 10240:  # > 10KB
                    checks.append((f"Content size is {content_length} bytes (> 10KB)", True))
                else:
                    checks.append((f"Content size is {content_length} bytes (expected > 10KB)", False))
                
                all_passed = all(check[1] for check in checks)
                
                if all_passed:
                    self.result.add_result(
                        "Download DOCX",
                        "PASS",
                        "DOCX report downloaded successfully",
                        {
                            "content_type": content_type,
                            "size_bytes": content_length,
                            "size_kb": round(content_length / 1024, 2)
                        }
                    )
                else:
                    failed_checks = [check[0] for check in checks if not check[1]]
                    self.result.add_result(
                        "Download DOCX",
                        "FAIL",
                        f"Verification failed: {', '.join(failed_checks)}",
                        {
                            "content_type": content_type,
                            "size_bytes": content_length
                        }
                    )
            else:
                self.result.add_result(
                    "Download DOCX",
                    "FAIL",
                    f"Status code: {response.status_code}, Response: {response.text[:200]}"
                )
        except Exception as e:
            self.result.add_result(
                "Download DOCX",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_check_opportunities(self):
        """Step 11: Check opportunities endpoint"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 11: CHECK OPPORTUNITIES ==={Colors.END}")
        
        if not self.audit_id:
            self.result.add_result(
                "Check Opportunities",
                "FAIL",
                "No audit ID available"
            )
            return
        
        try:
            response = self.session.get(f"{BASE_URL}/audits/{self.audit_id}/opportunities/")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) >= 1:
                        self.result.add_result(
                            "Check Opportunities",
                            "PASS",
                            f"Found {len(data)} content opportunities",
                            {
                                "count": len(data),
                                "sample": data[0] if data else None
                            }
                        )
                    else:
                        self.result.add_result(
                            "Check Opportunities",
                            "WARNING",
                            "No opportunities found (expected at least 1)",
                            {"count": 0}
                        )
                else:
                    self.result.add_result(
                        "Check Opportunities",
                        "FAIL",
                        f"Response is not a list: {type(data)}"
                    )
            else:
                self.result.add_result(
                    "Check Opportunities",
                    "FAIL",
                    f"Status code: {response.status_code}, Response: {response.text[:200]}"
                )
        except Exception as e:
            self.result.add_result(
                "Check Opportunities",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_check_competitors(self):
        """Step 12: Check competitors endpoint"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 12: CHECK COMPETITORS ==={Colors.END}")
        
        if not self.audit_id:
            self.result.add_result(
                "Check Competitors",
                "FAIL",
                "No audit ID available"
            )
            return
        
        try:
            response = self.session.get(f"{BASE_URL}/audits/{self.audit_id}/competitors/")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.result.add_result(
                        "Check Competitors",
                        "PASS",
                        f"Competitors endpoint working (found {len(data)} competitors)",
                        {
                            "count": len(data),
                            "note": "Empty list is OK for new audits"
                        }
                    )
                else:
                    self.result.add_result(
                        "Check Competitors",
                        "FAIL",
                        f"Response is not a list: {type(data)}"
                    )
            else:
                self.result.add_result(
                    "Check Competitors",
                    "FAIL",
                    f"Status code: {response.status_code}, Response: {response.text[:200]}"
                )
        except Exception as e:
            self.result.add_result(
                "Check Competitors",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def test_chat_with_orchestrator(self):
        """Step 13: Send message to chat orchestrator"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}=== STEP 13: CHAT WITH ORCHESTRATOR ==={Colors.END}")
        
        if not self.audit_id:
            self.result.add_result(
                "Chat with Orchestrator",
                "FAIL",
                "No audit ID available"
            )
            return
        
        try:
            chat_data = {
                "audit_id": self.audit_id,
                "content": "What are my top 3 SEO improvements?"
            }
            
            response = self.session.post(f"{BASE_URL}/chat/", json=chat_data)
            
            if response.status_code == 201:
                data = response.json()
                
                checks = []
                
                if "role" in data and data["role"] == "assistant":
                    checks.append(("Response has assistant role", True))
                else:
                    checks.append(("Response missing assistant role", False))
                
                if "content" in data and data["content"] and len(data["content"]) > 10:
                    checks.append((f"Response content is not empty ({len(data['content'])} chars)", True))
                else:
                    checks.append(("Response content is empty or too short", False))
                
                all_passed = all(check[1] for check in checks)
                
                if all_passed:
                    self.result.add_result(
                        "Chat with Orchestrator",
                        "PASS",
                        "Chat response received successfully",
                        {
                            "role": data.get("role"),
                            "content_length": len(data.get("content", "")),
                            "content_preview": data.get("content", "")[:200] + "..."
                        }
                    )
                else:
                    failed_checks = [check[0] for check in checks if not check[1]]
                    self.result.add_result(
                        "Chat with Orchestrator",
                        "FAIL",
                        f"Verification failed: {', '.join(failed_checks)}",
                        data
                    )
            else:
                self.result.add_result(
                    "Chat with Orchestrator",
                    "FAIL",
                    f"Status code: {response.status_code}, Response: {response.text[:200]}"
                )
        except Exception as e:
            self.result.add_result(
                "Chat with Orchestrator",
                "FAIL",
                f"Exception: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run complete audit workflow test"""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}COMPLETE END-TO-END AUDIT WORKFLOW TEST{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}{'='*80}{Colors.END}")
        
        # Run tests in sequence
        self.test_superadmin_login()
        self.test_create_audit()
        self.test_wait_and_check_status_first()
        self.test_wait_and_verify_completion()
        self.test_download_pdf()
        self.test_download_docx()
        self.test_check_opportunities()
        self.test_check_competitors()
        self.test_chat_with_orchestrator()
        
        # Print summary
        self.result.print_summary()
        
        # Return exit code
        return 0 if self.result.failed == 0 else 1

def main():
    tester = AuditWorkflowTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
