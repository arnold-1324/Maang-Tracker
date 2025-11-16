# Starting the MAANG Mentor System

This guide explains how to start all three services that make up the MAANG Mentor system.

## Prerequisites

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   pip install flask uvicorn
   ```

2. **Environment variables** (add to `.env`):
   ```
   GITHUB_TOKEN=<your_github_token>
   GOOGLE_API_KEY=<your_google_api_key>
   LEETCODE_USERNAME=<your_leetcode_username>
   ```

## Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| **MCP Server** | 8765 | Exposes tools (GitHub, LeetCode, GeeksforGeeks) via HTTP/SSE |
| **ADK Web UI** | 8000 | Agent builder and runner (connects to MCP on 8765) |
| **Dashboard** | 5100 | Web dashboard for viewing weaknesses and roadmap |

## Running Services

### Option 1: Run each in a separate terminal (Recommended)

**Terminal 1 - MCP Server:**
```powershell
cd C:\Users\anlsk\AI_Agent
python -u .\mcp_server\server.py
```
Watch for: `Starting uvicorn with mcp.streamable_http_app on 0.0.0.0:8765`

**Terminal 2 - ADK Web Server:**
```powershell
cd C:\Users\anlsk\AI_Agent
adk web --port 8000
```
Then open: http://127.0.0.1:8000

**Terminal 3 - Dashboard:**
```powershell
cd C:\Users\anlsk\AI_Agent
python ui/dashboard.py
```
Then open: http://127.0.0.1:5100

### Option 2: Use the startup script (Windows batch)

Create `start_all.bat` in `C:\Users\anlsk\AI_Agent\`:
```batch
@echo off
cd C:\Users\anlsk\AI_Agent

REM Start MCP Server in new window
start "MCP Server" python -u .\mcp_server\server.py

REM Start ADK Web Server in new window
timeout /t 2
start "ADK Web" adk web --port 8000

REM Start Dashboard in new window
timeout /t 2
start "Dashboard" python ui/dashboard.py

echo All services started. Check individual windows for logs.
pause
```

Then run: `start_all.bat`

## Verification Checklist

- [ ] MCP Server log shows: "Starting uvicorn with mcp.streamable_http_app on 0.0.0.0:8765"
- [ ] Port 8765 is listening: `Test-NetConnection -ComputerName localhost -Port 8765` → `TcpTestSucceeded: True`
- [ ] ADK Web starts without "No root_agent found" error
- [ ] ADK Web loads at http://127.0.0.1:8000 and shows maang_agent app
- [ ] Dashboard starts without ModuleNotFoundError and loads at http://127.0.0.1:5100

## Troubleshooting

**MCP Server won't start on port 8765**
- Check if port is in use: `netstat -ano | Select-String 8765`
- Set custom port: `$env:MCP_PORT=9000` then run server
- Agent must connect to the new port in `maang_agent/agent.py`

**ADK reports "No root_agent found"**
- Ensure `maang_agent/agent.py` exports a `root_agent` (function or instance of BaseAgent)
- Current setup: async `root_agent()` function + module-level `root_agent` instance

**Dashboard import errors**
- All `__init__.py` files must exist in: memory/, ui/, tracker/, roadmap/, analyzer/
- `dashboard.py` adds parent dir to sys.path automatically

**Port conflicts**
- MCP: `$env:MCP_PORT=9000` (update agent connection URL)
- ADK: `adk web --port 9001`
- Dashboard: Edit `dashboard.py` line ~95 → `app.run(port=5200, debug=True)`

## Next Steps

1. Start all three services following Option 1 or 2 above
2. Test agent runs in ADK Web UI (http://127.0.0.1:8000)
3. Monitor MCP server logs for tool calls (GitHub, LeetCode, GFG)
4. Use Dashboard to view collected weakness profile
