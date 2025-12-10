#!/bin/bash
# Start all Docker services for Maang-Tracker

set -e

echo "🚀 Starting Maang-Tracker Platform..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 .env created. Please update with your configuration."
    echo "🔑 Required: GOOGLE_API_KEY, GITHUB_TOKEN, OPENAI_API_KEY"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build images if needed
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo "🌀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T migrations bash -c "alembic upgrade head && python -m scripts.init_db" || true

# Show service status
echo ""
echo "📊 Service Status:"
docker-compose ps

# Show access information
echo ""
echo "✅ Maang-Tracker is starting up!"
echo ""
echo "📍 Access Points:"
echo "   Dashboard:        http://localhost:3000"
echo "   Nginx Proxy:      http://localhost:80"
echo "   PGAdmin:          http://localhost:5050"
echo "   Redis Commander: http://localhost:8081"
echo "   MCP Server:       http://localhost:8765"
echo "   Nginx:          http://localhost:80"
echo ""
echo "🔐 Credentials:"
echo "   PGAdmin Email:  admin@maang.local"
echo "   PGAdmin Pass:   admin"
echo "   Redis Password: redis-password"
echo ""
echo "📚 Commands:"
echo "   View logs:      docker-compose logs -f"
echo "   Stop services:  docker-compose down"
echo "   Restart:        docker-compose restart"
echo "   Clean data:     docker-compose down -v"
echo ""
