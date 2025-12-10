# Next.js Dashboard Integration with Docker

## ✅ Changes Made

### 1. Dockerfile Updates

#### `docker/Dockerfile.dashboard` - Complete Overhaul
- **Before**: Flask-based Python dashboard on port 5000
- **After**: Multi-stage Next.js build with production optimization
  - Build stage: Installs dependencies and builds Next.js app
  - Production stage: Optimized runtime with only necessary files
  - Port: 3000 (standard Node.js)
  - Non-root user: `nextjs` (UID 1001)
  - Health check: Simple HTTP health check

#### `docker/Dockerfile.app` - Python App Improvements
- Added proper package manager initialization
- Better error handling for package installation
- Installed curl for health checks

#### `docker/Dockerfile.mcp` - MCP Server Improvements
- Added proper package manager initialization
- Better error handling for package installation
- Installed curl for health checks

### 2. Docker Compose Updates

#### `docker-compose.yml` - Dashboard Service
**Old Configuration:**
```yaml
dashboard:
  dockerfile: docker/Dockerfile.dashboard
  environment:
    FLASK_PORT: 5000
    # ... Python/Flask env vars
  ports:
    - "5000:5000"
  command: python ui/dashboard.py
```

**New Configuration:**
```yaml
dashboard:
  build:
    target: production
  environment:
    NODE_ENV: development
    NEXT_PUBLIC_API_URL: http://localhost:8000
    NEXT_PUBLIC_MCP_URL: http://localhost:8765
  ports:
    - "3000:3000"
```

### 3. Nginx Reverse Proxy

#### `docker/nginx.conf` - Port Update
- Updated upstream from `dashboard:5000` to `dashboard:3000`
- Maintains full reverse proxy, SSL, load balancing capabilities
- Routes:
  - `/` → Next.js dashboard (port 3000)
  - `/api/*` → MCP Server or backend (port 8765)
  - Static assets served with gzip compression

### 4. Next.js Configuration

#### `dashboard/next.config.ts` - Docker Optimization
Added:
- `output: 'standalone'` - Enables Docker-optimized standalone build
- Environment-based API URLs for dev/prod flexibility
- `NEXT_PUBLIC_API_URL` - Backend API endpoint
- `NEXT_PUBLIC_MCP_URL` - MCP server endpoint
- Image optimization disabled (for Docker compatibility)
- Dynamic rewrites for API routing

### 5. Startup Scripts

#### `docker/start-services.ps1` & `docker/start-services.sh`
- Updated access points documentation:
  - Dashboard: `http://localhost:3000` ← **NEW**
  - Nginx: `http://localhost:80` (reverse proxy)
  - All other services remain the same

## 🚀 Port Configuration

### Service Port Mapping

| Service | Internal Port | Docker Port | Access |
|---------|---|---|---|
| **Next.js Dashboard** | 3000 | 3000 | `localhost:3000` |
| **Nginx Reverse Proxy** | 80 | 80 | `localhost:80` |
| **PostgreSQL** | 5432 | 5432 | `localhost:5432` |
| **Redis** | 6379 | 6379 | `localhost:6379` |
| **PGAdmin** | 80 | 5050 | `localhost:5050` |
| **Redis Commander** | 8081 | 8081 | `localhost:8081` |
| **MCP Server** | 8765 | 8765 | `localhost:8765` |

## 📦 Docker Image Sizes (Expected)

- **Next.js Dashboard**: ~150-200 MB (with node_modules)
- **Python App**: ~500-600 MB (with dependencies)
- **MCP Server**: ~450-500 MB (with dependencies)

## 🔧 Build Process

### Multi-Stage Build for Next.js
```
Stage 1: builder (node:20-alpine)
  - Installs npm dependencies
  - Runs: npm run build
  - Creates: .next, public/

Stage 2: production (node:20-alpine)
  - Copies built artifacts from builder
  - Installs only production dependencies
  - Creates non-root user
  - Sets up health check
  - Runs: npm start
```

## 📝 Environment Variables

### Added to `.env`:
```env
# Already supported by Next.js
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MCP_URL=http://localhost:8765
```

## ✨ Benefits

1. **Performance**: Next.js production build is optimized
2. **Security**: Non-root Docker user
3. **Scalability**: Standalone mode allows easy Kubernetes deployment
4. **Flexibility**: Environment-based configuration
5. **Health Checks**: Automated service monitoring
6. **Small Runtime**: Production image is lean and efficient

## 🚦 Next Steps

1. **Build images**:
   ```bash
   docker-compose build
   ```

2. **Start services**:
   ```bash
   # Windows PowerShell
   docker/start-services.ps1
   
   # Linux/Mac Bash
   docker/start-services.sh
   ```

3. **Access dashboard**:
   - Direct: `http://localhost:3000`
   - Via Nginx: `http://localhost:80`

4. **View logs**:
   ```bash
   docker-compose logs -f dashboard
   ```

## 🐛 Troubleshooting

### Next.js build fails
```bash
# Clear node_modules and rebuild
docker-compose down
rm -rf dashboard/node_modules dashboard/.next
docker-compose build --no-cache
```

### Port already in use
```bash
# Check what's using port 3000
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows
```

### Dashboard won't start
```bash
# Check Next.js logs
docker-compose logs dashboard

# Ensure dashboard directory exists with package.json
ls dashboard/package.json
```

## 📚 References

- Next.js with Docker: https://nextjs.org/docs/deployment/docker
- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- Node.js best practices: https://github.com/nodejs/docker-node/blob/main/README.md

---

**Status**: ✅ Ready for testing
**Last Updated**: December 5, 2025
