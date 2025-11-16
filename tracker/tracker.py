# tracker/tracker.py
"""
Polls the local MCP server tools (github, leetcode, gfg) and stores snapshots into SQLite memory.
Run this periodically (cron or manually) to update memory.
"""
import os
import requests
import time
import argparse
from memory.db import init_db, insert_snapshot, upsert_weakness

MCP_BASE = os.getenv("MCP_URL", "http://localhost:8765/mcp")  # adjust if different

def call_mcp(tool: str, params: dict):
    """
    Calls the FastMCP HTTP tool endpoint.
    FastMCP exposes POST /mcp/invoke with JSON: { "tool":"name", "args": {...} } or similar.
    We'll use the ADK MCP client style endpoint; if your FastMCP has different API, adapt this small function.
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

def snapshot_github(username: str):
    res = call_mcp("list_repos", {"username": username})
    insert_snapshot("github", username, res)
    # simple weakness heuristic: if repo count < 5 then small project exposure
    if res.get("ok"):
        repos = res.get("repos", [])
        if len(repos) < 5:
            upsert_weakness("OSS/ProjectExposure", 10)
    return res

def snapshot_leetcode(username: str):
    res = call_mcp("leetcode_stats", {"username": username})
    insert_snapshot("leetcode", username, res)
    # weakness heuristics: low counts in medium/hard => mark problems
    try:
        stats = res.get("data", {}).get("matchedUser", {}).get("submitStats", {}).get("acSubmissionNum", [])
        counts = {entry["difficulty"]: entry["count"] for entry in stats} if stats else {}
        easy = counts.get("Easy", 0)
        med = counts.get("Medium", 0)
        hard = counts.get("Hard", 0)
        if med < 20:
            upsert_weakness("Dynamic Programming / Medium Problems", 8)
        if hard < 5:
            upsert_weakness("Hard Problems", 9)
    except Exception:
        pass
    return res

def main_loop(args):
    init_db()
    if args.github:
        print("Pulling GitHub data...")
        snapshot_github(args.github)
        print("GitHub snapshot saved.")
    if args.leetcode:
        print("Pulling LeetCode data...")
        snapshot_leetcode(args.leetcode)
        print("LeetCode snapshot saved.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--github", help="GitHub username to snapshot")
    p.add_argument("--leetcode", help="LeetCode username to snapshot")
    args = p.parse_args()
    if not args.github and not args.leetcode:
        print("Run with --github <user> or --leetcode <user>")
    else:
        main_loop(args)
