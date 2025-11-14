#!/usr/bin/env python3
"""
Theme Management and LLM Settings Test Suite
Tests the newly implemented Theme Management and LLM Settings features as per review request
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://theme-fix-admin.preview.emergentagent.com/api"
SUPERADMIN_EMAIL = "superadmin@test.com"
SUPERADMIN_PASSWORD = "test123"
TEST_USER_EMAIL = "testuser@mjseo.com"
TEST_USER_PASSWORD = "testpass123"

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

class ThemeLLMTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.result = TestResult()
        self.superadmin_token = None
        self.user_token = None
        self.test_theme_id = None
        self.test_llm_id = None
        self.inactive_theme_id = None
        self.inactive_llm_id = None
    
    def login_superadmin(self):
        """Login as superadmin"""
        print(f"\n{Colors.BLUE}=== SUPERADMIN LOGIN ==={Colors.END}")
        
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
                    self.result.add_result("1. Superadmin Login", "PASS")
                    return True
                else:
                    self.result.add_result("1. Superadmin Login", "FAIL", "Missing access token")
                    return False
            else:
                self.result.add_result("1. Superadmin Login", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.result.add_result("1. Superadmin Login", "FAIL", str(e))
            return False
    
    def login_regular_user(self):
        """Login as regular user for access control tests"""
        try:
            # Try to register first
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "Test User"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                self.user_token = data.get("access_token")
            elif response.status_code == 400:
                # User exists, try login
                login_data = {
                    "email": TEST_USER_EMAIL,
                    "password": TEST_USER_PASSWORD
                }
                response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.user_token = data.get("access_token")
            
            return self.user_token is not None
        except Exception:
            return False
    
    def test_theme_management(self):
        """Test Theme Management features"""
        print(f"\n{Colors.PURPLE}=== THEME MANAGEMENT TESTS ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("Theme Management", "FAIL", "No superadmin token")
            return
        
        headers = {"Authorization": f"Bearer {self.superadmin_token}"}
        
        # Test 2: GET /api/themes/ - List all themes
        try:
            response = self.session.get(f"{BASE_URL}/themes/", headers=headers)
            
            if response.status_code == 200:
                themes = response.json()
                if isinstance(themes, list):
                    self.result.add_result("2. GET /api/themes/ - List themes", "PASS", f"Found {len(themes)} themes")
                    # Store an existing theme ID for later tests
                    if themes:
                        for theme in themes:
                            if not theme.get("is_active"):
                                self.inactive_theme_id = theme["id"]
                                break
                else:
                    self.result.add_result("2. GET /api/themes/ - List themes", "FAIL", "Invalid response format")
            else:
                self.result.add_result("2. GET /api/themes/ - List themes", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("2. GET /api/themes/ - List themes", "FAIL", str(e))
        
        # Test 3: POST /api/themes/ - Create a new theme
        try:
            theme_data = {
                "name": "Test Theme",
                "primary_color": "#ff6b6b",
                "secondary_color": "#4ecdc4",
                "accent_color": "#ffe66d",
                "background_color": "#2d3748",
                "surface_color": "#374151",
                "text_primary": "#ffffff",
                "text_secondary": "#d1d5db"
            }
            
            response = self.session.post(f"{BASE_URL}/themes/", json=theme_data, headers=headers)
            
            if response.status_code == 201:
                created_theme = response.json()
                if "id" in created_theme and created_theme.get("name") == "Test Theme":
                    self.test_theme_id = created_theme["id"]
                    self.result.add_result("3. POST /api/themes/ - Create theme", "PASS", f"Created theme ID: {self.test_theme_id}")
                else:
                    self.result.add_result("3. POST /api/themes/ - Create theme", "FAIL", "Invalid created theme response")
            elif response.status_code == 400 and "already exists" in response.text:
                self.result.add_result("3. POST /api/themes/ - Create theme", "WARNING", "Theme already exists, will use existing")
                # Try to find the existing theme
                response = self.session.get(f"{BASE_URL}/themes/", headers=headers)
                if response.status_code == 200:
                    themes = response.json()
                    for theme in themes:
                        if theme.get("name") == "Test Theme":
                            self.test_theme_id = theme["id"]
                            break
            else:
                self.result.add_result("3. POST /api/themes/ - Create theme", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("3. POST /api/themes/ - Create theme", "FAIL", str(e))
        
        # Test 4: GET /api/themes/ - Verify new theme appears
        try:
            response = self.session.get(f"{BASE_URL}/themes/", headers=headers)
            
            if response.status_code == 200:
                themes = response.json()
                theme_found = False
                for theme in themes:
                    if theme.get("name") == "Test Theme":
                        theme_found = True
                        break
                
                if theme_found:
                    self.result.add_result("4. GET /api/themes/ - Verify new theme", "PASS", "Test Theme found in list")
                else:
                    self.result.add_result("4. GET /api/themes/ - Verify new theme", "FAIL", "Test Theme not found in list")
            else:
                self.result.add_result("4. GET /api/themes/ - Verify new theme", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("4. GET /api/themes/ - Verify new theme", "FAIL", str(e))
        
        # Test 5: PUT /api/themes/{new_theme_id} - Update the theme colors
        if self.test_theme_id:
            try:
                update_data = {
                    "primary_color": "#ff0000",
                    "secondary_color": "#00ff00"
                }
                
                response = self.session.put(f"{BASE_URL}/themes/{self.test_theme_id}", json=update_data, headers=headers)
                
                if response.status_code == 200:
                    updated_theme = response.json()
                    if updated_theme.get("primary_color") == "#ff0000":
                        self.result.add_result("5. PUT /api/themes/{id} - Update theme", "PASS", "Theme colors updated successfully")
                    else:
                        self.result.add_result("5. PUT /api/themes/{id} - Update theme", "FAIL", "Theme colors not updated")
                else:
                    self.result.add_result("5. PUT /api/themes/{id} - Update theme", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("5. PUT /api/themes/{id} - Update theme", "FAIL", str(e))
        
        # Test 6: POST /api/themes/{new_theme_id}/activate - Try to activate the new theme
        if self.test_theme_id:
            try:
                response = self.session.post(f"{BASE_URL}/themes/{self.test_theme_id}/activate", headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result and "activated" in result["message"].lower():
                        self.result.add_result("6. POST /api/themes/{id}/activate - Activate theme", "PASS", "Theme activated successfully")
                    else:
                        self.result.add_result("6. POST /api/themes/{id}/activate - Activate theme", "FAIL", "Invalid activation response")
                else:
                    self.result.add_result("6. POST /api/themes/{id}/activate - Activate theme", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("6. POST /api/themes/{id}/activate - Activate theme", "FAIL", str(e))
        
        # Test 7: DELETE /api/themes/{inactive_theme_id} - Delete an inactive theme
        if self.inactive_theme_id:
            try:
                response = self.session.delete(f"{BASE_URL}/themes/{self.inactive_theme_id}", headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result and "deleted" in result["message"].lower():
                        self.result.add_result("7. DELETE /api/themes/{id} - Delete inactive theme", "PASS", "Inactive theme deleted successfully")
                    else:
                        self.result.add_result("7. DELETE /api/themes/{id} - Delete inactive theme", "FAIL", "Invalid deletion response")
                else:
                    self.result.add_result("7. DELETE /api/themes/{id} - Delete inactive theme", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("7. DELETE /api/themes/{id} - Delete inactive theme", "FAIL", str(e))
        else:
            self.result.add_result("7. DELETE /api/themes/{id} - Delete inactive theme", "WARNING", "No inactive theme available for deletion test")
        
        # Test 8: Verify cannot delete active theme
        if self.test_theme_id:
            try:
                response = self.session.delete(f"{BASE_URL}/themes/{self.test_theme_id}", headers=headers)
                
                if response.status_code == 400:
                    self.result.add_result("8. Verify cannot delete active theme", "PASS", "Active theme deletion correctly prevented")
                elif response.status_code == 200:
                    self.result.add_result("8. Verify cannot delete active theme", "FAIL", "Active theme was deleted (should be prevented)")
                else:
                    self.result.add_result("8. Verify cannot delete active theme", "WARNING", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.result.add_result("8. Verify cannot delete active theme", "FAIL", str(e))
    
    def test_llm_settings(self):
        """Test LLM Settings features"""
        print(f"\n{Colors.PURPLE}=== LLM SETTINGS TESTS ==={Colors.END}")
        
        if not self.superadmin_token:
            self.result.add_result("LLM Settings", "FAIL", "No superadmin token")
            return
        
        headers = {"Authorization": f"Bearer {self.superadmin_token}"}
        
        # Test 9: GET /api/admin/llm-settings/ - List all LLM settings
        try:
            response = self.session.get(f"{BASE_URL}/admin/llm-settings/", headers=headers)
            
            if response.status_code == 200:
                settings = response.json()
                if isinstance(settings, list):
                    self.result.add_result("9. GET /api/admin/llm-settings/ - List LLM settings", "PASS", f"Found {len(settings)} LLM settings")
                    # Store an existing inactive setting ID for later tests
                    if settings:
                        for setting in settings:
                            if not setting.get("is_active"):
                                self.inactive_llm_id = setting["id"]
                                break
                else:
                    self.result.add_result("9. GET /api/admin/llm-settings/ - List LLM settings", "FAIL", "Invalid response format")
            else:
                self.result.add_result("9. GET /api/admin/llm-settings/ - List LLM settings", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("9. GET /api/admin/llm-settings/ - List LLM settings", "FAIL", str(e))
        
        # Test 10: GET /api/admin/llm-settings/active - Get currently active LLM
        try:
            response = self.session.get(f"{BASE_URL}/admin/llm-settings/active", headers=headers)
            
            if response.status_code == 200:
                active_llm = response.json()
                if active_llm and "provider" in active_llm:
                    self.result.add_result("10. GET /api/admin/llm-settings/active - Get active LLM", "PASS", f"Active LLM: {active_llm.get('provider')} - {active_llm.get('model_name')}")
                else:
                    self.result.add_result("10. GET /api/admin/llm-settings/active - Get active LLM", "WARNING", "No active LLM found")
            else:
                self.result.add_result("10. GET /api/admin/llm-settings/active - Get active LLM", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("10. GET /api/admin/llm-settings/active - Get active LLM", "FAIL", str(e))
        
        # Test 11-15: Get available models for each provider
        providers = ["groq", "openai", "anthropic", "gemini", "ollama"]
        test_numbers = [11, 12, 13, 14, 15]
        
        for i, provider in enumerate(providers):
            try:
                response = self.session.get(f"{BASE_URL}/admin/llm-settings/models/{provider}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "models" in data and isinstance(data["models"], list):
                        model_count = len(data["models"])
                        self.result.add_result(f"{test_numbers[i]}. GET /api/admin/llm-settings/models/{provider} - Get {provider.title()} models", "PASS", f"Found {model_count} {provider} models")
                    else:
                        self.result.add_result(f"{test_numbers[i]}. GET /api/admin/llm-settings/models/{provider} - Get {provider.title()} models", "FAIL", "Invalid models response format")
                else:
                    self.result.add_result(f"{test_numbers[i]}. GET /api/admin/llm-settings/models/{provider} - Get {provider.title()} models", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result(f"{test_numbers[i]}. GET /api/admin/llm-settings/models/{provider} - Get {provider.title()} models", "FAIL", str(e))
        
        # Test 16: POST /api/admin/llm-settings/ - Create new LLM setting
        try:
            llm_data = {
                "provider": "openai",
                "model_name": "gpt-4o",
                "api_key_ref": "OPENAI_API_KEY",
                "temperature": 0.7,
                "max_tokens": 4096,
                "description": "GPT-4o for testing"
            }
            
            response = self.session.post(f"{BASE_URL}/admin/llm-settings/", json=llm_data, headers=headers)
            
            if response.status_code == 201:
                created_llm = response.json()
                if "id" in created_llm and created_llm.get("model_name") == "gpt-4o":
                    self.test_llm_id = created_llm["id"]
                    self.result.add_result("16. POST /api/admin/llm-settings/ - Create LLM setting", "PASS", f"Created LLM setting ID: {self.test_llm_id}")
                else:
                    self.result.add_result("16. POST /api/admin/llm-settings/ - Create LLM setting", "FAIL", "Invalid created LLM response")
            else:
                self.result.add_result("16. POST /api/admin/llm-settings/ - Create LLM setting", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.result.add_result("16. POST /api/admin/llm-settings/ - Create LLM setting", "FAIL", str(e))
        
        # Test 17: GET /api/admin/llm-settings/ - Verify new LLM setting created
        try:
            response = self.session.get(f"{BASE_URL}/admin/llm-settings/", headers=headers)
            
            if response.status_code == 200:
                settings = response.json()
                llm_found = False
                for setting in settings:
                    if setting.get("model_name") == "gpt-4o" and setting.get("provider") == "openai":
                        llm_found = True
                        break
                
                if llm_found:
                    self.result.add_result("17. GET /api/admin/llm-settings/ - Verify new LLM created", "PASS", "GPT-4o LLM setting found in list")
                else:
                    self.result.add_result("17. GET /api/admin/llm-settings/ - Verify new LLM created", "FAIL", "GPT-4o LLM setting not found in list")
            else:
                self.result.add_result("17. GET /api/admin/llm-settings/ - Verify new LLM created", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("17. GET /api/admin/llm-settings/ - Verify new LLM created", "FAIL", str(e))
        
        # Test 18: PUT /api/admin/llm-settings/{new_llm_id} - Update temperature to 0.9
        if self.test_llm_id:
            try:
                update_data = {
                    "temperature": 0.9
                }
                
                response = self.session.put(f"{BASE_URL}/admin/llm-settings/{self.test_llm_id}", json=update_data, headers=headers)
                
                if response.status_code == 200:
                    updated_llm = response.json()
                    if updated_llm.get("temperature") == 0.9:
                        self.result.add_result("18. PUT /api/admin/llm-settings/{id} - Update temperature", "PASS", "Temperature updated to 0.9")
                    else:
                        self.result.add_result("18. PUT /api/admin/llm-settings/{id} - Update temperature", "FAIL", f"Temperature not updated correctly: {updated_llm.get('temperature')}")
                else:
                    self.result.add_result("18. PUT /api/admin/llm-settings/{id} - Update temperature", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("18. PUT /api/admin/llm-settings/{id} - Update temperature", "FAIL", str(e))
        
        # Test 19: POST /api/admin/llm-settings/{new_llm_id}/activate - Activate the new LLM
        if self.test_llm_id:
            try:
                response = self.session.post(f"{BASE_URL}/admin/llm-settings/{self.test_llm_id}/activate", headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result and "activated" in result["message"].lower():
                        self.result.add_result("19. POST /api/admin/llm-settings/{id}/activate - Activate LLM", "PASS", "LLM activated successfully")
                    else:
                        self.result.add_result("19. POST /api/admin/llm-settings/{id}/activate - Activate LLM", "FAIL", "Invalid activation response")
                else:
                    self.result.add_result("19. POST /api/admin/llm-settings/{id}/activate - Activate LLM", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("19. POST /api/admin/llm-settings/{id}/activate - Activate LLM", "FAIL", str(e))
        
        # Test 20: GET /api/admin/llm-settings/active - Verify new LLM is now active
        try:
            response = self.session.get(f"{BASE_URL}/admin/llm-settings/active", headers=headers)
            
            if response.status_code == 200:
                active_llm = response.json()
                if active_llm and active_llm.get("model_name") == "gpt-4o":
                    self.result.add_result("20. GET /api/admin/llm-settings/active - Verify new LLM active", "PASS", "GPT-4o is now the active LLM")
                else:
                    self.result.add_result("20. GET /api/admin/llm-settings/active - Verify new LLM active", "FAIL", f"Expected GPT-4o, got: {active_llm.get('model_name') if active_llm else 'None'}")
            else:
                self.result.add_result("20. GET /api/admin/llm-settings/active - Verify new LLM active", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.result.add_result("20. GET /api/admin/llm-settings/active - Verify new LLM active", "FAIL", str(e))
        
        # Test 21: DELETE /api/admin/llm-settings/{inactive_llm_id} - Delete inactive LLM setting
        if self.inactive_llm_id:
            try:
                response = self.session.delete(f"{BASE_URL}/admin/llm-settings/{self.inactive_llm_id}", headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result and "deleted" in result["message"].lower():
                        self.result.add_result("21. DELETE /api/admin/llm-settings/{id} - Delete inactive LLM", "PASS", "Inactive LLM setting deleted successfully")
                    else:
                        self.result.add_result("21. DELETE /api/admin/llm-settings/{id} - Delete inactive LLM", "FAIL", "Invalid deletion response")
                else:
                    self.result.add_result("21. DELETE /api/admin/llm-settings/{id} - Delete inactive LLM", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.result.add_result("21. DELETE /api/admin/llm-settings/{id} - Delete inactive LLM", "FAIL", str(e))
        else:
            self.result.add_result("21. DELETE /api/admin/llm-settings/{id} - Delete inactive LLM", "WARNING", "No inactive LLM setting available for deletion test")
        
        # Test 22: Verify cannot delete active LLM setting
        if self.test_llm_id:
            try:
                response = self.session.delete(f"{BASE_URL}/admin/llm-settings/{self.test_llm_id}", headers=headers)
                
                if response.status_code == 400:
                    self.result.add_result("22. Verify cannot delete active LLM setting", "PASS", "Active LLM deletion correctly prevented")
                elif response.status_code == 200:
                    self.result.add_result("22. Verify cannot delete active LLM setting", "FAIL", "Active LLM was deleted (should be prevented)")
                else:
                    self.result.add_result("22. Verify cannot delete active LLM setting", "WARNING", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.result.add_result("22. Verify cannot delete active LLM setting", "FAIL", str(e))
    
    def test_access_control(self):
        """Test access control for theme and LLM settings"""
        print(f"\n{Colors.PURPLE}=== ACCESS CONTROL TESTS ==={Colors.END}")
        
        # Login regular user
        if not self.login_regular_user():
            self.result.add_result("Access Control Setup", "WARNING", "Could not login regular user, skipping access control tests")
            return
        
        user_headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test 23: Try accessing theme management with regular user (should fail with 403)
        try:
            response = self.session.get(f"{BASE_URL}/themes/", headers=user_headers)
            
            if response.status_code == 403:
                self.result.add_result("23. Theme access control - Regular user denied", "PASS", "Regular user correctly denied theme access")
            else:
                self.result.add_result("23. Theme access control - Regular user denied", "FAIL", f"Regular user should be denied, got: {response.status_code}")
        except Exception as e:
            self.result.add_result("23. Theme access control - Regular user denied", "FAIL", str(e))
        
        # Test 24: Try accessing LLM settings with regular user (should fail with 403)
        try:
            response = self.session.get(f"{BASE_URL}/admin/llm-settings/", headers=user_headers)
            
            if response.status_code == 403:
                self.result.add_result("24. LLM settings access control - Regular user denied", "PASS", "Regular user correctly denied LLM settings access")
            else:
                self.result.add_result("24. LLM settings access control - Regular user denied", "FAIL", f"Regular user should be denied, got: {response.status_code}")
        except Exception as e:
            self.result.add_result("24. LLM settings access control - Regular user denied", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run all tests as specified in the review request"""
        print(f"{Colors.BOLD}{Colors.PURPLE}🚀 Theme Management and LLM Settings Test Suite{Colors.END}")
        print(f"Testing against: {BASE_URL}")
        print("=" * 80)
        
        # Step 1: Login as superadmin
        if not self.login_superadmin():
            print(f"{Colors.RED}Cannot proceed without superadmin login{Colors.END}")
            return False
        
        # Run Theme Management Tests (2-8)
        self.test_theme_management()
        
        # Run LLM Settings Tests (9-22)
        self.test_llm_settings()
        
        # Run Access Control Tests (23-24)
        self.test_access_control()
        
        # Print final summary
        self.result.print_summary()
        
        return self.result.failed == 0

def main():
    """Main test runner"""
    tester = ThemeLLMTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Theme Management and LLM Settings are working correctly.{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED! Check the results above.{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())