# Dashboard Navigation Guide 🎯

**Date**: November 17, 2025  
**Status**: ✅ All Pages Live

---

## Dashboard URL

### Main Entry Point
- **Address**: http://localhost:5100
- **Status**: 🟢 Running
- **Access**: Direct browser access

---

## Available Pages

### 1. **Home** - http://localhost:5100/
**What You'll See:**
- Welcome banner with platform overview
- Quick statistics:
  - Total Problems Available
  - Problems You've Completed
  - Your Success Rate
- Quick action cards (Start Interview, View Roadmap, Sync Progress)
- Your weakness profile summary
- Option to sync GitHub/LeetCode accounts

**Features:**
- Latest activity overview
- Performance metrics
- Quick access to main features

---

### 2. **Interview** - http://localhost:5100/interview
**What You'll See:**
- Three interview modes:
  - **Coding Interview** (LeetCode-style)
    - Select difficulty (Easy/Medium/Hard)
    - Practice real coding problems
    - Live code execution
  
  - **System Design Interview**
    - Enter topic (URL shortener, Cache, etc.)
    - Discuss architecture
    - Design database schemas
  
  - **Behavioral Interview**
    - STAR method questions
    - Practice communication
    - Real-time feedback

- Recent interviews history
- Performance stats

**How to Use:**
1. Select interview type
2. Choose difficulty (for coding)
3. Click "Start Interview"
4. Solve the problem
5. Get AI feedback

---

### 3. **Roadmap** - http://localhost:5100/roadmap
**What You'll See:**
- Personalized 12-week learning path
- Topics organized by difficulty:
  - **Week 1-2**: Arrays & Strings (2-pointer, sliding window)
  - **Week 3-4**: Trees & Graphs (DFS, BFS)
  - **Week 5-8**: Dynamic Programming (patterns, optimizations)
  - **Week 9-10**: System Design (scalability, databases)
  - **Week 11-12**: Behavioral & Review

- Progress bars for each week
- Recommended problems per topic
- Difficulty ratings

**Features:**
- Adaptive recommendations based on weaknesses
- Progress tracking
- Milestone tracking

---

### 4. **Weaknesses** - http://localhost:5100/weakness
**What You'll See:**
- All identified weak areas
- Score for each weakness (0-10 scale)
- Last attempted date
- Practice difficulty badges

**For Each Weakness:**
- Color-coded difficulty
- Recent attempts
- "Practice Now" button
- Recommended problems

---

### 5. **Training** - http://localhost:5100/training
**What You'll See:**
- Guided learning modules:
  - Arrays & Strings
  - Dynamic Programming
  - System Design
  - Graphs & Trees
  - (More coming soon)

**Features:**
- Step-by-step lessons
- Interactive code editor
- Practice problems with hints
- Video tutorials

---

## Navigation Bar

Located at the top of every page:

```
[Home] [Interview] [Roadmap] [Training] [Weaknesses]
```

Click any link to jump to that section.

---

## Key Features

### 🔄 Sync Your Progress
- **Where**: Home page, top form
- **How**: 
  1. Enter your GitHub username
  2. Enter your LeetCode username
  3. Click "Sync Now"
- **What It Does**: 
  - Fetches your LeetCode problem history
  - Analyzes your GitHub solutions
  - Updates weakness profile
  - Recalculates recommendations

### 📊 View Statistics
- Home page shows:
  - Total problems solved
  - Success rate percentage
  - Topics mastered
  - Time spent

### 🎯 Start Interview
- **Quick Start**: Home page "Start Interview" button
- **Dedicated Page**: Interview page (more options)
- **Options**: 
  - Easy/Medium/Hard coding problems
  - System design topics
  - Behavioral questions

---

## API Endpoints (Backend)

If using the API directly:

### Interview Endpoints
```
GET  /api/interview/problems/<difficulty>      - Get problems by difficulty
GET  /api/interview/problem/<problem_id>        - Get specific problem
GET  /api/interview/system-design/<topic>       - Get system design problem
GET  /api/interview/behavioral-question         - Get behavioral question
POST /api/interview/session/create              - Start new session
POST /api/interview/session/<id>/submit-code    - Submit code for evaluation
POST /api/interview/session/<id>/end            - End interview session
```

### Scheduling Endpoints
```
POST /api/interview/schedule/create             - Schedule interview
GET  /api/interview/schedule/next/<user_id>     - Get next scheduled
GET  /api/interview/schedule/upcoming/<user_id> - Get upcoming interviews
POST /api/interview/schedule/<id>/complete      - Mark as complete
POST /api/interview/schedule/<id>/cancel        - Cancel interview
```

---

## Design & Styling

### Color Scheme
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Accent**: White backgrounds with purple borders
- **Text**: Dark gray on white

### Features
- ✨ Smooth animations and transitions
- 🎨 Responsive grid layout
- 📱 Mobile-friendly design
- 🎯 Large, clickable buttons
- 📊 Visual progress bars

---

## Troubleshooting

### Page Shows 404 Error
**Problem**: Route not found
**Solution**:
- Make sure dashboard is running: `docker-compose ps`
- Restart dashboard: `docker-compose restart dashboard`
- Check correct spelling: `/interview` not `/interviews`

### Buttons Don't Respond
**Problem**: API endpoints not responding
**Solution**:
- Check interview service: `docker logs maang-mcp-server`
- Ensure all containers are running
- Refresh the page

### Sync Fails
**Problem**: Cannot update from GitHub/LeetCode
**Solution**:
- Check internet connection
- Verify username is correct
- Check API keys in environment variables
- Review logs: `docker logs maang-dashboard`

---

## Quick Start Workflow

### First Time Setup
1. **Go Home** (http://localhost:5100/)
2. **Sync Progress** with GitHub/LeetCode username
3. **View Weakness** to see what to focus on
4. **Check Roadmap** for learning path
5. **Start Interview** from Coding section

### Daily Practice
1. **View Weaknesses** page
2. **Click "Practice Now"** on weak topics
3. **Complete Interview** in chosen mode
4. **Review Results** and feedback
5. **Sync Progress** to update stats

### Weekly Review
1. **Check Roadmap** progress
2. **View Statistics** on home page
3. **Complete 3-5 interviews** across all modes
4. **Sync with LeetCode** to update
5. **Adjust learning path** if needed

---

## Advanced Features

### Interview Session Tracking
- Real-time feedback during code submission
- Performance scoring
- Time tracking
- Solution comparison with optimal

### Progress Analytics
- Graphs showing improvement over time
- Problem mastery tracking
- Topic coverage percentage
- Success rate trends

### Personalized Recommendations
- AI-driven suggestions based on:
  - Your weaknesses
  - Time available
  - Target difficulty
  - Past performance

---

## Browser Compatibility

✅ **Supported**:
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

⚠️ **Not Tested**:
- Internet Explorer (Not recommended)

---

## Performance Tips

1. **Use Modern Browser**: Chrome/Firefox recommended
2. **Enable JavaScript**: Required for all features
3. **Check Internet**: Stable connection for syncing
4. **Clear Cache**: If pages load incorrectly
5. **Disable Ad Blockers**: Might block API calls

---

## Contact & Support

### Reporting Issues
- Check logs: `docker-compose logs dashboard`
- Verify all services running: `docker-compose ps`
- Restart service: `docker-compose restart dashboard`

### Common Commands
```powershell
# View all pages working
docker-compose ps

# Check dashboard status
docker logs maang-dashboard -f

# Restart dashboard
docker-compose restart dashboard

# Full rebuild if issues persist
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Summary

✅ **5 Main Pages** - Home, Interview, Roadmap, Weaknesses, Training  
✅ **Multiple Interview Modes** - Coding, System Design, Behavioral  
✅ **Progress Tracking** - Sync with GitHub/LeetCode  
✅ **Smart Recommendations** - Personalized learning path  
✅ **Real-time Feedback** - AI-powered interview assistant  

**Status**: 🟢 **All Systems Operational**

**Next Steps**: Visit http://localhost:5100 and start practicing!
