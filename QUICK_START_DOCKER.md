# Quick Start Guide - Maang-Tracker with PostgreSQL + RAG + Docker

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites

- Docker & Docker Compose installed
- API Keys: Google, GitHub, OpenAI (optional)

### 2. Clone & Configure

```bash
# Clone repository
git clone <repo-url>
cd Maang-Tracker

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your editor
```

### 3. Start Everything

```bash
# Build and start all services
docker-compose up -d

# Wait for services to start (30 seconds)
sleep 30

# Check status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run migrations and seed data
docker-compose exec -T migrations bash -c "alembic upgrade head && python -m scripts.init_db"
```

### 5. Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| 🎯 **Dashboard** | http://localhost:5000 | Main interface |
| 🔧 **PGAdmin** | http://localhost:5050 | Database management |
| 💾 **Redis** | http://localhost:8081 | Cache management |
| 🤖 **MCP Server** | http://localhost:8765 | External tools |

### Default Credentials

```
PGAdmin:
  Email: admin@maang.local
  Password: admin

Redis:
  Password: redis-password (from .env)
```

## 📊 What's New

### ✨ Features Added

- **PostgreSQL Database**: Replaces SQLite for production scalability
- **RAG Memory System**: Semantic search with vector embeddings
- **Redis Caching**: Fast distributed caching
- **Vector Embeddings**: pgvector extension for similarity search
- **Docker Orchestration**: Complete containerization
- **Database Pooling**: Connection pooling for performance
- **Health Checks**: Automated service monitoring

### 🏗️ Architecture

```
┌─────────────┐
│   Nginx     │ (Reverse Proxy)
└──────┬──────┘
       │
   ┌───┴────┬──────────┐
   │        │          │
┌──▼─┐  ┌──▼─┐     ┌──▼──┐
│App │  │MCP │     │Auth │
└──┬─┘  └──┬─┘     └──┬──┘
   │       │          │
   └───┬───┴─────┬────┘
       │         │
    ┌──▼──┐  ┌───▼───┐
    │PG   │  │ Redis │
    │(RAG)│  │(Cache)│
    └─────┘  └───────┘
```

### 🔄 RAG System Flow

```
User Query
    ↓
Generate Embedding
    ↓
Search PostgreSQL (pgvector)
    ↓
Calculate Similarity
    ↓
Return Top-K Results (with Cache)
    ↓
Use for Agent Context
```

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f dashboard

# Stop services
docker-compose down

# Restart specific service
docker-compose restart dashboard

# Database access
docker-compose exec postgres psql -U postgres -d maang_tracker

# Redis access
docker-compose exec redis redis-cli

# Rebuild services
docker-compose build --no-cache

# Scale dashboard to 3 instances
docker-compose up -d --scale dashboard=3

# Clean everything (including data!)
docker-compose down -v
```

## 📈 Performance Tips

1. **Increase Cache TTL** for frequently accessed data
2. **Monitor Redis** at http://localhost:8081
3. **Monitor Database** at http://localhost:5050
4. **Check Docker stats**: `docker stats`

## 🔍 Monitoring

### Health Check

```bash
curl http://localhost/health
```

### Service Status

```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

### Database Queries

```bash
docker-compose exec postgres psql -U postgres -d maang_tracker -c "SELECT * FROM pg_stat_statements;"
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Check Docker daemon
docker info

# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Database connection error

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U postgres -c "SELECT 1"

# Check environment variables
cat .env | grep DB_
```

### Memory issues

```bash
# Check memory usage
docker stats

# Reduce Redis memory
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb

# Clear cache
docker-compose exec redis redis-cli FLUSHDB
```

## 📚 Documentation

- **Restructuring Plan**: `RESTRUCTURING_PLAN.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Architecture**: `ARCHITECTURE.md`

## 🚨 Important Notes

### First Time Setup

1. Change default passwords in `.env`
2. Generate strong `SECRET_KEY`
3. Add your API keys
4. Set `ENVIRONMENT=production` when deploying

### Security

- Don't commit `.env` file
- Use strong passwords
- Enable SSL/TLS in production
- Regular backups: `docker-compose exec postgres pg_dump ...`
- Monitor logs for errors

### Data Persistence

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres maang_tracker > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres maang_tracker < backup.sql

# Backup volumes
docker run --rm -v maang-postgres-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

## 🎯 Next Steps

1. ✅ Verify all services are healthy
2. ✅ Create first user account
3. ✅ Test interview platform
4. ✅ Configure training modules
5. ✅ Set up tracking integration
6. ✅ Monitor performance

## 📞 Support

- Check logs: `docker-compose logs -f`
- Database admin: http://localhost:5050
- Cache admin: http://localhost:8081

---

**Congratulations! Your Maang-Tracker is now running with production-grade PostgreSQL, RAG memory, Redis caching, and Docker containerization! 🎉**

For detailed configuration, see `DEPLOYMENT_GUIDE.md`
