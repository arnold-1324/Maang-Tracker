# MAANG Mentor - Complete System

A comprehensive, AI-driven platform for interview preparation and data structures mastery. Combines intelligent problem tracking, weakness detection, personalized roadmaps, and multi-source resource recommendations.

## 🎯 Features

### 1. **Intelligent Weakness Detection**
- Automatic topic classification from problem tags
- Analyzes LeetCode, GeeksforGeeks, TakeUForward submissions
- Generates weakness scores (0-100) for each topic
- Custom tuning from user Excel trackers and PDFs

### 2. **Multi-Source Resource Aggregation**
- **LeetCode**: Problem links by topic/difficulty
- **GeeksforGeeks**: Explore page with submission sorting
- **TakeUForward**: DSA curriculum integration
- Curated resources for 15+ data structure/algorithm topics

### 3. **Personalized Learning Roadmaps**
- Priority-based topic ordering (1-3)
- Estimated practice problems by difficulty
- Weekly milestones and study hours
- Resource links for each topic
- Flexible intensity levels (high/medium/low)

### 4. **Automated Notifications**
- **Slack Integration**: Daily summaries with formatted blocks
- **Discord Integration**: Embed-based notifications
- Customizable schedule (default: 9 AM daily)
- Dashboard links in notifications

### 5. **User Data Analysis**
- Parse Excel tracker files
- Extract topics from reference PDFs
- Generate custom weakness profiles
- Create tailored study recommendations

## 📦 Architecture

```
MAANG Mentor/
├── mcp_server/              # MCP tools (GitHub, LeetCode, GFG)
│   └── server.py           # FastMCP + uvicorn server
├── maang_agent/            # AI agent definition
│   └── agent.py            # Google ADK LlmAgent
├── ui/                     # Web dashboard
│   └── dashboard.py        # Flask dashboard (port 5100)
├── tracker/                # Problem tracking
│   ├── tracker.py          # Basic tracker
│   └── enhanced_tracker.py # Topic classification + notifications
├── roadmap/                # Study planning
│   ├── generator.py        # Basic generator
│   └── enhanced_generator.py # Multi-source recommendations
├── analyzer/               # User data analysis
│   ├── complexity_analyzer.py
│   └── user_data_analyzer.py # Excel + PDF parsing
├── memory/                 # Database layer
│   ├── db.py              # SQLite ORM
│   └── sqlite_schema.sql  # Database schema
├── integration/            # Main pipeline
│   └── main_pipeline.py   # Orchestrates full workflow
├── userData/               # User documents (Excel, PDFs)
├── docker-compose.yml     # Multi-container deployment
├── Dockerfile.mcp         # MCP server container
├── Dockerfile.adk         # ADK web UI container
├── Dockerfile.dashboard   # Dashboard container
└── .env                   # Configuration (secrets)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose (optional)
- Google API Key (for agent)
- GitHub Token (for tools)

### 1. Local Installation

```bash
# Clone/navigate to project
cd AI_Agent

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_your_token
GOOGLE_API_KEY=your_api_key
LEETCODE_USERNAME=your_username
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/...
EOF

# Create/initialize database
python -c "from memory.db import init_db; init_db()"
```

### 2. Start Services (Local)

**Terminal 1 - MCP Server**
```bash
python -u mcp_server/server.py
# Logs: "Starting uvicorn with mcp.streamable_http_app on 0.0.0.0:8765"
```

**Terminal 2 - ADK Web UI**
```bash
adk web --port 8000
# Access: http://127.0.0.1:8000
```

**Terminal 3 - Dashboard**
```bash
python ui/dashboard.py
# Access: http://127.0.0.1:5100
```

### 3. Start Services (Docker)

```bash
# Build containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access services
# - ADK: http://localhost:8000
# - Dashboard: http://localhost:5100
# - MCP: http://localhost:8765/mcp
```

## 📊 Usage Examples

### Run Full Analysis Pipeline

```bash
# Local
python integration/main_pipeline.py

# Docker
docker-compose exec dashboard python integration/main_pipeline.py
```

This:
1. Analyzes `userData/` files
2. Fetches problems from LeetCode/GFG/TakeUForward
3. Updates weakness profile
4. Generates personalized roadmap
5. Sends notifications (if configured)
6. Exports results to JSON and Markdown

### Analyze User Excel Tracker

```bash
python analyzer/user_data_analyzer.py
```

Generates:
- `analysis_report.json` - Comprehensive analysis
- Weakness profile with scores
- Topic recommendations
- Study hour estimates

### Generate Roadmap with Markdown

```bash
python -c "
from roadmap.enhanced_generator import EnhancedRoadmapGenerator
gen = EnhancedRoadmapGenerator()
roadmap = gen.generate()
with open('ROADMAP.md', 'w') as f:
    f.write(gen.export_roadmap(format='markdown'))
print('✅ Roadmap saved to ROADMAP.md')
"
```

### Send Manual Notification

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

## 🗂️ Configuration

### Environment Variables

```env
# Required
GITHUB_TOKEN=                    # GitHub API token
GOOGLE_API_KEY=                  # Google Gemini API key

# Tracking
LEETCODE_USERNAME=               # LeetCode account
GFG_USERNAME=                    # GeeksforGeeks account
TUF_USERNAME=                    # TakeUForward account

# Notifications (Optional)
SLACK_WEBHOOK_URL=               # Slack incoming webhook
DISCORD_WEBHOOK_URL=             # Discord webhook

# Database
SQLITE_PATH=./memory.db          # Database location
MCP_PORT=8765                    # MCP server port
```

### Database Schema

```sql
-- weakness_profile: Topic difficulty tracking
CREATE TABLE weakness_profile (
    topic TEXT PRIMARY KEY,
    score INTEGER,
    last_seen DATETIME
);

-- user_snapshot: LeetCode/GitHub submission history
CREATE TABLE user_snapshot (
    source TEXT,
    key TEXT,
    data JSON,
    created_at DATETIME
);
```

## 📈 Workflow

```
User Data Files → Excel/PDF Parser
                    ↓
LeetCode/GFG/TUF → Problem Classifier → Weakness Profile
                    ↓
            Roadmap Generator
                    ↓
        Resource Aggregator
                    ↓
Slack/Discord Notification + Dashboard Display
```

## 🔌 API Integrations

### Supported Tools (via MCP)
- **GitHub**: `list_repos(username)` - Fetch repositories
- **LeetCode**: `leetcode_stats(username)` - Submission statistics
- **GeeksforGeeks**: `gfg_search(query)` - Article search

### Supported Sources
- **LeetCode**: https://leetcode.com/graphql
- **GeeksforGeeks**: https://www.geeksforgeeks.org/explore?page=1&sortBy=submissions
- **TakeUForward**: https://takeuforward.org/plus/dsa/

## 📚 Resources Generated

Each topic roadmap includes:

```json
{
  "topic": "dynamic-programming",
  "weakness_score": 75,
  "intensity": "high",
  "estimated_problems": 75,
  "estimated_hours": {
    "total": 30,
    "per_week": 8
  },
  "resources": [
    {
      "source": "leetcode",
      "url": "https://leetcode.com/tag/dynamic-programming/",
      "type": "curated_problems"
    },
    {
      "source": "geeksforgeeks",
      "url": "https://www.geeksforgeeks.org/dynamic-programming/",
      "type": "curated_problems"
    },
    {
      "source": "takeuforward",
      "url": "https://takeuforward.org/plus/dsa/",
      "type": "curated_curriculum"
    }
  ],
  "milestones": [
    {
      "week": 1,
      "target_problems": 19,
      "goal": "Complete 19 dynamic-programming problems"
    }
  ]
}
```

## 🔔 Notifications

### Slack Format
- Header: "🎯 MAANG Mentor Daily Report"
- Top 5 weak topics with scores
- "View Dashboard" button
- Timestamp footer

### Discord Format
- Embed title: "🎯 MAANG Mentor Daily Report"
- Fields for each weak topic
- Color-coded by severity
- Footer with timestamp

## 🐳 Docker Details

### Services

| Service | Port | Image | Command |
|---------|------|-------|---------|
| mcp-server | 8765 | python:3.13-slim | `python mcp_server/server.py` |
| adk-web | 8000 | python:3.13-slim | `adk web --port 8000` |
| dashboard | 5100 | python:3.13-slim | `python ui/dashboard.py` |

### Networking
- Internal: `maang-network` bridge
- Services communicate via hostnames
- Example: `http://mcp-server:8765/mcp`

### Volumes
- All services share `memory/` volume for database
- Config changes reflected in real-time

## 🧪 Testing

```bash
# Test imports
python -c "from analyzer.user_data_analyzer import UserDataAnalyzer; print('✅')"

# Test pipeline
python integration/main_pipeline.py --dry-run

# Test notifications
python -c "from tracker.enhanced_tracker import ProblemTracker; print(ProblemTracker().TOPIC_DIFFICULTY_MAP)"

# Test database
python -c "from memory.db import init_db, get_weaknesses; init_db(); print(get_weaknesses())"
```

## 📝 Generated Files

| File | Purpose |
|------|---------|
| `ROADMAP_GENERATED.md` | Formatted study roadmap |
| `pipeline_results_*.json` | Full analysis results |
| `analysis_report.json` | User data analysis |
| `execution_log.json` | Pipeline execution timeline |
| `memory.db` | SQLite database |

## 🤝 Contributing

To extend functionality:

1. Add new tools to `mcp_server/server.py` with `@mcp.tool()` decorator
2. Extend topic classification in `tracker/enhanced_tracker.py`
3. Add resources to `roadmap/enhanced_generator.py` RESOURCE_SOURCES
4. Update schema in `memory/sqlite_schema.sql`

## 📄 License

[Your License Here]

## 🆘 Support

For issues:
1. Check logs: `docker-compose logs -f [service]`
2. Verify env vars: `cat .env`
3. Test connectivity: `Test-NetConnection localhost -Port 8765`
4. Review documentation in `DOCKER_GUIDE.md` and `START_SERVICES.md`

---

**Last Updated**: November 16, 2025
**Python Version**: 3.13+
**Docker Version**: 20.10+
