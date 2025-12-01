# tracker/tracker.py
"""
Polls the local MCP server tools (github, leetcode, gfg) and stores snapshots into SQLite memory.
Updated for multi-user system.
"""
import os
import requests
import time
import argparse

MCP_BASE = os.getenv("MCP_URL", "http://localhost:8765")

def call_mcp(tool: str, params: dict):
    """
    Calls the MCP HTTP wrapper endpoints.
    """
    # Try /call/{tool} endpoint first (most direct)
    url = f"{MCP_BASE}/call/{tool}"
    try:
        r = requests.post(url, json=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                return data.get('result', data)
            else:
                return {"ok": False, "error": data.get('error', 'Unknown error')}
        
        # Fallback to /invoke endpoint
        url = f"{MCP_BASE}/invoke"
        payload = {"tool": tool, "args": params}
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                return data.get('result', data)
            else:
                return {"ok": False, "error": data.get('error', 'Unknown error')}
        
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def snapshot_github(username: str, token: str = None):
    """Fetch GitHub data via MCP"""
    res = call_mcp("list_repos", {"username": username, "token": token})
    return res

def snapshot_leetcode(username: str, session: str = None):
    """Fetch LeetCode data via MCP"""
    res = call_mcp("leetcode_stats", {"username": username, "session_cookie": session})
    return res

def main_loop(args):
    """Legacy CLI interface - now just prints data"""
    if args.github:
        print("Pulling GitHub data...")
        result = snapshot_github(args.github)
        print(f"Result: {result}")
    if args.leetcode:
        print("Pulling LeetCode data...")
        result = snapshot_leetcode(args.leetcode)
        print(f"Result: {result}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--github", help="GitHub username to snapshot")
    p.add_argument("--leetcode", help="LeetCode username to snapshot")
    args = p.parse_args()
    if not args.github and not args.leetcode:
        print("Run with --github <user> or --leetcode <user>")
    else:
        main_loop(args)
