# tracker/tracker.py
"""
Polls the local MCP server tools (github, leetcode, gfg) and stores snapshots into SQLite memory.
Updated for multi-user system.
"""
import os
import requests
import time
import argparse

MCP_BASE = os.getenv("MCP_URL", "http://localhost:8765/mcp")  # adjust if different

def call_mcp(tool: str, params: dict):
    """
    Calls the FastMCP HTTP tool endpoint.
    FastMCP exposes POST /mcp/invoke with JSON: { "tool":"name", "args": {...} } or similar.
    """
    url = f"{MCP_BASE}/invoke"  # many FastMCP versions expose /invoke; fallback handled later
    payload = {"tool": tool, "args": params}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 404:
            # fallback: some FastMCP versions expose /rpc or direct JSON; try /call/<tool>
            alt = f"{MCP_BASE}/call/{tool}"
            r = requests.post(alt, json=params, timeout=10)
        r.raise_for_status()
        return r.json()
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
