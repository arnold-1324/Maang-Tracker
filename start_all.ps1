$ErrorActionPreference = "Stop"

Write-Host "Starting MAANG Tracker Ecosystem..." -ForegroundColor Cyan

# ---- REAL Git Bash path ----
$GitBash = "C:\Users\80133\scoop\apps\git\2.48.1\git-bash.exe"

if (!(Test-Path $GitBash)) {
    throw "Git Bash not found at: $GitBash"
}

# ---- Function ----
function Start-Service {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Args,
        [Parameter(Mandatory = $true)][string]$Dir
    )

    Write-Host "Starting $Name..." -ForegroundColor Yellow

    if ($Args -eq $null -or $Args.Count -eq 0) {
        throw "Missing argument list for: $Name"
    }

    if (!(Test-Path $Dir)) {
        throw "Directory not found: $Dir"
    }

    Start-Process -FilePath $Command -ArgumentList $Args -WorkingDirectory $Dir
}

$Root = $PSScriptRoot

# ---- SERVICES ----

# 1. MCP Server (Python)
Start-Service `
    -Name "MCP Server" `
    -Command "py" `
    -Args @("mcp_server/http_wrapper.py") `
    -Dir $Root

# 2. Backend Dashboard (Python)
Start-Service `
    -Name "Backend Dashboard" `
    -Command "py" `
    -Args @("ui/dashboard.py") `
    -Dir $Root

# 3. Frontend (Next.js) — Git Bash
Start-Service `
    -Name "Frontend (Next.js)" `
    -Command $GitBash `
    -Args @("--login", "-c", "npm run dev") `
    -Dir "$Root\dashboard"

Write-Host "`nAll services launched!" -ForegroundColor Green
Write-Host "----------------------------------------------"
Write-Host "Frontend:   http://localhost:3000"
Write-Host "Backend:    Running"
Write-Host "MCP:        http://localhost:8765"
Write-Host "----------------------------------------------"
Read-Host "Press Enter to exit"
