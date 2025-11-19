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
#  GitHub Tool
# ----------------------------------------------------------
@mcp.tool()
def list_repos(username: str):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"ok": False, "error": "Missing GITHUB_TOKEN in environment"}

    gh = Github(token)
    user = gh.get_user(username)

    repos = [{
        "name": r.name,
        "url": r.html_url,
        "stars": r.stargazers_count,
        "description": r.description
    } for r in user.get_repos()]

    return {"ok": True, "repos": repos}

# ----------------------------------------------------------
#  LeetCode Tool
# ----------------------------------------------------------
@mcp.tool()
def leetcode_stats(username: str):
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
    }
    """
    url = "https://leetcode.com/graphql"
    resp = requests.post(url,
        json={"query": query, "variables": {"username": username}},
        headers={"User-Agent": "maang-agent"}
    )
    return resp.json()

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
