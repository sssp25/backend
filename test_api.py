import requests
import json

BASE_URL = 'http://localhost:8000'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def print_test(name, passed):
    status = f"{Colors.GREEN}✓ PASSED{Colors.RESET}" if passed else f"{Colors.RED}✗ FAILED{Colors.RESET}"
    print(f"{status} - {name}")

def test_google_auth():
    print(f"{Colors.YELLOW}Note: Google OAuth testing requires a valid Google ID token{Colors.RESET}")
    print(f"{Colors.YELLOW}Skipping authentication tests - please test manually with frontend{Colors.RESET}")
    print(f"{Colors.YELLOW}See GOOGLE_OAUTH_INTEGRATION.md for integration instructions{Colors.RESET}")
    
    token = input(f"\n{Colors.YELLOW}Enter your authentication token (or press Enter to skip): {Colors.RESET}").strip()
    if token:
        return token
    return None

def test_create_category(token):
    url = f"{BASE_URL}/post/categories/"
    data = {
        "name": "Test Category",
        "description": "A test category"
    }
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        passed = response.status_code in [200, 201]
        print_test("Create Category", passed)
        if passed:
            return response.json()['id']
    except Exception as e:
        print_test("Create Category", False)
        print(f"  Error: {str(e)}")
    return None

def test_create_tag(token):
    url = f"{BASE_URL}/post/tags/"
    data = {"name": "testtag"}
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        passed = response.status_code in [200, 201]
        print_test("Create Tag", passed)
        if passed:
            return response.json()['id']
    except Exception as e:
        print_test("Create Tag", False)
        print(f"  Error: {str(e)}")
    return None

def test_create_post(token, category_id, tag_id):
    url = f"{BASE_URL}/post/posts/"
    data = {
        "title": "Test Post",
        "content": "This is a test post content",
        "category": category_id,
        "tag_ids": [tag_id] if tag_id else []
    }
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        passed = response.status_code in [200, 201]
        print_test("Create Post", passed)
        if passed:
            return response.json()['id']
    except Exception as e:
        print_test("Create Post", False)
        print(f"  Error: {str(e)}")
    return None

def test_get_feed():
    url = f"{BASE_URL}/post/feed/"
    
    try:
        response = requests.get(url)
        passed = response.status_code == 200
        print_test("Get Public Feed", passed)
    except Exception as e:
        print_test("Get Public Feed", False)
        print(f"  Error: {str(e)}")

def test_like_post(token, post_id):
    url = f"{BASE_URL}/post/posts/{post_id}/like/"
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        passed = response.status_code in [200, 201]
        print_test("Like Post", passed)
    except Exception as e:
        print_test("Like Post", False)
        print(f"  Error: {str(e)}")

def test_search_posts():
    url = f"{BASE_URL}/post/search/?q=test"
    
    try:
        response = requests.get(url)
        passed = response.status_code == 200
        print_test("Search Posts", passed)
    except Exception as e:
        print_test("Search Posts", False)
        print(f"  Error: {str(e)}")

def test_get_categories():
    url = f"{BASE_URL}/post/categories/"
    
    try:
        response = requests.get(url)
        passed = response.status_code == 200
        print_test("Get Categories", passed)
    except Exception as e:
        print_test("Get Categories", False)
        print(f"  Error: {str(e)}")

def test_get_tags():
    url = f"{BASE_URL}/post/tags/"
    
    try:
        response = requests.get(url)
        passed = response.status_code == 200
        print_test("Get Tags", passed)
    except Exception as e:
        print_test("Get Tags", False)
        print(f"  Error: {str(e)}")

def run_tests():
    print(f"\n{Colors.YELLOW}=== Pororohub API Tests ==={Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Testing Authentication...{Colors.RESET}")
    token = test_google_auth()
    
    if not token:
        print(f"\n{Colors.YELLOW}Skipping authenticated tests{Colors.RESET}")
        print(f"{Colors.YELLOW}Testing public endpoints only...{Colors.RESET}\n")
    
    print(f"\n{Colors.YELLOW}Testing Feed and Search (Public)...{Colors.RESET}")
    test_get_feed()
    test_search_posts()
    test_get_categories()
    test_get_tags()
    
    if token:
        print(f"\n{Colors.YELLOW}Testing Post System...{Colors.RESET}")
        category_id = test_create_category(token)
        tag_id = test_create_tag(token)
        post_id = test_create_post(token, category_id, tag_id)
        
        print(f"\n{Colors.YELLOW}Testing Interactions...{Colors.RESET}")
        if post_id:
            test_like_post(token, post_id)
    
    print(f"\n{Colors.YELLOW}=== Tests Complete ==={Colors.RESET}\n")
    
    if not token:
        print(f"{Colors.YELLOW}For full testing, authenticate with Google OAuth and provide token{Colors.RESET}")
        print(f"{Colors.YELLOW}See GOOGLE_OAUTH_INTEGRATION.md for details{Colors.RESET}\n")

if __name__ == '__main__':
    print(f"{Colors.YELLOW}Starting API tests...{Colors.RESET}")
    print(f"Make sure the server is running on {BASE_URL}\n")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/")
        print(f"{Colors.GREEN}Server is reachable{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}Server is not reachable at {BASE_URL}{Colors.RESET}")
        print("Please start the server with: python manage.py runserver\n")
        exit(1)
    
    run_tests()

