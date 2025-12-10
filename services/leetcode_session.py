"""
LeetCode Session Manager
Allows users to manually enter their LeetCode session credentials
"""
import os
import json
from pathlib import Path

class LeetCodeSessionManager:
    def __init__(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.session_file = self.config_dir / "leetcode_session.json"
    
    def save_session(self, username, session_id):
        """Save LeetCode session credentials"""
        session_data = {
            "username": username,
            "session_id": session_id,
            "saved_at": str(Path.ctime(Path.cwd()))
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return True
    
    def get_session(self):
        """Retrieve saved LeetCode session"""
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading session: {e}")
            return None
    
    def clear_session(self):
        """Clear saved session"""
        if self.session_file.exists():
            self.session_file.unlink()
        return True
    
    def is_session_valid(self):
        """Check if session exists"""
        session = self.get_session()
        return session is not None and 'session_id' in session and session['session_id']


def get_leetcode_headers(session_id):
    """Generate headers for LeetCode API requests"""
    return {
        'Cookie': f'LEETCODE_SESSION={session_id}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://leetcode.com/',
        'Origin': 'https://leetcode.com'
    }


def fetch_leetcode_stats(username, session_id):
    """
    Fetch LeetCode statistics using session credentials
    No SOCKS proxy needed - direct API calls
    """
    import requests
    
    # GraphQL query for user stats
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
            profile {
                ranking
                reputation
            }
        }
        recentSubmissionList(username: $username, limit: 10) {
            title
            titleSlug
            timestamp
            statusDisplay
            lang
        }
    }
    """
    
    url = "https://leetcode.com/graphql"
    headers = get_leetcode_headers(session_id)
    
    payload = {
        "query": query,
        "variables": {"username": username}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            return {"success": False, "error": "Invalid session or username"}
        
        # Parse stats
        user_data = data.get('data', {}).get('matchedUser', {})
        submissions = data.get('data', {}).get('recentSubmissionList', [])
        
        stats = {
            "username": user_data.get('username', username),
            "ranking": user_data.get('profile', {}).get('ranking', 0),
            "reputation": user_data.get('profile', {}).get('reputation', 0),
            "problems_solved": {},
            "recent_submissions": []
        }
        
        # Parse problem counts
        for item in user_data.get('submitStats', {}).get('acSubmissionNum', []):
            difficulty = item.get('difficulty', 'All').lower()
            count = item.get('count', 0)
            stats['problems_solved'][difficulty] = count
        
        # Parse recent submissions
        for sub in submissions[:5]:  # Last 5
            stats['recent_submissions'].append({
                "title": sub.get('title'),
                "status": sub.get('statusDisplay'),
                "language": sub.get('lang'),
                "timestamp": sub.get('timestamp')
            })
        
        return {"success": True, "data": stats}
        
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}
