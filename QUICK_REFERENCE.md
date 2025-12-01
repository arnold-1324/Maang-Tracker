# Quick Reference - MAANG Mentor

## 🚀 Quick Start

### Local Setup (3 terminals)
```bash
# Terminal 1: MCP Server
python -u mcp_server/server.py

# Terminal 2: ADK Web
adk web --port 8000

# Terminal 3: Dashboard
python ui/dashboard.py
```

### Docker Setup
```bash
docker-compose up -d
```

## 📍 Access Points
- **ADK Web**: http://localhost:8000
- **Dashboard**: http://localhost:5100
- **MCP API**: http://localhost:8765/mcp

## ⚙️ Configuration

### .env File
```env
GITHUB_TOKEN=ghp_xxx
GOOGLE_API_KEY=xxx
LEETCODE_USERNAME=xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/xxx
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/xxx
```

## 🔨 Common Commands

### Run Full Pipeline
```bash
python integration/main_pipeline.py
```

### Analyze User Data
```bash
python analyzer/user_data_analyzer.py
```

### Generate Roadmap
```bash
python roadmap/enhanced_generator.py
```

### Send Notification
```bash
python -c "
from tracker.enhanced_tracker import ProblemTracker
import os
tracker = ProblemTracker()
tracker.send_daily_summary(
    slack_webhook=os.getenv('SLACK_WEBHOOK_URL'),
    discord_webhook=os.getenv('DISCORD_WEBHOOK_URL')
)
"
```

### Docker Logs
```bash
docker-compose logs -f [service]
# Services: mcp-server, adk-web, dashboard
```

## 📊 Module Overview

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **mcp_server** | AI tools access | server.py (GitHub, LeetCode, GFG) |
| **tracker** | Problem tracking | enhanced_tracker.py (topic classification) |
| **analyzer** | User data analysis | user_data_analyzer.py (Excel + PDF) |
| **roadmap** | Study planning | enhanced_generator.py (3 sources) |
| **integration** | Main pipeline | main_pipeline.py (orchestration) |
| **memory** | Database | db.py (SQLite) |

## 💪 Weakness Scoring

- **High** (70-100): Urgent, start immediately
- **Medium** (40-70): Important, start in 3 days
- **Low** (0-40): Nice-to-have, start in 1 week

## 📚 Topics Covered

Array, String, Linked-List, Stack, Queue, Hash-Table, Tree, Binary-Search-Tree, Graph, Backtracking, Dynamic-Programming, Greedy, Sorting, Bit-Manipulation, Math, Database, Design, System-Design

## 🔔 Notifications

### Slack Format
- Daily summary with top 5 weak topics
- Dashboard link button
- Default: 9 AM daily

### Discord Format
- Rich embed notification
- Topic breakdown fields
- Color-coded severity

## 📁 Input Files

Place in `userData/` for analysis:
- `Maang tracker (1).xlsx` - Your problem tracker
- PDF reference books (optional)

## 📤 Output Files

Generated during pipeline run:
- `ROADMAP_GENERATED.md` - Study roadmap
- `pipeline_results_*.json` - Full results
- `analysis_report.json` - User analysis
- `execution_log.json` - Timeline

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change `MCP_PORT` env var |
| MCP won't connect | Verify `http://localhost:8765/mcp` returns data |
| Dashboard imports fail | Run from project root (not ui/) |
| Notifications fail | Check webhook URLs in `.env` |
| Database locked | Ensure single access (close other terminals) |

## 📖 Documentation

- **README.md** - Full system guide
- **DOCKER_GUIDE.md** - Deployment details
- **START_SERVICES.md** - Local setup steps
- **IMPLEMENTATION_SUMMARY.md** - What was built

## 🎯 Typical Workflow

```
1. Analyze user data: python analyzer/user_data_analyzer.py
   ↓
2. Run full pipeline: python integration/main_pipeline.py
   ↓
3. Check dashboard: http://localhost:5100
   ↓
4. Review roadmap: ROADMAP_GENERATED.md
   ↓
5. Get notification: Slack/Discord message
```

## 💾 Database

SQLite location: `memory.db` (or `$SQLITE_PATH`)

Tables:
- `weakness_profile` - Topic scores
- `user_snapshot` - Problem history

## 🔐 Security

✅ No hardcoded credentials  
✅ API keys via env variables  
✅ Docker volume isolation  
✅ Network segmentation  

## 📦 Dependencies

Core:
- google-adk, fastmcp, mcp, flask, uvicorn

Analysis:
- openpyxl, PyPDF2, requests, beautifulsoup4

Scheduling:
- apscheduler

## 🆘 Help

1. Check logs: `docker-compose logs -f`
2. Verify config: `cat .env`
3. Test connectivity: `curl http://localhost:8765/mcp`
4. Review docs: See file list above

## ✅ Health Checks

```bash
# All services running?
docker-compose ps

# MCP responding?
curl http://localhost:8765/mcp

# Database ready?
python -c "from memory.db import get_weaknesses; print(get_weaknesses())"

# Imports working?
python -c "from analyzer.user_data_analyzer import UserDataAnalyzer; print('OK')"
```

---

**Version**: 2.0  
**Updated**: November 16, 2025  
**Ready for**: Production deployment
