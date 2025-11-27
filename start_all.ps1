$ErrorActionPreference = "Stop"

Write-Host "Starting MAANG Tracker Ecosystem..." -ForegroundColor Cyan

# Function to start a process
function Start-Service {
    param($Name, $Command, $Args, $Dir)
    Write-Host "Starting $Name..." -ForegroundColor Yellow
    Start-Process $Command -ArgumentList $Args -WorkingDirectory $Dir
}

$Root = $PSScriptRoot

# 1. Start MCP Server
Start-Service "MCP Server" "python" "mcp_server/server.py" $Root

# 2. Start Backend Dashboard
Start-Service "Backend Dashboard" "python" "ui/dashboard.py" $Root

# 3. Start Frontend (Next.js)
# Ensure we bind to 0.0.0.0 for LAN access (already in package.json)
Start-Service "Frontend" "cmd" "/k npm run dev" "$Root\dashboard"

# 4. Start P2P Tunnel Host (for external access)
if (Test-Path "$Root\p2p-tunnel") {
    Start-Service "P2P Tunnel Host" "cmd" "/k npm run host" "$Root\p2p-tunnel"
} else {
    Write-Host "P2P Tunnel not found, skipping." -ForegroundColor Red
}

Write-Host "`nAll services launching..." -ForegroundColor Green
Write-Host "------------------------------------------------"
Write-Host "Local Access:     http://localhost:3000"
Write-Host "LAN Access:       http://<YOUR_IP>:3000"
Write-Host "P2P Tunnel:       Active (Check tunnel window)"
Write-Host "------------------------------------------------"
Write-Host "Press Enter to exit this launcher (services will keep running)."
Read-Host
