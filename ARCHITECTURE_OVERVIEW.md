# 🎯 Dashboard Architecture & Navigation

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     User's Browser                              │
│              http://localhost:5100                              │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Web Server      │
                    │ Port: 5100      │
                    │ Flask App       │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐  ┌──────────▼────────┐  ┌──────▼─────────┐
│   Interview  │  │  Roadmap &        │  │  Training      │
│   Routes     │  │  Weakness         │  │  Resources     │
│              │  │  Tracker          │  │                │
│ /interview   │  │  Generator        │  │ /training      │
└───────┬──────┘  └──────────┬────────┘  └──────┬─────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐  ┌──────────▼────────┐  ┌──────▼─────────┐
│   MCP        │  │  Memory/          │  │  Code          │
│   Server     │  │  Database         │  │  Compiler      │
│   8765       │  │  SQLite           │  │  (if needed)   │
└──────────────┘  └───────────────────┘  └────────────────┘
```

---

## Frontend Navigation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Navigation Bar                                │
│  [Home] [Interview] [Roadmap] [Training] [Weaknesses]           │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
     
    ┌─ HOME ─┐       ┌─ INTERVIEW ─┐      ┌─ ROADMAP ─┐
    │ /       │       │ /interview  │      │ /roadmap  │
    │         │       │             │      │           │
    │ • Stats │       │ • Coding    │      │ • Week 1-2│
    │ • Sync  │       │ • Design    │      │ • Week 3-4│
    │ • Start │       │ • Behavioral│      │ • Week 5-8│
    │ • View  │       │ • History   │      │ • Week 9-10
    └─────────┘       └─────────────┘      │ • Week 11-12
        │                    │              └───────────┘
        ▼                    ▼                       │
    
    ┌─ WEAKNESS ─┐     ┌─ TRAINING ─┐      ┌─ SYNC ──┐
    │ /weakness  │     │ /training  │      │ POST    │
    │            │     │            │      │ /sync   │
    │ • Areas    │     │ • Arrays   │      │         │
    │ • Scores   │     │ • DP       │      │ (Form)  │
    │ • Practice │     │ • Design   │      │         │
    └────────────┘     │ • Graphs   │      └─────────┘
                       └────────────┘

                    All pages link to each other
```

---

## Data Flow

```
User Input                  Processing              Output
─────────────────────────────────────────────────────────

Browser                Flask App               Database
├─ Visit /          → Dashboard.index()   → Get weaknesses
├─ Click Interview  → Dashboard.interview() → Fetch problems
├─ View Roadmap     → Dashboard.roadmap()  → Generate path
├─ Check Weakness   → Dashboard.weakness() → Query DB
├─ Study Training   → Dashboard.training() → Load modules
└─ Sync Progress    → Dashboard.sync()     → Update stats

                      ↓
                  Back to Browser
                  ├─ Render HTML
                  ├─ Apply CSS
                  ├─ Execute JS
                  └─ Display Page
```

---

## Page Component Hierarchy

```
Base Layout (Consistent across all pages)
├── Header
│   └── Title: "MAANG Mentor Dashboard"
├── Navigation Bar
│   ├── Home
│   ├── Interview
│   ├── Roadmap
│   ├── Training
│   └── Weaknesses
├── Content Area
│   └── Page-specific content
│       ├── HOME: Stats, actions, sync
│       ├── INTERVIEW: 3 modes
│       ├── ROADMAP: 12 weeks
│       ├── TRAINING: Courses
│       └── WEAKNESS: Areas, scores
└── Footer
    └── Info & status
```

---

## Interview Features Overview

```
CODING INTERVIEW
├── Difficulty: Easy ──► Medium ──► Hard
├── Problem Load: Auto
├── Editor: Browser
├── Execution: Live
├── Feedback: AI-powered
└── Scoring: 0-100%

SYSTEM DESIGN
├── Topic Input: Required
├── Whiteboard: Interactive
├── Components: 
│   ├── Architecture
│   ├── Database
│   ├── API Design
│   └── Scaling
├── Feedback: Expert
└── Recording: Optional

BEHAVIORAL
├── Questions: Generated
├── Method: STAR
│   ├── Situation
│   ├── Task
│   ├── Action
│   └── Result
├── Analysis: Detailed
└── Score: Competency-based
```

---

## User Journey

```
DAY 1: Setup
├─ Open http://localhost:5100
├─ See Home page
├─ Enter GitHub username
├─ Enter LeetCode username
├─ Click Sync Now
└─ Wait for data update

DAY 2: Explore
├─ View Home statistics
├─ Check Weakness page
├─ Review Roadmap
├─ Browse Training
└─ Decide on focus area

DAY 3+: Practice
├─ Open Interview page
├─ Select interview type
├─ Choose difficulty
├─ Complete interview
├─ Review feedback
├─ Check progress
└─ Repeat daily

WEEKLY: Review
├─ Sync GitHub/LeetCode
├─ Check overall progress
├─ Update roadmap
├─ Set next week goals
└─ Adjust strategy if needed
```

---

## State Management

```
Session State (Per User)
├── user_id
├── current_page
├── selected_difficulty
├── interview_mode
├── weakness_profile
└── progress_data

Database State (Persistent)
├── Problems
│   ├── ID, title, difficulty
│   ├── Description, test cases
│   └── Solutions, discuss
├── User Progress
│   ├── Problems solved
│   ├── Scores achieved
│   └── Topics covered
├── Interviews
│   ├── Session data
│   ├── Submissions
│   └── Feedback
└── Weaknesses
    ├── Topic name
    ├── Score (0-10)
    └── Last attempted
```

---

## Response Types

```
HOME Page (GET /)
├─ Status: 200 OK
├─ Type: HTML
├─ Components:
│   ├─ CSS styling
│   ├─ Navigation
│   ├─ Statistics
│   └─ Forms
└─ Load time: <500ms

INTERVIEW API (GET /api/interview/*)
├─ Status: 200 OK
├─ Type: JSON
├─ Content:
│   ├─ Problem details
│   ├─ Test cases
│   └─ Metadata
└─ Load time: <300ms

SYNC Handler (POST /sync)
├─ Status: 302 Redirect
├─ Action: Fetch GitHub/LeetCode
├─ Update: Database
├─ Redirect: Home page
└─ Time: 2-5 seconds

Error Handling
├─ 404: Page not found
├─ 400: Bad request
├─ 500: Server error
└─ Recovery: Auto-retry
```

---

## Browser Compatibility

```
✅ SUPPORTED
├─ Chrome 90+
├─ Firefox 88+
├─ Safari 14+
└─ Edge 90+

⚠️  LIMITED
├─ Mobile browsers: All modern
└─ Tablets: All modern

❌ NOT SUPPORTED
├─ Internet Explorer
├─ Old Android browsers
└─ Obsolete Safari versions
```

---

## CSS Styling Strategy

```
Layout
├─ Flexbox: Header, navigation
├─ Grid: Content sections, cards
└─ Responsive: @media queries

Colors
├─ Primary: #667eea (purple)
├─ Accent: #764ba2 (darker purple)
├─ Background: white (#fff)
└─ Text: dark gray (#333)

Typography
├─ Font: 'Segoe UI', sans-serif
├─ Sizes: 1em - 2.5em
├─ Weights: normal, bold
└─ Line height: 1.5

Effects
├─ Shadows: Box-shadow
├─ Transitions: 0.3s ease
├─ Transforms: scale, translate
└─ Borders: Rounded corners
```

---

## Performance Optimization

```
Frontend
├─ Inline CSS (no extra requests)
├─ Minimal JavaScript
├─ No external dependencies
├─ Cached resources
└─ Compressed responses

Backend
├─ Connection pooling
├─ Query optimization
├─ In-memory caching
├─ Async operations
└─ Rate limiting (future)

Network
├─ Local-only (fast)
├─ No external APIs (initially)
├─ Minimal payload size
└─ Efficient serialization
```

---

## Deployment Architecture

```
Host Machine (Windows)
│
├─ Docker Daemon
│  │
│  ├─ Network: maang-network
│  │
│  ├─ Container 1: dashboard (5100)
│  ├─ Container 2: adk-web (8000)
│  ├─ Container 3: mcp-server (8765)
│  └─ Container 4: sqlite-db (volume)
│
└─ Browser
   └─ http://localhost:5100
```

---

## Integration Points

```
Dashboard ←─→ Interview Routes
    ↓
Interview Routes ←─→ Simulation Engine
    ↓
Simulation Engine ←─→ Code Compiler
    ↓
Dashboard ←─→ Roadmap Generator
    ↓
Roadmap Generator ←─→ Memory/Database
    ↓
Dashboard ←─→ Tracker Module
    ↓
Tracker ←─→ GitHub/LeetCode APIs
```

---

## Feature Availability Matrix

```
Feature              Home  Interview  Roadmap  Training  Weakness
────────────────────────────────────────────────────────────────
View Stats            ✅      ○         ○         ○         ○
Start Interview       ✅      ✅        ○         ○         ✅
View Roadmap          ✅      ○         ✅        ○         ○
Sync Progress         ✅      ○         ○         ○         ○
Practice Problems     ○       ✅        ○         ✅        ✅
View Weaknesses       ✅      ○         ○         ○         ✅
Learn Topics          ○       ○         ○         ✅        ○
Track Progress        ✅      ✅        ✅        ○         ✅
Get Feedback          ○       ✅        ○         ✅        ○

✅ = Primary feature
○ = Secondary/referenced
```

---

## Success Indicators

```
✅ System Running
├─ All 4 containers active
├─ All 5 pages loading
├─ All routes responsive
└─ No error messages

✅ User Experience
├─ Page loads <1 second
├─ Buttons respond immediately
├─ Navigation smooth
└─ Text readable

✅ Features Working
├─ Interviews can start
├─ Sync fetches data
├─ Pages display correctly
└─ Forms submit data

✅ Production Ready
├─ Error handling complete
├─ No console errors
├─ No security issues
└─ Documentation complete
```

---

## 🎯 You're All Set!

Architecture: ✅ Designed  
Implementation: ✅ Complete  
Testing: ✅ Verified  
Documentation: ✅ Written  

**Status**: 🟢 **READY TO USE**

Open: http://localhost:5100
