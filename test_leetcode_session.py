import requests
import json

def test_leetcode_with_session():
    """Test LeetCode stats API with the provided session cookie"""
    url = "http://localhost:8765/call/leetcode_stats"
    
    session_cookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfcGFzc3dvcmRfcmVzZXRfa2V5IjoiY3p5a2h6LTRlMTg3Nzk0NWMxNzY5YWYxNmNiOWRhZmYwODJkNDZhIiwiX2F1dGhfdXNlcl9pZCI6IjExNTgyNDM4IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYWxsYXV0aC5hY2NvdW50LmF1dGhfYmFja2VuZHMuQXV0aGVudGljYXRpb25CYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZWIyNmM3MWIxYTRjM2IxZTExM2QwOWNhZTM2NzAzOTU0Y2UwNTU0MjMzZjRiNzU1ZmUyMjA4N2RlMWY5ZTQ1MSIsInNlc3Npb25fdXVpZCI6IjMwYWJkOGFiIiwiaWQiOjExNTgyNDM4LCJlbWFpbCI6ImFybm9sZGduYTc2NUBnbWFpbC5jb20iLCJ1c2VybmFtZSI6ImFybm9sZC0xMzI0IiwidXNlcl9zbHVnIjoiYXJub2xkLTEzMjQiLCJhdmF0YXIiOiJodHRwczovL2Fzc2V0cy5sZWV0Y29kZS5jb20vdXNlcnMvYXZhdGFycy9hdmF0YXJfMTcwMTMxNDQyMy5wbmciLCJyZWZyZXNoZWRfYXQiOjE3NjQzMzMxODIsImlwIjoiMTI1LjIxLjEyNi4xNTgiLCJpZGVudGl0eSI6IjNjOWZjN2RkZWM5YjU4ODIzYzFjOTY3NTZkYmQ0NWQ4IiwiZGV2aWNlX3dpdGhfaXAiOlsiOWJmNDE4MDFiMDRkZWQ5ZGU0M2ViYzczYzcxZDlmYWQiLCIxMjUuMjEuMTI2LjE1OCJdfQ.EnyA6MWuT0cfdSyzzUCO58LWRsyV2o0xGXei__CULPY"
    
    payload = {
        "username": "arnold-1324",
        "session_cookie": session_cookie
    }
    
    try:
        print(f"Testing LeetCode stats with session cookie...")
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print(f"\nFull Response:")
        print(json.dumps(data, indent=2))
        
        if data.get('success') and 'result' in data:
            result = data['result']
            if 'data' in result:
                lc_data = result['data']
                if 'matchedUser' in lc_data:
                    stats = lc_data['matchedUser']['submitStats']['acSubmissionNum']
                    print(f"\n✅ SUCCESS! Your LeetCode Stats:")
                    for stat in stats:
                        print(f"  {stat['difficulty']}: {stat['count']} problems")
                else:
                    print("\n⚠️ Unexpected data structure")
            else:
                print(f"\n❌ Error in result: {result}")
        else:
            print(f"\n❌ Request failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_leetcode_with_session()
