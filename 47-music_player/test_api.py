import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Test registration
def test_register():
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "testpass123",
        "password2": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test login
def test_login():
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": "testuser123",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Registration...")
    test_register()
    print("\nTesting Login...")
    test_login()