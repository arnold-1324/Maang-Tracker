import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

import requests
from bs4 import BeautifulSoup
from github import Github
import logging
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("maang-mcp")

# ----------------------------------------------------------
#  LeetCode Authentication
# ----------------------------------------------------------
@mcp.tool()
def leetcode_login(username: str, password: str):
    """Authenticate with LeetCode and return session cookie"""
    login_url = "https://leetcode.com/accounts/login/"
    graphql_url = "https://leetcode.com/graphql"
    
    session = requests.Session()
    
    try:
        # Get CSRF token
        response = session.get(login_url)
        csrf_token = session.cookies.get('csrftoken')
        
        if not csrf_token:
            return {"ok": False, "error": "Failed to get CSRF token"}
        
        # Login
        login_data = {
            'login': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token
        }
        
        headers = {
            'Referer': login_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = session.post(login_url, data=login_data, headers=headers)
        
        # Get session cookie
        leetcode_session = session.cookies.get('LEETCODE_SESSION')
        
        if leetcode_session:
            return {"ok": True, "session": leetcode_session}
        else:
            return {"ok": False, "error": "Login failed. Please check your credentials."}
            
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ----------------------------------------------------------
#  GitHub Tool
# ----------------------------------------------------------
@mcp.tool()
def list_repos(username: str, token: str = None):
    # Use provided token, fallback to env, then fail if neither
    api_token = token or os.getenv("GITHUB_TOKEN")
    if not api_token:
        return {"ok": False, "error": "Missing GITHUB_TOKEN. Please provide it in settings."}

    gh = Github(api_token)
    try:
        user = gh.get_user(username)
        repos = [{
            "name": r.name,
            "url": r.html_url,
            "stars": r.stargazers_count,
            "description": r.description,
            "language": r.language
        } for r in user.get_repos()]
        return {"ok": True, "repos": repos}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ----------------------------------------------------------
#  LeetCode Tool
# ----------------------------------------------------------
@mcp.tool()
def leetcode_stats(username: str, session_cookie: str = None):
    query = """
    query getUser($username: String!) {
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
      recentAcSubmissionList(username: $username, limit: 100) {
        title
        titleSlug
        timestamp
      }
    }
    """
    url = "https://leetcode.com/graphql"
    headers = {
        "User-Agent": "maang-agent", 
        "Content-Type": "application/json"
    }
    if session_cookie:
        headers["Cookie"] = f"LEETCODE_SESSION={session_cookie}"

    try:
        resp = requests.post(url,
            json={"query": query, "variables": {"username": username}},
            headers=headers
        )
        return resp.json()
    except Exception as e:
        return {"errors": [str(e)]}

@mcp.tool()
def leetcode_problems(tag: str, limit: int = 20):
    query = """
    query getTopicTag($slug: String!, $limit: Int) {
      topicTag(name: $slug) {
        name
        questions(limit: $limit) {
          questionId
          questionFrontendId
          title
          titleSlug
          difficulty
          topicTags {
            name
            slug
          }
        }
      }
    }
    """
    url = "https://leetcode.com/graphql"
    try:
        resp = requests.post(url,
            json={"query": query, "variables": {"slug": tag, "limit": limit}},
            headers={"User-Agent": "maang-agent", "Content-Type": "application/json"}
        )
        return resp.json()
    except Exception as e:
        return {"errors": [str(e)]}

@mcp.tool()
def leetcode_all_solved(username: str):
    """Get all solved problems for a LeetCode user"""
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
        }
      }
      recentAcSubmissionList(username: $username, limit: 5000) {
        title
        titleSlug
        timestamp
      }
    }
    """
    url = "https://leetcode.com/graphql"
    try:
        resp = requests.post(url,
            json={"query": query, "variables": {"username": username}},
            headers={"User-Agent": "maang-agent", "Content-Type": "application/json"}
        )
        return resp.json()
    except Exception as e:
        return {"errors": [str(e)]}

# ----------------------------------------------------------
#  GeeksForGeeks Search
# ----------------------------------------------------------
@mcp.tool()
def gfg_search(q: str):
    url = f"https://www.geeksforgeeks.org/?s={q}"
    resp = requests.get(url, headers={"User-Agent": "maang-agent"})
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    for a in soup.find_all("a", href=True)[:5]:
        title = a.text.strip()
        href = a["href"]
        if title:
            results.append({"title": title, "url": href})

    return {"ok": True, "results": results}

# ----------------------------------------------------------
#  RUN MCP SERVER
# ----------------------------------------------------------
if __name__ == "__main__":
  # Configure basic logging so exceptions are visible
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger("mcp_server")

  logger.info("Starting MCP server...")
  # FastMCP can expose different runtimes (stdio or HTTP). Prefer an
  # explicit HTTP run method if available so we guarantee the server
  # listens on the expected port (8765). If not, fall back to `run()`
  # and log the available attributes to aid debugging.
  try:
    logger.info("Inspecting `mcp` methods for best run strategy...")
    attrs = dir(mcp)
    logger.info("mcp attributes: %s", ", ".join([a for a in attrs if not a.startswith("__")]))

    # If FastMCP exposes an ASGI app, prefer serving it with uvicorn so
    # the server reliably binds to the expected port and path. Only
    # fall back to `mcp.run()` (which may use a stdio transport) if an
    # ASGI app or uvicorn isn't available.
    port = int(os.getenv("MCP_PORT", "8765"))
    started = False
    try:
      if hasattr(mcp, "streamable_http_app") or hasattr(mcp, "sse_app"):
        try:
          import uvicorn
          if hasattr(mcp, "streamable_http_app"):
            logger.info("Starting uvicorn with `mcp.streamable_http_app` on 0.0.0.0:%s", port)
            uvicorn.run(mcp.streamable_http_app, host="0.0.0.0", port=port)
          else:
            logger.info("Starting uvicorn with `mcp.sse_app` on 0.0.0.0:%s", port)
            uvicorn.run(mcp.sse_app, host="0.0.0.0", port=port)
          started = True
        except ImportError:
          logger.warning("uvicorn not installed - cannot serve ASGI app. Will attempt other run methods.")

      if not started:
        # Try various run methods exposed by FastMCP (HTTP-first candidates
        # omitted because we attempted ASGI above). Keep `run` only as a
        # last resort; note that `run()` may use stdio and will read JSON
        # RPC messages from stdin — do not type or paste other commands
        # into the same terminal while `mcp.run()` is active.
        candidates = ["run_http", "serve_http", "start_http_server", "run_server", "serve", "run"]
        tried = []
        for name in candidates:
          if hasattr(mcp, name):
            fn = getattr(mcp, name)
            tried.append(name)
            logger.info("Attempting to start MCP using `%s`...", name)
            try:
              try:
                fn(host="0.0.0.0", port=port)
              except TypeError:
                fn()
              started = True
              logger.info("MCP started via `%s`", name)
              break
            except KeyboardInterrupt:
              logger.info("MCP server interrupted by user (KeyboardInterrupt). Exiting.")
              started = True
              break
            except Exception:
              logger.exception("Starting MCP via %s failed", name)

        if not started:
          logger.error("Could not find or start an HTTP run method on `mcp`. Tried: %s", tried)
          logger.info("Falling back to `mcp.run()` (may use stdio transport).")
          try:
            logger.warning("`mcp.run()` may use stdio transport. Run this script in a dedicated terminal and avoid typing other commands into the same terminal while it's running. Otherwise you'll see JSON parsing errors (Invalid JSON).")
            mcp.run()
          except KeyboardInterrupt:
            logger.info("MCP server interrupted by user (KeyboardInterrupt). Exiting.")
          except Exception:
            logger.exception("MCP server stopped with exception")

    except Exception:
      logger.exception("Unexpected error while attempting to start MCP server")

  finally:
    logger.info("MCP server stopped.")
