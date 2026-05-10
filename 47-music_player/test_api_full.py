import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

# Test with unique credentials
timestamp = str(int(time.time()))
user_data = {
    "username": f"testuser_{timestamp}",
    "email": f"test_{timestamp}@example.com",
    "password": "testpass123",
    "password2": "testpass123"
}

print("=" * 50)
print("Testing Registration...")
print("=" * 50)
try:
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 201:
        token = result.get('token')
        print("\n✓ Registration successful!")
        
        print("\n" + "=" * 50)
        print("Testing Login...")
        print("=" * 50)
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Status: {login_response.status_code}")
        login_result = login_response.json()
        print(f"Response: {json.dumps(login_result, indent=2)}")
        
        if login_response.status_code == 200:
            print("\n✓ Login successful!")
            token = login_result.get('token')
            
            print("\n" + "=" * 50)
            print("Testing API Endpoints...")
            print("=" * 50)
            
            headers = {'Authorization': f'Token {token}'}
            
            # Test getting genres
            print("\nFetching Genres...")
            genres_response = requests.get(f"{BASE_URL}/genres/", headers=headers)
            print(f"Status: {genres_response.status_code}")
            if genres_response.status_code == 200:
                print("✓ Genres endpoint working!")
            
            # Test getting songs
            print("\nFetching Songs...")
            songs_response = requests.get(f"{BASE_URL}/songs/", headers=headers)
            print(f"Status: {songs_response.status_code}")
            if songs_response.status_code == 200:
                print("✓ Songs endpoint working!")
            
            # Test getting artists
            print("\nFetching Artists...")
            artists_response = requests.get(f"{BASE_URL}/artists/", headers=headers)
            print(f"Status: {artists_response.status_code}")
            if artists_response.status_code == 200:
                print("✓ Artists endpoint working!")
        else:
            print("\n✗ Login failed!")
    else:
        print("\n✗ Registration failed!")
except Exception as e:
    print(f"Error: {e}")
