# Docker Deployment Guide for MAANG Mentor

## Quick Start

### 1. Build and Run All Services

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
# GitHub API
GITHUB_TOKEN=ghp_your_github_token_here

# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# LeetCode / GeeksforGeeks / TakeUForward
LEETCODE_USERNAME=your_leetcode_username
GFG_USERNAME=your_gfg_username
TUF_USERNAME=your_tuf_username

# Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR/WEBHOOK/URL

# Database
SQLITE_PATH=/app/memory/memory.db
MCP_PORT=8765
```

## Services

| Service | Port | Container | Health Check |
|---------|------|-----------|--------------|
| MCP Server | 8765 | `maang-mcp-server` | `curl http://localhost:8765/mcp` |
| ADK Web | 8000 | `maang-adk-web` | http://localhost:8000 |
| Dashboard | 5100 | `maang-dashboard` | http://localhost:5100 |

## Features

### 1. Enhanced Problem Tracking
- Automatic topic classification from problem tags
- Support for LeetCode, GeeksforGeeks, TakeUForward
- Weakness profile scoring (0-100)
- Historical tracking with snapshots

### 2. User Data Analysis
- Parse Excel tracker (`userData/Maang tracker (1).xlsx`)
- Extract topics from reference PDFs
- Generate personalized study plans
- Custom weakness tuning

### 3. Intelligent Recommendations
- Multi-source resource aggregation (LeetCode, GFG, TakeUForward)
- Problem count estimation by difficulty
- Weekly milestones and study hours
- Priority-based scheduling

### 4. Notifications
- Daily Slack summaries (configurable time)
- Discord embed notifications
- Customizable report format
- Dashboard links in notifications

## Usage Examples

### Analyze User Data

```bash
docker-compose exec dashboard python analyzer/user_data_analyzer.py
```

This will:
1. Parse `userData/Maang tracker (1).xlsx`
2. Extract topics from PDFs
3. Generate weakness profile
4. Create study recommendations
5. Export `analysis_report.json`

### Generate Enhanced Roadmap

```bash
docker-compose exec dashboard python roadmap/enhanced_generator.py
```

### Send Daily Notification

```bash
docker-compose exec dashboard python -c "
from tracker.enhanced_tracker import ProblemTracker
import os

tracker = ProblemTracker()
tracker.send_daily_summary(
    slack_webhook=os.getenv('SLACK_WEBHOOK_URL'),
    discord_webhook=os.getenv('DISCORD_WEBHOOK_URL')
)
"
```

## Volume Mounts

- **memory/**: SQLite database and snapshots
- **mcp_server/**: MCP server code and tools
- **maang_agent/**: Agent definitions
- **ui/**: Dashboard frontend
- **tracker/, roadmap/, analyzer/**: Core modules

## Networking

Services communicate over the `maang-network` bridge:
- MCP Server: `http://mcp-server:8765/mcp`
- ADK Web: `http://adk-web:8000`
- Dashboard: `http://dashboard:5100`

## Debugging

### View Container Logs
```bash
docker-compose logs -f mcp-server
docker-compose logs -f adk-web
docker-compose logs -f dashboard
```

### Access Container Shell
```bash
docker-compose exec mcp-server /bin/bash
docker-compose exec dashboard python
```

### Test MCP Server
```bash
docker-compose exec mcp-server curl -X GET http://mcp-server:8765/mcp
```

### Check Network Connectivity
```bash
docker-compose exec dashboard ping mcp-server
docker-compose exec adk-web ping mcp-server
```

## Production Considerations

1. **Environment Variables**: Store secrets in a secure location, not in `.env`
2. **Persistent Storage**: Map volumes to host directories
3. **Resource Limits**: Add `cpu_shares`, `memory` limits in docker-compose.yml
4. **Monitoring**: Use Docker Compose health checks
5. **Logging**: Configure log drivers (json-file, splunk, awslogs, etc.)
6. **Reverse Proxy**: Use Nginx for production access
7. **SSL/TLS**: Implement HTTPS certificates

## Example Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mcp-server:
    # ... base config ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    restart: always

  # Add reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/:/etc/nginx/ssl/:ro
    depends_on:
      - adk-web
      - dashboard
```

## Troubleshooting

### MCP Server won't start
```bash
# Check port 8765 is not in use
docker-compose down
docker-compose up -d mcp-server
docker-compose logs mcp-server
```

### ADK can't connect to MCP
```bash
# Verify network connectivity
docker-compose exec adk-web ping mcp-server
# Should return: mcp-server is being resolved correctly
```

### Database locked errors
```bash
# Check database permissions
docker-compose exec dashboard ls -la memory/
# Ensure write permissions
```

## Scaling

For multi-user deployment:

```yaml
# Use docker-compose with scaling
docker-compose up -d --scale dashboard=3
```

Use a load balancer (Nginx, HAProxy) to distribute traffic.
