# Start all Docker services for Maang-Tracker
# For Windows PowerShell users

Write-Host "🚀 Starting Maang-Tracker Platform..." -ForegroundColor Green

# Get the project root directory (parent of docker directory)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = Join-Path $ProjectRoot ".env.example"

# Change to project root
Set-Location $ProjectRoot

# Check if .env file exists
if (-not (Test-Path $EnvFile)) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path $EnvExample) {
        Copy-Item -Path $EnvExample -Destination $EnvFile
        Write-Host "📝 .env created. Please update with your configuration." -ForegroundColor Cyan
        Write-Host "🔑 Required: GOOGLE_API_KEY, GITHUB_TOKEN, OPENAI_API_KEY" -ForegroundColor Yellow
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

# Check if Docker is running
Write-Host "🐳 Checking Docker..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } else {
        throw "Docker not available"
    }
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Build images if needed
Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "🌀 Starting services..." -ForegroundColor Cyan
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to start (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Cyan
docker-compose exec -T migrations bash -c "alembic upgrade head && python -m scripts.init_db" 2>&1 | Out-Null

# Show service status
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Green
docker-compose ps

# Show access information
Write-Host ""
Write-Host "✅ Maang-Tracker is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access Points:" -ForegroundColor Cyan
Write-Host "   Dashboard:        http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Nginx Proxy:      http://localhost:80" -ForegroundColor Yellow
Write-Host "   PGAdmin:          http://localhost:5050" -ForegroundColor Yellow
Write-Host "   Redis Commander: http://localhost:8081" -ForegroundColor Yellow
Write-Host "   MCP Server:       http://localhost:8765" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔍 To view logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f" -ForegroundColor Gray
Write-Host ""
Write-Host "✋ To stop services:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor Gray
