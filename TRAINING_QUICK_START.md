# Training Agent - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Start the System
```bash
cd c:\Users\anlsk\AI_Agent
docker-compose up -d
```

### 2. Access Training Dashboard
```
http://localhost:5100/training/dashboard
```

### 3. Export Your Progress
- Visit https://takeuforward.org (your profile)
- Export progress JSON (or use your `userData/learned_DSA_and_SystemDesign.json`)

### 4. Paste & Analyze
- Paste JSON in dashboard
- Click "Analyze Progress"
- View your gaps and strengths

---

## 📊 Dashboard Sections

### Section 1: Analyze Progress
**Input:** Your TakeUForward progress JSON  
**Output:** Topic coverage %, gaps, strengths, next topics

**Example Result:**
```
- Arrays: 75% coverage
- Recursion: 30% coverage (PRIORITY)
- Binary Search: 85% coverage
```

### Section 2: Generate Training Plan
**Input:** Duration (days) + Daily target (problems)  
**Output:** Weekly schedule with specific problems

**Default:** 30 days, 5 problems/day = 150 total problems

### Section 3: Get Custom Problem
**Input:** Topic + Difficulty + Focus area  
**Output:** Problem name, URL, hints, time limit, approach

**Topics Available:**
- arrays, strings, linked-list, binary-search
- recursion, hashing, sorting
- dynamic-programming, graphs

**Difficulties:** easy, medium, hard

---

## 🎯 How It Works

### Step 1: Progress Analysis
```
Your 131 Solved Problems
         ↓
Categorize by Topic
         ↓
Calculate Coverage %
         ↓
Compute Gap Scores
         ↓
Identify Priorities
```

### Step 2: Plan Generation
```
Top 5 Weak Topics
         ↓
Distribute across weeks
         ↓
Add difficulty progression
         ↓
Select specific problems
         ↓
Create milestones
```

### Step 3: Custom Problems
```
Select Topic & Difficulty
         ↓
Pick from TUF curriculum
         ↓
Generate hints
         ↓
Set time limit
         ↓
Return with approach
```

---

## 📈 Key Metrics

### Gap Score
- **Formula:** (100 - Coverage%) × Difficulty Weight
- **Interpretation:** Higher = more urgent to learn

### Coverage %
- **Formula:** (Solved / Total in Topic) × 100
- **Target:** 70%+ for each topic

### Priority Levels
- **Critical:** >150 gap score (learn immediately)
- **High:** 100-150 (secondary focus)
- **Medium:** 50-100 (maintenance)
- **Low:** <50 (skip or light review)

---

## 🔧 MCP Tools (7 Available)

### 1. analyze_dsa_progress
```bash
Analyze your 131 problems and identify gaps
Input: progress_json
Output: coverage, gaps, strengths, recommendations
```

### 2. generate_training_plan
```bash
Create 30-day personalized plan
Input: progress_json, duration_days, daily_target
Output: weekly schedule with specific problems
```

### 3. get_custom_problem
```bash
Get a problem recommendation
Input: topic, difficulty, focus_area
Output: problem name, hints, time limit, approach
```

### 4. identify_weak_topics
```bash
Ranked list of your weakest areas
Input: progress_json
Output: weak areas with coverage and priority
```

### 5. get_tuf_curriculum
```bash
Browse TakeUForward curriculum
Input: topic (optional)
Output: all available problems per difficulty
```

### 6. calculate_study_hours
```bash
Estimate study time needed
Input: topics (comma-separated), difficulty_level
Output: estimated hours with review
```

### 7. get_interview_prep_roadmap
```bash
MAANG interview prep roadmap
Input: experience_level (beginner/intermediate/advanced)
Output: weeks, phases, topics, timeline
```

---

## 📝 Example Usage

### Use Case 1: Identify Weakest Topic
```
1. Paste progress JSON
2. Analyze Progress
3. Check "Next Topics" → shows [recursion, graphs, strings]
4. Focus on recursion (most critical)
```

### Use Case 2: Create 30-Day Plan
```
1. Analyze progress
2. Set duration: 30 days
3. Set daily target: 5 problems
4. Generate Plan
5. Follow weekly schedule
```

### Use Case 3: Get Problem for Today
```
1. Check weakest topic (e.g., recursion)
2. Select: topic=recursion, difficulty=medium
3. Click "Get Problem"
4. Get: "letter-combinations-of-phone-number" with hints
5. Solve and track time
```

### Use Case 4: Interview Prep
```
1. Select: experience_level=intermediate
2. Get Roadmap
3. Follow 10-week timeline
4. Focus on hard problems weeks 9-10
5. Use for mock interviews
```

---

## 💾 Database Tracking

### Tables Created
1. **training_sessions** - Track problems solved, time, attempts
2. **learning_gaps** - Store gap analysis results
3. **training_plans** - Save generated plans

### View Sessions
```python
from training.adaptive_learning_agent import AdaptiveLearningAgent
agent = AdaptiveLearningAgent()
stats = agent.get_training_stats()
# Returns: total_sessions, topics breakdown, total_time, avg_attempts
```

---

## ⏱️ Time Estimates

### Study Time Per Topic
- **Easy Problems**: 30 minutes each
- **Medium Problems**: 1 hour each
- **Hard Problems**: 1.5 hours each

### 30-Day Plan Example (150 problems)
```
Week 1: 25 problems (arrays, easy/medium)
Week 2: 25 problems (recursion, medium)
Week 3: 25 problems (graphs, medium/hard)
Week 4: 25 problems (review + hard)
...
Total: ~180 hours (6 hours/day recommended)
```

---

## 🎓 Best Practices

### Daily Routine
```
1. Check dashboard for daily problem
2. Spend 1 hour solving
3. Review solution (30 min)
4. Log time in dashboard
5. Track progress
```

### Weekly Review
```
1. Check topic coverage stats
2. Identify improving topics
3. Rotate to next weak area
4. Update training plan if needed
```

### Monthly Goals
```
1. Complete 150 problems (5/day × 30 days)
2. Achieve 70%+ coverage on all topics
3. Master hard problems (practice 50)
4. Take 2 mock interviews
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard won't load | Restart: `docker-compose restart dashboard` |
| Invalid JSON error | Use valid JSON format; validate with `python -m json.tool` |
| No topics found | Check TakeUForward account and export data |
| Train slow | Increase `daily_target` or extend `duration_days` |
| Lost progress | Check `memory/memory.db` for session data |

---

## 📞 Support

### Check System Status
```bash
# All containers running?
docker-compose ps

# MCP server accessible?
curl http://localhost:8765/mcp

# Dashboard reachable?
curl http://localhost:5100/training/dashboard
```

### View Logs
```bash
# Dashboard logs
docker-compose logs dashboard --tail 50

# MCP server logs
docker-compose logs mcp-server --tail 50
```

### Reset & Start Fresh
```bash
docker-compose down
rm memory/memory.db
docker-compose up -d
```

---

## 🎯 Next Steps

1. **Export Progress** from TakeUForward
2. **Upload to Dashboard** and analyze
3. **Generate Training Plan** for 30 days
4. **Follow Daily Schedule** with custom problems
5. **Track Progress** in database
6. **Take Mock Interviews** with hard problems
7. **Prepare for MAANG** interviews!

---

## Key Takeaway

Your agent has learned **131 DSA problems** across key topics. Now use the **AI training system** to:
- Identify your **biggest learning gaps**
- Create a **personalized 30-day roadmap**
- Get **custom problems** matching your weaknesses
- Track **progress in real-time**
- **Master MAANG interview prep**

**Start here:** http://localhost:5100/training/dashboard
