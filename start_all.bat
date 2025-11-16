@echo off
REM Start all MAANG Mentor services
setlocal enabledelayedexpansion

cd /d C:\Users\anlsk\AI_Agent

echo ========================================
echo MAANG Mentor - Starting All Services
echo ========================================
echo.
echo Starting MCP Server on port 8765...
start "MCP Server (port 8765)" python -u .\mcp_server\server.py

timeout /t 3 /nobreak

echo Starting ADK Web UI on port 8000...
start "ADK Web (port 8000)" adk web --port 8000

timeout /t 3 /nobreak

echo Starting Dashboard on port 5100...
start "Dashboard (port 5100)" python ui/dashboard.py

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Access the services at:
echo   - ADK Web UI:    http://127.0.0.1:8000
echo   - Dashboard:     http://127.0.0.1:5100
echo   - MCP Server:    http://127.0.0.1:8765/mcp
echo.
echo Check the individual terminal windows for logs and errors.
echo Close any window to stop that service.
echo.
pause
