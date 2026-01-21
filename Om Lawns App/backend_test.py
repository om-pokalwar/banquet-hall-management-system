import requests
import sys
from datetime import datetime
import json

class BanquetHallAPITester:
    def __init__(self, base_url="https://omshiv-banquets.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_id = None
        self.hall_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login(self, username, password):
        """Test admin login"""
        success, response = self.run_test(
            f"Admin Login ({username})",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.admin_id = response.get('admin', {}).get('id')
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_get_halls(self):
        """Test getting halls"""
        success, response = self.run_test(
            "Get Halls",
            "GET",
            "halls",
            200
        )
        if success and response:
            self.hall_id = response[0].get('id') if response else None
            print(f"   Found {len(response)} halls")
            return True
        return False

    def test_get_services(self):
        """Test getting services"""
        success, response = self.run_test(
            "Get Services",
            "GET",
            "services",
            200
        )
        if success:
            print(f"   Found {len(response)} services")
            return True
        return False

    def test_get_packages(self):
        """Test getting packages"""
        success, response = self.run_test(
            "Get Packages",
            "GET",
            "packages",
            200
        )
        if success:
            print(f"   Found {len(response)} packages")
            return True
        return False

    def test_get_shubh_dates(self):
        """Test getting shubh dates"""
        success, response = self.run_test(
            "Get Shubh Dates",
            "GET",
            "shubh-dates",
            200
        )
        if success:
            print(f"   Found {len(response)} shubh dates")
            return True
        return False

    def test_create_service(self):
        """Test creating a service (requires auth)"""
        if not self.token or not self.hall_id:
            print("❌ Skipping service creation - no auth token or hall_id")
            return False
            
        service_data = {
            "hall_id": self.hall_id,
            "name": "Test Service",
            "name_mr": "टेस्ट सेवा",
            "price": 5000,
            "description": "Test service description",
            "description_mr": "टेस्ट सेवा वर्णन"
        }
        
        success, response = self.run_test(
            "Create Service",
            "POST",
            "services",
            200,
            data=service_data
        )
        return success

    def test_create_package(self):
        """Test creating a package (requires auth)"""
        if not self.token or not self.hall_id:
            print("❌ Skipping package creation - no auth token or hall_id")
            return False
            
        package_data = {
            "hall_id": self.hall_id,
            "package_type": "thali",
            "name": "Test Thali Package",
            "name_mr": "टेस्ट थाली पॅकेज",
            "items": [{"name": "Rice", "name_mr": "भात"}],
            "rent": 10000,
            "light_charges": 2000
        }
        
        success, response = self.run_test(
            "Create Package",
            "POST",
            "packages",
            200,
            data=package_data
        )
        return success

    def test_get_bookings(self):
        """Test getting bookings (requires auth)"""
        if not self.token:
            print("❌ Skipping bookings - no auth token")
            return False
            
        success, response = self.run_test(
            "Get Bookings",
            "GET",
            "bookings",
            200
        )
        if success:
            print(f"   Found {len(response)} bookings")
            return True
        return False

    def test_get_bills(self):
        """Test getting bills (requires auth)"""
        if not self.token:
            print("❌ Skipping bills - no auth token")
            return False
            
        success, response = self.run_test(
            "Get Bills",
            "GET",
            "bills",
            200
        )
        if success:
            print(f"   Found {len(response)} bills")
            return True
        return False

    def test_get_settings(self):
        """Test getting settings"""
        success, response = self.run_test(
            "Get Settings",
            "GET",
            "settings",
            200
        )
        return success

    def test_change_password(self):
        """Test changing password (requires auth)"""
        if not self.token:
            print("❌ Skipping password change - no auth token")
            return False
            
        # Test with invalid old password first
        success, response = self.run_test(
            "Change Password (Invalid Old)",
            "POST",
            "auth/change-password",
            400,
            data={"old_password": "wrong_password", "new_password": "new123"}
        )
        return success

def main():
    print("🚀 Starting Banquet Hall Management System API Tests")
    print("=" * 60)
    
    # Setup
    tester = BanquetHallAPITester()
    
    # Test public endpoints first
    print("\n📋 Testing Public Endpoints...")
    tester.test_get_halls()
    tester.test_get_services()
    tester.test_get_packages()
    tester.test_get_shubh_dates()
    tester.test_get_settings()
    
    # Test admin authentication
    print("\n🔐 Testing Admin Authentication...")
    om_login_success = tester.test_admin_login("om_admin", "om123")
    
    if om_login_success:
        print("\n🔧 Testing Authenticated Endpoints (Om Admin)...")
        tester.test_create_service()
        tester.test_create_package()
        tester.test_get_bookings()
        tester.test_get_bills()
        tester.test_change_password()
    
    # Test second admin
    print("\n🔐 Testing Second Admin Authentication...")
    tester.token = None  # Reset token
    shiv_login_success = tester.test_admin_login("shiv_admin", "shiv123")
    
    if shiv_login_success:
        print("\n🔧 Testing Authenticated Endpoints (Shiv Admin)...")
        tester.test_get_bookings()
        tester.test_get_bills()
    
    # Test invalid login
    print("\n❌ Testing Invalid Login...")
    tester.token = None  # Reset token
    tester.test_admin_login("invalid_user", "invalid_pass")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())