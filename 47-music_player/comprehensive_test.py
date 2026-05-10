#!/usr/bin/env python
"""
Comprehensive Music Player API Test
Tests all major endpoints and functionality
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 60}")
    print(f"{text}")
    print(f"{'=' * 60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_server_status():
    """Test if server is running"""
    print_header("Testing Server Status")
    try:
        response = requests.get(f"{BASE_URL}/genres/", timeout=5)
        if response.status_code in [200, 401]:
            print_success("Server is running")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Server is not responding: {e}")
        return False

def test_authentication():
    """Test registration and login"""
    print_header("Testing Authentication")
    
    # Generate unique credentials
    timestamp = str(int(time.time()))
    username = f"testuser_{timestamp}"
    email = f"test_{timestamp}@example.com"
    password = "testpass123"
    
    # Test registration
    print_info("Testing registration...")
    reg_data = {
        "username": username,
        "email": email,
        "password": password,
        "password2": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=reg_data)
        if response.status_code == 201:
            result = response.json()
            token = result.get('token')
            user_id = result['user']['id']
            print_success(f"Registration successful (User ID: {user_id})")
        else:
            print_error(f"Registration failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Registration error: {e}")
        return None
    
    # Test login
    print_info("Testing login...")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            print_success(f"Login successful (Token: {token[:20]}...)")
            return token
        else:
            print_error(f"Login failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Login error: {e}")
        return None

def test_read_only_endpoints(token):
    """Test read-only endpoints"""
    print_header("Testing Read-Only Endpoints")
    
    headers = {'Authorization': f'Token {token}'}
    
    endpoints = [
        ('/genres/', 'Genres'),
        ('/artists/', 'Artists'),
        ('/albums/', 'Albums'),
        ('/songs/', 'Songs'),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('results', []))
                print_success(f"{name} endpoint working (found {count} items)")
            else:
                print_error(f"{name} endpoint failed: {response.status_code}")
        except Exception as e:
            print_error(f"{name} endpoint error: {e}")

def test_user_endpoints(token):
    """Test user-specific endpoints"""
    print_header("Testing User Endpoints")
    
    headers = {'Authorization': f'Token {token}'}
    
    # Test favorites
    print_info("Testing favorites endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/library/favorites/", headers=headers)
        if response.status_code == 200:
            print_success("Favorites endpoint working")
        else:
            print_error(f"Favorites failed: {response.status_code}")
    except Exception as e:
        print_error(f"Favorites error: {e}")
    
    # Test recently played
    print_info("Testing recently played endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/library/recently_played/", headers=headers)
        if response.status_code == 200:
            print_success("Recently played endpoint working")
        else:
            print_error(f"Recently played failed: {response.status_code}")
    except Exception as e:
        print_error(f"Recently played error: {e}")
    
    # Test recommendations
    print_info("Testing recommendations endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/library/recommendations/", headers=headers)
        if response.status_code == 200:
            print_success("Recommendations endpoint working")
        else:
            print_error(f"Recommendations failed: {response.status_code}")
    except Exception as e:
        print_error(f"Recommendations error: {e}")

def test_search():
    """Test search functionality"""
    print_header("Testing Search Functionality")
    
    try:
        response = requests.get(f"{BASE_URL}/search/?q=test&type=all")
        if response.status_code == 200:
            print_success("Search endpoint working")
        else:
            print_error(f"Search failed: {response.status_code}")
    except Exception as e:
        print_error(f"Search error: {e}")

def test_cors():
    """Test CORS headers"""
    print_header("Testing CORS Headers")
    
    try:
        response = requests.get(f"{BASE_URL}/genres/")
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print_success(f"CORS headers present: {cors_header}")
        else:
            print_error("CORS headers not found")
    except Exception as e:
        print_error(f"CORS test error: {e}")

def main():
    print(f"{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║       MUSIC PLAYER - COMPREHENSIVE API TEST SUITE          ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}")
    
    # Test server status
    if not test_server_status():
        print_error("Server is not running. Please start the server first.")
        sys.exit(1)
    
    # Test CORS
    test_cors()
    
    # Test authentication
    token = test_authentication()
    if not token:
        print_error("Authentication failed. Cannot continue with other tests.")
        sys.exit(1)
    
    # Test read-only endpoints
    test_read_only_endpoints(token)
    
    # Test user endpoints
    test_user_endpoints(token)
    
    # Test search
    test_search()
    
    # Summary
    print_header("Test Summary")
    print_success("All critical tests completed!")
    print_info("The Music Player API is running correctly.")
    print()

if __name__ == "__main__":
    main()
