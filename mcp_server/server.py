import os
import sys
import json
import base64
import sqlite3
import shutil
import logging
import requests
from bs4 import BeautifulSoup
from github import Github
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Try to import Windows crypto libraries
try:
    import win32crypt
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

mcp = FastMCP("maang-mcp")

with open("mcp_debug.txt", "w") as f:
    f.write(str(dir(mcp)))

def get_chrome_cookie(domain, name):
    """Extract cookie from Chrome on Windows"""
    if not HAS_CRYPTO:
        return None
        
    try:
        # Get the encryption key from Local State
        local_state_path = os.path.join(os.environ["LOCALAPPDATA"],
                                        r"Google\Chrome\User Data\Local State")
        if not os.path.exists(local_state_path):
            return None
            
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())

        # Decode the encryption key
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        # Remove DPAPI prefix
        encrypted_key = encrypted_key[5:] 
        # Decrypt the key
        secret_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        # Find Cookies database
        paths = [
            os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Default\Network\Cookies"),
            os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Default\Cookies"),
            os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data\Profile 1\Network\Cookies")
        ]
        
        cookies_path = None
        for p in paths:
            if os.path.exists(p):
                cookies_path = p
                break
        
        if not cookies_path:
            return None
        
        # Copy to temp to avoid lock
        temp_cookies = f"Cookies.temp.{os.getpid()}"
        shutil.copy2(cookies_path, temp_cookies)

        try:
            conn = sqlite3.connect(temp_cookies)
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT encrypted_value FROM cookies WHERE host_key LIKE '%{domain}%' AND name='{name}'")
            row = cursor.fetchone()
            conn.close()
            
            if row:
                encrypted_value = row[0]
                if not encrypted_value:
                    return None
                    
                # Decrypt (v10 cookies start with v10)
                if encrypted_value.startswith(b'v10'):
                    nonce = encrypted_value[3:15]
                    ciphertext = encrypted_value[15:]
                    aesgcm = AESGCM(secret_key)
                    decrypted_value = aesgcm.decrypt(nonce, ciphertext, None)
                    return decrypted_value.decode('utf-8')
                else:
                    # Legacy DPAPI
                    return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8')
        finally:
            if os.path.exists(temp_cookies):
                os.remove(temp_cookies)
                
    except Exception as e:
        logger.error(f"Failed to extract Chrome cookie: {e}")
        return None
    return None

# ----------------------------------------------------------
#  LeetCode Authentication
# ----------------------------------------------------------
@mcp.tool()
def leetcode_login(username: str, password: str):
    """Authenticate with LeetCode and return session cookie"""
    # 1. Fallback: If password looks like a session cookie (long string), use it directly
    if len(password) > 60:
        return {"ok": True, "session": password}
        
    # 2. Try automatic browser cookie extraction if password is 'auto' or empty
    if not password or password.lower() == 'auto':
        session_cookie = get_chrome_cookie('leetcode.com', 'LEETCODE_SESSION')
        if session_cookie:
            return {"ok": True, "session": session_cookie}
        if not password:
            return {"ok": False, "error": "Could not find LeetCode session in Chrome. Please provide password or session cookie."}

    login_url = "https://leetcode.com/accounts/login/"
    
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Origin': 'https://leetcode.com',
        'Referer': 'https://leetcode.com/accounts/login/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        # Get CSRF token with headers
        response = session.get(login_url, headers=headers)
        csrf_token = session.cookies.get('csrftoken')
        
        if not csrf_token:
            # Try to extract from hidden input if cookie missing
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
        
        if not csrf_token:
            return {"ok": False, "error": "Failed to get CSRF token. Please try manual cookie method."}
        
        # Login
        login_data = {
            'login': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token
        }
        
        # Update headers for POST
        headers.update({
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'
        })
        
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
  logger.info("Starting MCP server...")
  try:
    logger.info("Inspecting `mcp` methods for best run strategy...")
    attrs = dir(mcp)
    logger.info("mcp attributes: %s", ", ".join([a for a in attrs if not a.startswith("__")]))

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
