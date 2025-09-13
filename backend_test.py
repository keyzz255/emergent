import requests
import sys
import json
from datetime import datetime

class DramaBoxAPITester:
    def __init__(self, base_url="https://apa-bisa-kamu.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("API Root", success, details)
            return success
        except Exception as e:
            self.log_test("API Root", False, str(e))
            return False

    def test_latest_dramas(self):
        """Test getting latest dramas"""
        try:
            response = requests.get(f"{self.api_url}/dramas/latest", timeout=30)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if data.get("success") and data.get("data"):
                    drama_count = len(data["data"])
                    details += f", Found {drama_count} dramas"
                    # Check first drama structure
                    if drama_count > 0:
                        first_drama = data["data"][0]
                        required_fields = ["bookId", "bookName"]
                        missing_fields = [field for field in required_fields if field not in first_drama]
                        if missing_fields:
                            details += f", Missing fields: {missing_fields}"
                        else:
                            details += f", Sample drama: {first_drama.get('bookName', 'Unknown')}"
                else:
                    success = False
                    details += f", Invalid response structure: {data}"
            
            self.log_test("Latest Dramas", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Latest Dramas", False, str(e))
            return False, {}

    def test_search_dramas(self, keyword="cinta"):
        """Test drama search functionality"""
        try:
            payload = {"keyword": keyword}
            response = requests.post(
                f"{self.api_url}/dramas/search", 
                json=payload, 
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Keyword: '{keyword}'"
            
            if success:
                data = response.json()
                if data.get("success"):
                    result_count = len(data.get("data", []))
                    details += f", Found {result_count} results"
                    if result_count > 0:
                        first_result = data["data"][0]
                        details += f", Sample: {first_result.get('bookName', 'Unknown')}"
                else:
                    details += f", Search returned no results: {data.get('message', 'Unknown error')}"
            
            self.log_test("Search Dramas", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Search Dramas", False, str(e))
            return False, {}

    def test_categories(self):
        """Test getting drama categories"""
        try:
            response = requests.get(f"{self.api_url}/dramas/categories", timeout=30)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                if data.get("success") and data.get("categories"):
                    category_count = len(data["categories"])
                    details += f", Found {category_count} categories"
                    if category_count > 0:
                        sample_categories = data["categories"][:3]  # Show first 3
                        details += f", Sample: {sample_categories}"
                else:
                    success = False
                    details += f", Invalid response structure: {data}"
            
            self.log_test("Drama Categories", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Drama Categories", False, str(e))
            return False, {}

    def test_dramas_by_category(self, category):
        """Test getting dramas by category"""
        try:
            payload = {"category": category}
            response = requests.post(
                f"{self.api_url}/dramas/by-category", 
                json=payload, 
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Category: '{category}'"
            
            if success:
                data = response.json()
                if data.get("success"):
                    result_count = len(data.get("data", []))
                    details += f", Found {result_count} dramas"
                    if result_count > 0:
                        first_drama = data["data"][0]
                        details += f", Sample: {first_drama.get('bookName', 'Unknown')}"
                else:
                    details += f", Category search returned no results: {data.get('message', 'Unknown error')}"
            
            self.log_test(f"Category Filter ({category})", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test(f"Category Filter ({category})", False, str(e))
            return False, {}

    def test_stream_link(self, book_id, episode=1):
        """Test getting stream link for a drama"""
        try:
            payload = {"book_id": book_id, "episode": episode}
            response = requests.post(
                f"{self.api_url}/dramas/stream", 
                json=payload, 
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            success = response.status_code == 200
            details = f"Status: {response.status_code}, BookID: {book_id}, Episode: {episode}"
            
            if success:
                data = response.json()
                if data.get("success") and data.get("stream_url"):
                    details += f", Stream URL found: {data['stream_url'][:50]}..."
                    if data.get("available_qualities"):
                        details += f", Qualities: {data['available_qualities']}"
                else:
                    success = False
                    details += f", No stream URL: {data.get('message', 'Unknown error')}"
            
            self.log_test("Stream Link", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Stream Link", False, str(e))
            return False, {}

    def test_status_endpoints(self):
        """Test status check endpoints"""
        try:
            # Test POST status
            test_data = {"client_name": f"test_client_{datetime.now().strftime('%H%M%S')}"}
            response = requests.post(
                f"{self.api_url}/status", 
                json=test_data, 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            post_success = response.status_code == 200
            
            # Test GET status
            response = requests.get(f"{self.api_url}/status", timeout=10)
            get_success = response.status_code == 200
            
            success = post_success and get_success
            details = f"POST: {post_success}, GET: {get_success}"
            
            self.log_test("Status Endpoints", success, details)
            return success
        except Exception as e:
            self.log_test("Status Endpoints", False, str(e))
            return False

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting DramaBox API Comprehensive Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)

        # Test 1: API Root
        self.test_api_root()

        # Test 2: Latest Dramas
        latest_success, latest_data = self.test_latest_dramas()
        
        # Test 3: Search Dramas
        search_success, search_data = self.test_search_dramas("cinta")
        
        # Test 4: Stream Link (use drama from latest or search)
        book_id = None
        if latest_success and latest_data.get("data"):
            book_id = latest_data["data"][0].get("bookId")
        elif search_success and search_data.get("data"):
            book_id = search_data["data"][0].get("bookId")
        
        if book_id:
            self.test_stream_link(book_id)
        else:
            self.log_test("Stream Link", False, "No valid book_id found from previous tests")

        # Test 5: Status Endpoints
        self.test_status_endpoints()

        # Print Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Print failed tests details
        failed_tests = [test for test in self.test_results if not test["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['name']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = DramaBoxAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())