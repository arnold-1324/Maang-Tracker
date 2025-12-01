import requests
import json

def test_leetcode_login():
    url = "http://localhost:8765/call/leetcode_login"
    # Try with auto login (cookie extraction)
    payload = {
        "username": "arnold-1324", 
        "password": "auto"
    }
    try:
        print(f"Testing {url} with payload: {payload}")
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        try:
            data = response.json()
            if 'result' in data:
                print(f"Result: {json.dumps(data['result'], indent=2)}")
        except:
            pass
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_leetcode_login()
