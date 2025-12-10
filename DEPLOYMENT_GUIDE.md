# Maang-Tracker Production Deployment Guide

## Overview

This guide covers deploying Maang-Tracker with PostgreSQL, Redis, RAG memory system, and Docker containers to production.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)               │
│              Port 80/443 - Load Balancing               │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
    ┌────────▼─────────┐       ┌────────▼─────────┐
    │   Dashboard      │       │   MCP Server     │
    │  (Flask/5000)    │       │   (FastMCP/8765) │
    └────────┬─────────┘       └────────┬─────────┘
             │                          │
             └─────────┬────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼────┐      ┌──────▼────┐      ┌─────▼──┐
│ PostgreSQL (RAG+Vectors) │      │ Redis │
│ Port 5432   │      │ Port 6379 │
└──────────┘      └───────────┘      └───────┘
```

## Prerequisites

- Docker and Docker Compose 3.9+
- 8GB+ RAM available
- 20GB+ disk space
- Linux, macOS, or Windows (with Docker Desktop)

## 1. Setup Configuration

### Copy and Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your specific configuration:

```env
# Environment
ENVIRONMENT=production
DEBUG=False

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=maang_tracker
DB_USER=postgres
DB_PASSWORD=<secure-password>

# Redis
REDIS_PASSWORD=<secure-password>

# API Keys
GOOGLE_API_KEY=<your-key>
GITHUB_TOKEN=<your-token>
OPENAI_API_KEY=<your-key>

# Security
SECRET_KEY=<generate-secure-key>

# RAG Settings
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.3
```

### Generate Secure Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate DB Password
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

## 2. Build Docker Images

```bash
# Build all images
docker-compose build

# Or build specific service
docker-compose build dashboard
docker-compose build mcp-server
```

## 3. Start Services

### Development Environment

```bash
docker-compose up -d
```

### Production Environment

```bash
# Set production environment
export ENVIRONMENT=production

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 4. Initialize Database

The migrations service runs automatically on startup. To manually run:

```bash
# Run migrations
docker-compose exec postgres psql -U postgres -d maang_tracker -c \
  "CREATE EXTENSION IF NOT EXISTS vector;"

# Initialize database
docker-compose exec app python -m scripts.init_db
```

## 5. Verify Services

### Check Service Status

```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS
maang-postgres          Up (healthy)
maang-redis             Up (healthy)
maang-pgadmin           Up
maang-redis-commander   Up
maang-mcp-server        Up
maang-dashboard         Up
maang-nginx             Up
```

### Test Connectivity

```bash
# Test Dashboard
curl http://localhost/health

# Test MCP Server
curl http://localhost:8765/health

# Test PostgreSQL
docker-compose exec postgres psql -U postgres -d maang_tracker -c "SELECT 1"

# Test Redis
docker-compose exec redis redis-cli ping
```

## 6. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Dashboard | http://localhost | - |
| PGAdmin | http://localhost:5050 | admin@maang.local / admin |
| Redis Commander | http://localhost:8081 | - |
| MCP Server | http://localhost:8765 | - |

## 7. SSL/TLS Configuration

### Generate Self-Signed Certificate (Development)

```bash
cd docker/ssl

openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/CN=localhost"

cd ../..
```

### Let's Encrypt Certificate (Production)

```bash
# Using Certbot
docker run -it --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d your-domain.com

# Copy certificates to docker/ssl/
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/key.pem
```

Update `docker/nginx.conf` to enable SSL.

## 8. Database Backups

### Create Backup

```bash
docker-compose exec postgres pg_dump -U postgres maang_tracker > backup.sql
```

### Restore from Backup

```bash
docker-compose exec -T postgres psql -U postgres maang_tracker < backup.sql
```

### Automated Backups (via Cron)

```bash
# Add to crontab
0 2 * * * cd /path/to/maang-tracker && docker-compose exec -T postgres pg_dump -U postgres maang_tracker > backups/backup-$(date +\%Y\%m\%d-\%H\%M\%S).sql
```

## 9. Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dashboard
docker-compose logs -f postgres
```

### Check Resource Usage

```bash
docker stats
```

### Database Monitoring

Access pgAdmin at http://localhost:5050

### Cache Monitoring

Access Redis Commander at http://localhost:8081

## 10. Performance Tuning

### PostgreSQL Configuration

Edit environment or modify PostgreSQL config:

```sql
-- Increase shared buffers
ALTER SYSTEM SET shared_buffers = '2GB';

-- Increase work memory
ALTER SYSTEM SET work_mem = '256MB';

-- Enable parallel queries
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;

-- Select reload config
SELECT pg_reload_conf();
```

### Redis Configuration

```bash
docker-compose exec redis redis-cli CONFIG GET maxmemory
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 11. Scaling

### Horizontal Scaling (Multiple Instances)

```bash
# Scale dashboard service to 3 instances
docker-compose up -d --scale dashboard=3
```

### Load Balancing Configuration

Nginx automatically load balances across multiple instances.

## 12. Health Checks

### Application Health Endpoint

```bash
curl -X GET http://localhost/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "services": {
    "mcp_server": "up",
    "agent": "ready"
  }
}
```

## 13. Troubleshooting

### Database Connection Failed

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection
docker-compose exec postgres psql -U postgres -d maang_tracker -c "SELECT 1"
```

### Redis Connection Failed

```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### High Memory Usage

```bash
# Check Docker stats
docker stats

# Reduce cache TTL in .env
RAG_CACHE_TTL=300  # 5 minutes instead of 3600

# Restart services
docker-compose restart
```

### Slow Queries

```bash
# Enable query logging in PostgreSQL
docker-compose exec postgres psql -U postgres -d maang_tracker -c \
  "ALTER SYSTEM SET log_min_duration_statement = 1000;"

# View slow query logs
docker-compose exec postgres tail -f /var/log/postgresql/postgresql.log
```

## 14. Maintenance

### Update Services

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

### Clean Up

```bash
# Remove unused containers
docker-compose down

# Remove unused volumes (caution: deletes data)
docker volume prune

# Remove unused images
docker image prune -a
```

### Database Maintenance

```bash
# Vacuum and analyze
docker-compose exec postgres psql -U postgres -d maang_tracker -c "VACUUM ANALYZE;"

# Reindex
docker-compose exec postgres psql -U postgres -d maang_tracker -c "REINDEX DATABASE maang_tracker;"
```

## 15. Security Best Practices

- ✅ Use strong passwords for all services
- ✅ Enable SSL/TLS for HTTPS
- ✅ Regularly update Docker images
- ✅ Run containers with non-root users
- ✅ Use environment variables for secrets (never hardcode)
- ✅ Enable firewall rules
- ✅ Regular database backups
- ✅ Monitor access logs
- ✅ Keep dependencies updated
- ✅ Use private networks for internal communication

## 16. Support & Issues

For issues, check:

1. Docker logs: `docker-compose logs`
2. Service health: `docker-compose ps`
3. Resource availability: `docker stats`
4. Database connection: `docker-compose exec postgres psql -U postgres`

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
