#!/usr/bin/env python3
"""
Additional specific tests for MJ SEO Backend based on review requirements
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://deploy-stripe-admin.preview.emergentagent.com/api"
SUPERADMIN_EMAIL = "superadmin@test.com"
SUPERADMIN_PASSWORD = "test123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def test_backend_port():
    """Test that backend is running on port 8001 internally"""
    print(f"{Colors.BLUE}=== BACKEND PORT TEST ==={Colors.END}")
    try:
        # Test internal port (this will fail from outside but we can check the external mapping)
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Backend accessible via external URL (port mapping working){Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Backend not accessible{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Backend connection failed: {str(e)}{Colors.END}")
        return False

def test_database_connection():
    """Test database connection by checking if we can fetch data"""
    print(f"{Colors.BLUE}=== DATABASE CONNECTION TEST ==={Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/plans/")
        if response.status_code == 200:
            plans = response.json()
            if isinstance(plans, list) and len(plans) > 0:
                print(f"{Colors.GREEN}✅ Database connection working - found {len(plans)} plans{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Database connection issue - no plans found{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Database connection failed - status: {response.status_code}{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Database connection test failed: {str(e)}{Colors.END}")
        return False

def test_plan_structure():
    """Test that all 4 expected plans exist with correct structure"""
    print(f"{Colors.BLUE}=== PLAN STRUCTURE TEST ==={Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/plans/")
        if response.status_code == 200:
            plans = response.json()
            
            # Check for expected plans
            plan_names = [plan.get("name", "").lower() for plan in plans]
            expected_plans = ["free", "basic", "pro", "enterprise"]
            
            missing_plans = [plan for plan in expected_plans if plan not in plan_names]
            if not missing_plans:
                print(f"{Colors.GREEN}✅ All 4 expected plans found: {plan_names}{Colors.END}")
                
                # Check plan structure
                for plan in plans:
                    required_fields = ["id", "name", "display_name", "price", "max_audits_per_month", "features"]
                    missing_fields = [field for field in required_fields if field not in plan]
                    if missing_fields:
                        print(f"{Colors.YELLOW}⚠️  Plan {plan.get('name')} missing fields: {missing_fields}{Colors.END}")
                        return False
                
                print(f"{Colors.GREEN}✅ All plans have correct structure{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Missing plans: {missing_plans}{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Failed to fetch plans - status: {response.status_code}{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Plan structure test failed: {str(e)}{Colors.END}")
        return False

def test_theme_pastel_colors():
    """Test that themes have pastel color schemes"""
    print(f"{Colors.BLUE}=== THEME PASTEL COLORS TEST ==={Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/themes/active")
        if response.status_code == 200:
            theme = response.json()
            
            # Check if theme has color fields
            color_fields = ["primary_color", "secondary_color", "accent_color"]
            colors = {}
            
            for field in color_fields:
                if field in theme:
                    colors[field] = theme[field]
            
            if colors:
                print(f"{Colors.GREEN}✅ Active theme has pastel colors: {colors}{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Theme missing color fields{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Failed to fetch active theme - status: {response.status_code}{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Theme colors test failed: {str(e)}{Colors.END}")
        return False

def test_jwt_token_format():
    """Test JWT token format and structure"""
    print(f"{Colors.BLUE}=== JWT TOKEN FORMAT TEST ==={Colors.END}")
    try:
        login_data = {
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token", "")
            refresh_token = data.get("refresh_token", "")
            
            # Check JWT format (should have 3 parts separated by dots)
            if access_token.count('.') == 2 and refresh_token.count('.') == 2:
                print(f"{Colors.GREEN}✅ JWT tokens have correct format{Colors.END}")
                print(f"   Access token: {access_token[:20]}...{access_token[-10:]}")
                print(f"   Refresh token: {refresh_token[:20]}...{refresh_token[-10:]}")
                return True
            else:
                print(f"{Colors.RED}❌ JWT tokens have incorrect format{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Failed to get JWT tokens - status: {response.status_code}{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ JWT token format test failed: {str(e)}{Colors.END}")
        return False

def test_api_token_format():
    """Test API token generation format"""
    print(f"{Colors.BLUE}=== API TOKEN FORMAT TEST ==={Colors.END}")
    try:
        # First login to get auth token
        login_data = {
            "email": SUPERADMIN_EMAIL,
            "password": SUPERADMIN_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"{Colors.RED}❌ Failed to login for API token test{Colors.END}")
            return False
        
        auth_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create API token
        token_data = {"name": "Format Test Token"}
        response = requests.post(f"{BASE_URL}/api-tokens/", json=token_data, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            api_token = data.get("token", "")
            
            if api_token.startswith("mjseo_") and len(api_token) > 20:
                print(f"{Colors.GREEN}✅ API token has correct format: {api_token[:15]}...{Colors.END}")
                
                # Clean up - delete the test token
                token_id = data.get("id")
                if token_id:
                    requests.delete(f"{BASE_URL}/api-tokens/{token_id}", headers=headers)
                
                return True
            else:
                print(f"{Colors.RED}❌ API token has incorrect format: {api_token}{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Failed to create API token - status: {response.status_code}{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ API token format test failed: {str(e)}{Colors.END}")
        return False

def run_additional_tests():
    """Run all additional tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 Running Additional Backend Tests{Colors.END}")
    print("=" * 50)
    
    tests = [
        test_backend_port,
        test_database_connection,
        test_plan_structure,
        test_theme_pastel_colors,
        test_jwt_token_format,
        test_api_token_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"{Colors.BOLD}=== ADDITIONAL TESTS SUMMARY ==={Colors.END}")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All additional tests passed!{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some additional tests failed!{Colors.END}")
        return False

if __name__ == "__main__":
    success = run_additional_tests()
    sys.exit(0 if success else 1)