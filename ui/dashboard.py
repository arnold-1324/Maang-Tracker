# ui/dashboard.py
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv() # Fallback to .env

# Add parent directory to path so we can import sibling packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, send_from_directory
from memory.db import (
    init_db, create_user, authenticate_user, get_user_by_id,
    save_user_credentials, get_user_credentials, CacheManager
)
import subprocess
import threading
import time
import json
import asyncio
from datetime import datetime, timedelta
from flask_cors import CORS
from maang_agent.agent import get_mentor
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
init_db()

# Cleanup expired cache on startup
CacheManager.cleanup_expired()

# Import services
from services.auth_service import generate_token, verify_token, get_user_from_token
from services.sync_service import SyncService

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No authorization token provided"}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = get_user_from_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Add user_id to request context
        request.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function

# Try to register training blueprint if available
try:
    from dashboard.app.training.routes import training_bp
    app.register_blueprint(training_bp)
    print("[OK] Training blueprint registered successfully")
except Exception as e:
    # If the module doesn't exist yet, just log a warning
    print(f"[WARN] Warning: Training routes not available: {e}")

# Try to register interview blueprint if available
socketio_instance = None
try:
    from ui.interview_routes import interview_bp, init_socketio
    app.register_blueprint(interview_bp)
    print("[OK] Interview blueprint registered successfully")
    socketio_instance = init_socketio(app)
    if socketio_instance:
        print("[OK] SocketIO initialized successfully")
    else:
        print("[WARN] Warning: SocketIO initialization returned None")
except Exception as e:
    # Interview module not available, continue without it
    import traceback
    print(f"[WARN] Warning: Interview routes not available: {e}")
    traceback.print_exc()

from tracker.tracker import snapshot_github, snapshot_leetcode, call_mcp
from roadmap.generator import recommend as get_recommendations

# ===== HTML TEMPLATES =====

MAIN_LAYOUT = """
<!doctype html>
<html>
<head>
    <title>MAANG Mentor Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        header h1 { font-size: 2.5em; margin-bottom: 10px; }
        nav {
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #667eea;
            flex-wrap: wrap;
        }
        nav a {
            text-decoration: none;
            color: #667eea;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        nav a:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        nav a.active {
            background: #667eea;
            color: white;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 30px;
        }
        h2 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border-radius: 5px;
            text-decoration: none;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 1em;
        }
        .btn:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        .btn-secondary {
            background: #764ba2;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: inherit;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .stats {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            border: 2px solid #667eea;
        }
        .stats .number {
            font-size: 2.5em;
            color: #667eea;
            font-weight: bold;
        }
        .stats .label {
            color: #666;
            margin-top: 10px;
        }
        ul { margin-left: 20px; }
        li { margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 MAANG Mentor Dashboard</h1>
            <p>Interview Preparation Platform</p>
        </header>
        
        <nav>
            <a href="/" class="nav-link">Home</a>
            <a href="/interview" class="nav-link">Interview</a>
            <a href="/roadmap" class="nav-link">Roadmap</a>
            <a href="/training" class="nav-link">Training</a>
            <a href="/weakness" class="nav-link">Weaknesses</a>
        </nav>
        
        <div class="content">
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
"""

HOME_TEMPLATE = """
<div class="section">
    <h2>Welcome to MAANG Interview Prep</h2>
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h3 style="margin-bottom: 10px;">🎯 Target: March 2026</h3>
        <div style="font-size: 1.5em; font-weight: bold;" id="countdown-display">{{ days_remaining }} days remaining</div>
    </div>
    <div class="grid">
        <div class="stats">
            <div class="number">{{ total_problems }}</div>
            <div class="label">Total Problems</div>
        </div>
        <div class="stats">
            <div class="number">{{ completed_problems }}</div>
            <div class="label">Completed</div>
        </div>
        <div class="stats">
            <div class="number">{{ success_rate }}%</div>
            <div class="label">Success Rate</div>
        </div>
    </div>
</div>
<script>
    function updateCountdown() {
        const targetDate = new Date('2026-03-15');
        const now = new Date();
        const diff = targetDate - now;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        document.getElementById('countdown-display').textContent = 
            days + ' days, ' + hours + ' hours, ' + minutes + ' minutes remaining';
    }
    updateCountdown();
    setInterval(updateCountdown, 60000);
</script>

<div class="section">
    <h2>⚡ Quick Actions</h2>
    <div class="grid">
        <div class="card">
            <h3>Start Interview</h3>
            <p>Practice coding interviews with real-time feedback</p>
            <a href="/interview" class="btn">Start Now</a>
        </div>
        <div class="card">
            <h3>View Roadmap</h3>
            <p>Check your learning path and progress</p>
            <a href="/roadmap" class="btn">View Roadmap</a>
        </div>
        <div class="card">
            <h3>Sync Progress</h3>
            <p>Update your LeetCode and GitHub stats</p>
            <form method="post" action="/sync" style="margin: 0;">
                GitHub: <input type="text" name="github" placeholder="username" value="{{ github }}" style="width: auto; display: inline; padding: 5px;"><br>
                LeetCode: <input type="text" name="leetcode" placeholder="username" value="{{ leetcode }}" style="width: auto; display: inline; padding: 5px;"><br>
                <button type="submit" class="btn">Sync Now</button>
            </form>
        </div>
    </div>
</div>

<div class="section">
    <h2>📊 Weakness Profile</h2>
    {% if weaknesses %}
        {% for w in weaknesses %}
            <div class="card">
                <strong>{{ w.topic }}</strong> — Score: {{ w.score }}/10
                <br><small>Last seen: {{ w.last_seen }}</small>
            </div>
        {% endfor %}
    {% else %}
        <p>No weaknesses recorded yet. Start practicing to build your profile!</p>
    {% endif %}
</div>
"""

INTERVIEW_TEMPLATE = """
<div class="section">
    <h2>🎤 Interview Simulation</h2>
    <div class="grid">
        <div class="card">
            <h3>Coding Interview</h3>
            <p>Practice LeetCode-style problems with live code execution</p>
            <div style="margin-top: 10px;">
                <select id="difficulty" style="width: 100%; padding: 8px; margin: 5px 0;">
                    <option>Select Difficulty</option>
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                </select>
                <button class="btn" onclick="startCodingInterview()">Start Coding Interview</button>
            </div>
        </div>
        
        <div class="card">
            <h3>System Design</h3>
            <p>Discuss architecture and system design problems</p>
            <div style="margin-top: 10px;">
                <input type="text" id="design_topic" placeholder="Topic (e.g., URL shortener, Cache)">
                <button class="btn" onclick="startDesignInterview()">Start Design Interview</button>
            </div>
        </div>
        
        <div class="card">
            <h3>Behavioral</h3>
            <p>Practice STAR method and behavioral questions</p>
            <button class="btn" onclick="startBehavioralInterview()">Start Behavioral Interview</button>
        </div>
    </div>
</div>

<div class="section">
    <h2>📈 Recent Interviews</h2>
    <div id="recent-interviews">
        <p>Loading...</p>
    </div>
</div>

<script>
function startCodingInterview() {
    const difficulty = document.getElementById('difficulty').value;
    if (!difficulty || difficulty === 'Select Difficulty') {
        alert('Please select a difficulty');
        return;
    }
    fetch('/api/interview/problems/' + difficulty)
        .then(r => r.json())
        .then(d => {
            if (d.success && d.problems.length) {
                alert('Interview started! Problem: ' + d.problems[0].title);
                // In production, open interview editor
            }
        })
        .catch(e => alert('Error: ' + e));
}

function startDesignInterview() {
    const topic = document.getElementById('design_topic').value;
    if (!topic) {
        alert('Please enter a topic');
        return;
    }
    fetch('/api/interview/system-design/' + topic)
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                alert('System Design Interview started!');
            }
        })
        .catch(e => alert('Error: ' + e));
}

function startBehavioralInterview() {
    fetch('/api/interview/behavioral-question')
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                alert('Question: ' + d.question.question);
            }
        })
        .catch(e => alert('Error: ' + e));
}
</script>
"""

ROADMAP_TEMPLATE = """
<div class="section">
    <h2>📚 Learning Roadmap</h2>
    <p>Follow this structured path to master MAANG interview topics</p>
    
    {% if roadmap %}
        {% for rec in roadmap %}
            <div class="card">
                <strong style="color: #667eea; font-size: 1.2em;">{{ rec.topic }}</strong>
                <br>Score: {{ rec.score }}/10
                <ul>
                {% for r in rec.recommendations %}
                    <li>{{ r }}</li>
                {% endfor %}
                </ul>
            </div>
        {% endfor %}
    {% else %}
        <p>Sync your progress to see personalized recommendations.</p>
    {% endif %}
</div>

<div class="section">
    <h2>🎯 12-Week Sprint</h2>
    <div class="card">
        <h3>Week 1-2: Arrays & Strings</h3>
        <p>Master two-pointer, sliding window, and basic array operations</p>
        <progress style="width: 100%; height: 20px;" value="75" max="100"></progress>
    </div>
    <div class="card">
        <h3>Week 3-4: Trees & Graphs</h3>
        <p>Learn DFS, BFS, and tree traversals</p>
        <progress style="width: 100%; height: 20px;" value="50" max="100"></progress>
    </div>
    <div class="card">
        <h3>Week 5-8: Dynamic Programming</h3>
        <p>Solve DP problems and recognize patterns</p>
        <progress style="width: 100%; height: 20px;" value="25" max="100"></progress>
    </div>
    <div class="card">
        <h3>Week 9-10: System Design</h3>
        <p>Design scalable systems and databases</p>
        <progress style="width: 100%; height: 20px;" value="10" max="100"></progress>
    </div>
    <div class="card">
        <h3>Week 11-12: Behavioral & Review</h3>
        <p>Practice interviews and consolidate learning</p>
        <progress style="width: 100%; height: 20px;" value="5" max="100"></progress>
    </div>
</div>
"""

WEAKNESS_TEMPLATE = """
<div class="section">
    <h2>💪 Weakness Analysis</h2>
    <p>Topics where you need the most practice</p>
    
    {% if weaknesses %}
        <div class="grid">
        {% for w in weaknesses %}
            <div class="card">
                <strong style="color: #667eea;">{{ w.topic }}</strong>
                <br>Score: <span style="color: #ff6b6b; font-weight: bold;">{{ w.score }}/10</span>
                <br><small>Last attempted: {{ w.last_seen }}</small>
                <br>
                <button class="btn" style="width: 100%; margin-top: 10px; font-size: 0.9em;">Practice Now</button>
            </div>
        {% endfor %}
        </div>
    {% else %}
        <p>Complete some interviews to identify your weak areas!</p>
    {% endif %}
</div>

<div class="section">
    <h2>📈 Progress Overview</h2>
    <div class="card">
        <strong>Topics Completed:</strong> {{ completed_topics }}/{{ total_topics }}
        <progress style="width: 100%; height: 20px; margin-top: 10px;" value="{{ completed_topics }}" max="{{ total_topics }}"></progress>
    </div>
</div>
"""

# ===== ROUTES =====

@app.route("/", methods=["GET"])
def index():
    from datetime import datetime, timedelta
    github = request.args.get("github") or os.getenv("GITHUB_USERNAME", "")
    leetcode = request.args.get("leetcode") or os.getenv("LEETCODE_USERNAME", "")
    weaknesses = get_weaknesses()
    user_id = request.args.get("user_id", "default_user")
    
    # Calculate countdown to March 2026
    target_date = datetime(2026, 3, 15)
    now = datetime.now()
    days_remaining = (target_date - now).days
    
    # Get progress data if available
    try:
        from maang_agent.memory_persistence import get_memory_manager
        memory = get_memory_manager()
        summary = memory.get_user_summary(user_id)
        total_problems = summary.get('total_problems_solved', 0)
        completed_problems = total_problems
        success_rate = 78  # Could calculate from interview stats
    except:
        total_problems = 500
        completed_problems = 125
        success_rate = 78
    
    return render_template_string(
        MAIN_LAYOUT + HOME_TEMPLATE,
        github=github,
        leetcode=leetcode,
        weaknesses=weaknesses,
        total_problems=total_problems,
        completed_problems=completed_problems,
        success_rate=success_rate,
        days_remaining=days_remaining
    )

@app.route("/interview", methods=["GET"])
def interview():
    """Interview page - use template file if available"""
    from pathlib import Path
    interview_template_path = Path(__file__).parent / "templates" / "interview.html"
    if interview_template_path.exists():
        with open(interview_template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return render_template_string(MAIN_LAYOUT + INTERVIEW_TEMPLATE)

@app.route("/roadmap", methods=["GET"])
def roadmap():
    from pathlib import Path
    roadmap_template_path = Path(__file__).parent / "templates" / "roadmap.html"
    if roadmap_template_path.exists():
        with open(roadmap_template_path, 'r', encoding='utf-8') as f:
            return f.read()
    recommendations = get_recommendations()
    return render_template_string(
        MAIN_LAYOUT + ROADMAP_TEMPLATE,
        roadmap=recommendations
    )

@app.route("/api/roadmap/visualization", methods=["GET"])
def roadmap_visualization():
    """API endpoint for roadmap visualization data"""
    from roadmap.enhanced_generator import get_roadmap_generator
    user_id = request.args.get('user_id', 'default_user')
    
    generator = get_roadmap_generator(user_id)
    visualization = generator.visualize_progress()
    progress_summary = generator._get_progress_summary()
    
    return jsonify({
        'success': True,
        'visualization': {
            **visualization,
            'progress_summary': progress_summary
        }
    })

@app.route("/weakness", methods=["GET"])
def weakness():
    weaknesses = get_weaknesses()
    return render_template_string(
        MAIN_LAYOUT + WEAKNESS_TEMPLATE,
        weaknesses=weaknesses,
        completed_topics=8,
        total_topics=19
    )

@app.route("/training", methods=["GET"])
def training():
    """Training page - use blueprint route if available, otherwise fallback"""
    # Check if training blueprint is registered
    try:
        # Try to redirect to training dashboard
        from flask import redirect
        return redirect('/training/dashboard')
    except:
        # Fallback to simple template
        html = """
<div class="section">
    <h2>🎓 Training Mode</h2>
    <p>Learn new concepts with guided lessons and practice problems</p>
    <div class="grid">
        <div class="card">
            <h3>Arrays & Strings</h3>
            <p>Master fundamental data structures</p>
            <a href="/training/dashboard" class="btn">Start Training</a>
        </div>
        <div class="card">
            <h3>Dynamic Programming</h3>
            <p>Learn DP patterns and optimizations</p>
            <a href="/training/dashboard" class="btn">Start Training</a>
        </div>
        <div class="card">
            <h3>System Design</h3>
            <p>Design large-scale systems</p>
            <a href="/training/dashboard" class="btn">Start Training</a>
        </div>
    </div>
</div>
"""
        return render_template_string(MAIN_LAYOUT + html)

@app.route("/sync", methods=["POST"])
def sync():
    github_user = request.form.get("github") or os.getenv("GITHUB_TOKEN")
    leetcode_user = request.form.get("leetcode") or os.getenv("LEETCODE_USERNAME")
    
    def _worker(g, l):
        try:
            if g:
                snapshot_github(g)
            if l:
                snapshot_leetcode(l)
        except:
            pass
    
    t = threading.Thread(target=_worker, args=(github_user, leetcode_user))
    t.daemon = True
    t.start()
    
    return redirect(url_for("index", github=github_user, leetcode=leetcode_user))

@app.route("/api/integration/progress", methods=["GET"])
def unified_progress():
    """Get unified progress across all modules"""
    user_id = request.args.get('user_id', 'default_user')
    try:
        from integration.main_pipeline import get_pipeline
        pipeline = get_pipeline(user_id)
        progress = pipeline.get_unified_progress()
        return jsonify({'success': True, 'progress': progress})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route("/api/integration/sync", methods=["POST"])
def sync_modules():
    """Force sync across all modules"""
    user_id = request.json.get('user_id', 'default_user') if request.json else 'default_user'
    try:
        from integration.main_pipeline import get_pipeline
        pipeline = get_pipeline(user_id)
        result = pipeline.sync_all_modules()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route("/analyze", methods=["POST"])
def analyze():
    content = request.json
    code = content.get("code", "")
    func = content.get("func", "")
    try:
        from analyzer.complexity_analyzer import static_analysis, micro_benchmark
        static = static_analysis(code)
        micro = {}
        if func and content.get("param_gen"):
            try:
                micro = micro_benchmark(code, func, content.get("param_gen"))
            except Exception as e:
                micro = {"error": str(e)}
        return jsonify({"static": static, "micro": micro})
    except:
        return jsonify({"error": "Analyzer not available"}), 400

@app.route("/api/chat", methods=["POST"])
def chat_api():
    """Chat API for Next.js frontend"""
    data = request.json
    user_id = data.get("user_id", "default_user")
    message = data.get("message", "")
    context = data.get("context", {})
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
        
    try:
        mentor = get_mentor(user_id)
        if not mentor.current_session_id:
            mentor.start_session(
                session_id=f"session_{int(time.time())}", 
                session_type="chat", 
                context=context
            )
            
        response = mentor.process_user_input(message, context)
        return jsonify({
            "response": response,
            "session_id": mentor.current_session_id
        })
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

        return jsonify({"error": str(e)}), 500

@app.route("/api/roadmap", methods=["GET"])
def get_roadmap_api():
    """Get roadmap data for visualization"""
    user_id = request.args.get("user_id", "default_user")
    try:
        from roadmap.enhanced_generator import get_roadmap_generator
        generator = get_roadmap_generator(user_id)
        roadmap_data = generator.get_learning_roadmap(weeks=12)
        visualization = generator.visualize_progress()
        
        return jsonify({
            "success": True,
            "roadmap": roadmap_data,
            "visualization": visualization
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/roadmap/topic-details", methods=["GET"])
def get_topic_details_api():
    """Get solved problems and notes for a specific topic"""
    user_id = request.args.get("user_id", "default_user")
    topic = request.args.get("topic", "")
    
    try:
        from maang_agent.memory_persistence import get_memory_manager
        memory = get_memory_manager()
        
        # Get all mastery records
        mastery = memory.get_problem_mastery(user_id)
        
        # Filter by topic (using simple string matching or category mapping)
        # In a real app, we'd have a better mapping. For now, we'll search in problem name or category
        topic_problems = []
        
        # Mock data for demonstration if DB is empty or no matches
        if not mastery:
             # Return some mock data for UI testing
            if topic == "Two Pointers" or topic == "Arrays & Hashing":
                topic_problems = [
                    {
                        "problem_id": "two-sum",
                        "problem_name": "Two Sum",
                        "solved": True,
                        "difficulty": "Easy",
                        "starred": True,
                        "code": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        seen = {}\n        for i, num in enumerate(nums):\n            diff = target - num\n            if diff in seen:\n                return [seen[diff], i]\n            seen[num] = i",
                        "notes": "Used a hash map to store complements. Time complexity O(n), Space O(n). Key insight: x + y = target -> y = target - x.",
                        "language": "python"
                    },
                    {
                        "problem_id": "container-most-water",
                        "problem_name": "Container With Most Water",
                        "solved": True,
                        "difficulty": "Medium",
                        "starred": False,
                        "code": "class Solution:\n    def maxArea(self, height: List[int]) -> int:\n        l, r = 0, len(height) - 1\n        res = 0\n        while l < r:\n            res = max(res, min(height[l], height[r]) * (r - l))\n            if height[l] < height[r]:\n                l += 1\n            else:\n                r -= 1\n        return res",
                        "notes": "Greedy approach with two pointers moving inwards. Always move the shorter pointer because moving the taller one can only decrease the area.",
                        "language": "python"
                    },
                    {
                        "problem_id": "valid-palindrome",
                        "problem_name": "Valid Palindrome",
                        "solved": False,
                        "difficulty": "Easy",
                        "starred": False,
                        "code": "",
                        "notes": "",
                        "language": "python"
                    },
                    {
                        "problem_id": "3sum",
                        "problem_name": "3Sum",
                        "solved": False,
                        "difficulty": "Medium",
                        "starred": True,
                        "code": "",
                        "notes": "",
                        "language": "python"
                    },
                    {
                        "problem_id": "trapping-rain-water",
                        "problem_name": "Trapping Rain Water",
                        "solved": False,
                        "difficulty": "Hard",
                        "starred": False,
                        "code": "",
                        "notes": "",
                        "language": "python"
                    }
                ]
        
        return jsonify({
            "success": True,
            "topic": topic,
            "problems": topic_problems
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/compiler/run", methods=["POST"])
def run_code_api():
    """Run code with custom input"""
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "python")
    input_data = data.get("input", "")
    
    try:
        from interview.compiler import CodeCompiler
        compiler = CodeCompiler()
        result = compiler.compile_and_run(code, language, input_data, stdin_input=True)
        
        return jsonify({
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/compiler/submit", methods=["POST"])
def submit_code_api():
    """Submit code and run against test cases"""
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "python")
    problem_id = data.get("problem_id", "")
    test_cases = data.get("test_cases", [])
    
    try:
        from interview.compiler import InterviewCodeValidator
        validator = InterviewCodeValidator()
        result = validator.validate_solution(code, language, problem_id, test_cases)
        
        # If successful, update progress in memory
        if result["metrics"]["all_tests_passed"]:
            user_id = data.get("user_id", "default_user")
            from maang_agent.memory_persistence import get_memory_manager
            memory = get_memory_manager()
            # Infer category/name from problem_id or pass it in
            memory.track_problem_attempt(
                user_id=user_id,
                problem_id=problem_id,
                problem_name=data.get("problem_name", "Unknown Problem"),
                category=data.get("category", "General"),
                time_to_solve_minutes=5, # Placeholder
                optimal_solution_found=True
            )
            
        return jsonify({
            "success": True,
            "validation": result
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/progress", methods=["GET"])
def get_progress_api():
    """Get user progress analytics using RAG and AI"""
    user_id = request.args.get("user_id", "default_user")
    
    try:
        from maang_agent.memory_persistence import get_memory_manager
        from maang_agent.agent import get_mentor
        
        memory = get_memory_manager()
        
        # Get all progress data from memory
        mastery = memory.get_problem_mastery(user_id)
        topics = memory.get_topic_coverage(user_id)
        
        # Calculate metrics from real data
        total_problems = 350  # Total problems in curriculum
        solved_problems = len([m for m in mastery if m.get('optimal_solution_found')]) if mastery else 0
        
        # Count problems attempted (even if not optimally solved)
        attempted_problems = len(mastery) if mastery else 0
        
        # Calculate topic mastery
        topics_mastered = len([t for t in topics if t.get('proficiency_level', 0) >= 3]) if topics else 0
        total_topics = max(len(topics), 20) if topics else 20
        
        # Get weak and strong areas from actual data
        weak_areas = []
        strong_areas = []
        
        if topics:
            # Sort topics by proficiency
            sorted_topics = sorted(topics, key=lambda x: x.get('proficiency_level', 0))
            weak_areas = [t['topic'] for t in sorted_topics if t.get('proficiency_level', 0) < 2][:3]
            strong_areas = [t['topic'] for t in sorted(topics, key=lambda x: x.get('proficiency_level', 0), reverse=True) if t.get('proficiency_level', 0) >= 3][:3]
        
        # If no data, provide defaults
        if not weak_areas:
            weak_areas = ["Dynamic Programming", "Graph Algorithms", "Backtracking"]
        if not strong_areas:
            strong_areas = ["Arrays", "Hash Maps", "Two Pointers"]
        
        # Get AI-powered recommendations
        try:
            mentor = get_mentor(user_id)
            
            # Use RAG context to generate personalized recommendations
            rag_context = memory.get_rag_context(
                user_id=user_id,
                query="What should I focus on next in my interview preparation?",
                limit=10
            )
            
            # Build AI prompt for recommendations
            context_info = f"User has solved {solved_problems} problems, mastered {topics_mastered} topics. "
            context_info += f"Weak areas: {', '.join(weak_areas)}. Strong areas: {', '.join(strong_areas)}."
            
            recommendations = [
                f"Priority: Focus on {weak_areas[0]} - you've shown less progress here",
                f"Strengthen your {weak_areas[1] if len(weak_areas) > 1 else 'algorithmic thinking'} skills with daily practice",
                f"Maintain your strong performance in {strong_areas[0] if strong_areas else 'core topics'} with periodic review"
            ]
            
        except Exception as e:
            print(f"AI recommendation error: {e}")
            recommendations = [
                "Focus on consistency - solve at least 2 problems daily",
                "Review your weak areas before attempting new topics",
                "Practice explaining your solutions out loud"
            ]
        
        # Calculate overall mastery percentage
        overall_mastery = min(100, (solved_problems / max(1, total_problems)) * 100) if solved_problems > 0 else 0
        
        return jsonify({
            "success": True,
            "data": {
                "overall_mastery": round(overall_mastery, 1),
                "problems_solved": solved_problems,
                "total_problems": total_problems,
                "topics_mastered": topics_mastered,
                "total_topics": total_topics,
                "avg_time_per_problem": 25,  # TODO: Calculate from actual timing data
                "interview_sessions": len([m for m in mastery if m.get('interview_mode')]) if mastery else 0,
                "weak_areas": weak_areas,
                "strong_areas": strong_areas,
                "weak_areas": weak_areas,
                "strong_areas": strong_areas,
                "recommendations": recommendations,
                "recent_activity": [
                    {
                        "date": a.get('date', ''), 
                        "topic": "General Practice", # Analytics doesn't store topic per day yet
                        "problems_solved": a.get('problems_solved', 0),
                        "time_spent": a.get('time_spent_minutes', 0)
                    } for a in memory.get_progress_analytics(user_id, days=7)
                ] or [
                    { "date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), "topic": "Arrays & Hashing", "problems_solved": 3, "time_spent": 45 },
                    { "date": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), "topic": "Two Pointers", "problems_solved": 2, "time_spent": 30 },
                    { "date": (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'), "topic": "Binary Search", "problems_solved": 4, "time_spent": 60 }
                ]
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

import sys
# Add project root to path to allow importing mcp_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp_server.server import leetcode_stats, leetcode_problems, leetcode_all_solved
except ImportError:
    # Fallback or mock if import fails (e.g. missing dependencies)
    print("Could not import mcp_server.server. using mocks.")
    def leetcode_stats(username): return {}
    def leetcode_problems(tag, limit): return {}
    def leetcode_all_solved(username): return {}

@app.route("/api/roadmap/leetcode", methods=["GET"])
def get_leetcode_roadmap():
    """Get roadmap data directly from LeetCode via direct function call"""
    username = request.args.get("username") or os.getenv("LEETCODE_USERNAME") or "neal_wu"
    
    # Initialize Memory Manager
    from maang_agent.memory_persistence import AgentMemoryManager
    memory = AgentMemoryManager()
    
    # 1. Get User Stats & ALL Solved Problems (up to 1000 most recent)
    try:
        all_solved_res = leetcode_all_solved(username)
        print(f"Fetching all solved problems for: {username}")
    except Exception as e:
        print(f"Error fetching all solved problems: {e}")
        all_solved_res = {}

    solved_slugs = set()
    if all_solved_res and "data" in all_solved_res:
        submissions = all_solved_res["data"].get("recentAcSubmissionList", [])
        for sub in submissions:
            solved_slugs.add(sub["titleSlug"])
        print(f"Found {len(solved_slugs)} solved problems for {username}")
            
    # 2. Define Roadmap Topics
    topics = [
        {"id": "arrays", "name": "Arrays & Hashing", "tag": "array"},
        {"id": "two_pointers", "name": "Two Pointers", "tag": "two-pointers"},
        {"id": "stack", "name": "Stack", "tag": "stack"},
        {"id": "binary_search", "name": "Binary Search", "tag": "binary-search"},
        {"id": "sliding_window", "name": "Sliding Window", "tag": "sliding-window"},
        {"id": "linked_list", "name": "Linked List", "tag": "linked-list"},
        {"id": "trees", "name": "Trees", "tag": "tree"},
        {"id": "tries", "name": "Tries", "tag": "trie"},
        {"id": "backtracking", "name": "Backtracking", "tag": "backtracking"},
        {"id": "heap", "name": "Heap / Priority Queue", "tag": "heap"},
        {"id": "graphs", "name": "Graphs", "tag": "graph"},
        {"id": "dp_1d", "name": "1-D DP", "tag": "dynamic-programming"},
        {"id": "intervals", "name": "Intervals", "tag": "intervals"},
        {"id": "greedy", "name": "Greedy", "tag": "greedy"},
        {"id": "adv_graphs", "name": "Advanced Graphs", "tag": "adv_graphs"}, # Using 'adv_graphs' key in fallback
        {"id": "dp_2d", "name": "2-D DP", "tag": "dp_2d"}, # Using 'dp_2d' key in fallback
        {"id": "bit_manip", "name": "Bit Manipulation", "tag": "bit-manipulation"},
        {"id": "math", "name": "Math & Geometry", "tag": "math"}
    ]
    
    roadmap_data = []
    
    # Fallback data (Expanded to ~15 questions per topic for solid logic building)
    FALLBACK_PROBLEMS = {
        "array": [
            {"id": "1", "title": "Two Sum", "slug": "two-sum", "difficulty": "Easy"},
            {"id": "217", "title": "Contains Duplicate", "slug": "contains-duplicate", "difficulty": "Easy"},
            {"id": "242", "title": "Valid Anagram", "slug": "valid-anagram", "difficulty": "Easy"},
            {"id": "1929", "title": "Concatenation of Array", "slug": "concatenation-of-array", "difficulty": "Easy"},
            {"id": "1299", "title": "Replace Elements with Greatest Element on Right Side", "slug": "replace-elements-with-greatest-element-on-right-side", "difficulty": "Easy"},
            {"id": "392", "title": "Is Subsequence", "slug": "is-subsequence", "difficulty": "Easy"},
            {"id": "58", "title": "Length of Last Word", "slug": "length-of-last-word", "difficulty": "Easy"},
            {"id": "14", "title": "Longest Common Prefix", "slug": "longest-common-prefix", "difficulty": "Easy"},
            {"id": "49", "title": "Group Anagrams", "slug": "group-anagrams", "difficulty": "Medium"},
            {"id": "347", "title": "Top K Frequent Elements", "slug": "top-k-frequent-elements", "difficulty": "Medium"},
            {"id": "238", "title": "Product of Array Except Self", "slug": "product-of-array-except-self", "difficulty": "Medium"},
            {"id": "36", "title": "Valid Sudoku", "slug": "valid-sudoku", "difficulty": "Medium"},
            {"id": "128", "title": "Longest Consecutive Sequence", "slug": "longest-consecutive-sequence", "difficulty": "Medium"},
            {"id": "75", "title": "Sort Colors", "slug": "sort-colors", "difficulty": "Medium"},
            {"id": "53", "title": "Maximum Subarray", "slug": "maximum-subarray", "difficulty": "Medium"},
            {"id": "41", "title": "First Missing Positive", "slug": "first-missing-positive", "difficulty": "Hard"}
        ],
        "two-pointers": [
            {"id": "125", "title": "Valid Palindrome", "slug": "valid-palindrome", "difficulty": "Easy"},
            {"id": "680", "title": "Valid Palindrome II", "slug": "valid-palindrome-ii", "difficulty": "Easy"},
            {"id": "344", "title": "Reverse String", "slug": "reverse-string", "difficulty": "Easy"},
            {"id": "977", "title": "Squares of a Sorted Array", "slug": "squares-of-a-sorted-array", "difficulty": "Easy"},
            {"id": "283", "title": "Move Zeroes", "slug": "move-zeroes", "difficulty": "Easy"},
            {"id": "167", "title": "Two Sum II - Input Array Is Sorted", "slug": "two-sum-ii-input-array-is-sorted", "difficulty": "Medium"},
            {"id": "15", "title": "3Sum", "slug": "3sum", "difficulty": "Medium"},
            {"id": "11", "title": "Container With Most Water", "slug": "container-with-most-water", "difficulty": "Medium"},
            {"id": "189", "title": "Rotate Array", "slug": "rotate-array", "difficulty": "Medium"},
            {"id": "881", "title": "Boats to Save People", "slug": "boats-to-save-people", "difficulty": "Medium"},
            {"id": "18", "title": "4Sum", "slug": "4sum", "difficulty": "Medium"},
            {"id": "16", "title": "3Sum Closest", "slug": "3sum-closest", "difficulty": "Medium"},
            {"id": "80", "title": "Remove Duplicates from Sorted Array II", "slug": "remove-duplicates-from-sorted-array-ii", "difficulty": "Medium"},
            {"id": "1768", "title": "Merge Strings Alternately", "slug": "merge-strings-alternately", "difficulty": "Easy"},
            {"id": "42", "title": "Trapping Rain Water", "slug": "trapping-rain-water", "difficulty": "Hard"}
        ],
        "stack": [
            {"id": "20", "title": "Valid Parentheses", "slug": "valid-parentheses", "difficulty": "Easy"},
            {"id": "682", "title": "Baseball Game", "slug": "baseball-game", "difficulty": "Easy"},
            {"id": "1047", "title": "Remove All Adjacent Duplicates In String", "slug": "remove-all-adjacent-duplicates-in-string", "difficulty": "Easy"},
            {"id": "496", "title": "Next Greater Element I", "slug": "next-greater-element-i", "difficulty": "Easy"},
            {"id": "232", "title": "Implement Queue using Stacks", "slug": "implement-queue-using-stacks", "difficulty": "Easy"},
            {"id": "155", "title": "Min Stack", "slug": "min-stack", "difficulty": "Medium"},
            {"id": "150", "title": "Evaluate Reverse Polish Notation", "slug": "evaluate-reverse-polish-notation", "difficulty": "Medium"},
            {"id": "22", "title": "Generate Parentheses", "slug": "generate-parentheses", "difficulty": "Medium"},
            {"id": "739", "title": "Daily Temperatures", "slug": "daily-temperatures", "difficulty": "Medium"},
            {"id": "853", "title": "Car Fleet", "slug": "car-fleet", "difficulty": "Medium"},
            {"id": "901", "title": "Online Stock Span", "slug": "online-stock-span", "difficulty": "Medium"},
            {"id": "735", "title": "Asteroid Collision", "slug": "asteroid-collision", "difficulty": "Medium"},
            {"id": "394", "title": "Decode String", "slug": "decode-string", "difficulty": "Medium"},
            {"id": "71", "title": "Simplify Path", "slug": "simplify-path", "difficulty": "Medium"},
            {"id": "84", "title": "Largest Rectangle in Histogram", "slug": "largest-rectangle-in-histogram", "difficulty": "Hard"}
        ],
        "binary-search": [
            {"id": "704", "title": "Binary Search", "slug": "binary-search", "difficulty": "Easy"},
            {"id": "374", "title": "Guess Number Higher or Lower", "slug": "guess-number-higher-or-lower", "difficulty": "Easy"},
            {"id": "35", "title": "Search Insert Position", "slug": "search-insert-position", "difficulty": "Easy"},
            {"id": "278", "title": "First Bad Version", "slug": "first-bad-version", "difficulty": "Easy"},
            {"id": "69", "title": "Sqrt(x)", "slug": "sqrtx", "difficulty": "Easy"},
            {"id": "74", "title": "Search a 2D Matrix", "slug": "search-a-2d-matrix", "difficulty": "Medium"},
            {"id": "875", "title": "Koko Eating Bananas", "slug": "koko-eating-bananas", "difficulty": "Medium"},
            {"id": "153", "title": "Find Minimum in Rotated Sorted Array", "slug": "find-minimum-in-rotated-sorted-array", "difficulty": "Medium"},
            {"id": "33", "title": "Search in Rotated Sorted Array", "slug": "search-in-rotated-sorted-array", "difficulty": "Medium"},
            {"id": "981", "title": "Time Based Key-Value Store", "slug": "time-based-key-value-store", "difficulty": "Medium"},
            {"id": "162", "title": "Find Peak Element", "slug": "find-peak-element", "difficulty": "Medium"},
            {"id": "34", "title": "Find First and Last Position of Element in Sorted Array", "slug": "find-first-and-last-position-of-element-in-sorted-array", "difficulty": "Medium"},
            {"id": "744", "title": "Find Smallest Letter Greater Than Target", "slug": "find-smallest-letter-greater-than-target", "difficulty": "Easy"},
            {"id": "367", "title": "Valid Perfect Square", "slug": "valid-perfect-square", "difficulty": "Easy"},
            {"id": "4", "title": "Median of Two Sorted Arrays", "slug": "median-of-two-sorted-arrays", "difficulty": "Hard"}
        ],
        "sliding-window": [
            {"id": "121", "title": "Best Time to Buy and Sell Stock", "slug": "best-time-to-buy-and-sell-stock", "difficulty": "Easy"},
            {"id": "219", "title": "Contains Duplicate II", "slug": "contains-duplicate-ii", "difficulty": "Easy"},
            {"id": "1876", "title": "Substrings of Size Three with Distinct Characters", "slug": "substrings-of-size-three-with-distinct-characters", "difficulty": "Easy"},
            {"id": "643", "title": "Maximum Average Subarray I", "slug": "maximum-average-subarray-i", "difficulty": "Easy"},
            {"id": "3", "title": "Longest Substring Without Repeating Characters", "slug": "longest-substring-without-repeating-characters", "difficulty": "Medium"},
            {"id": "424", "title": "Longest Repeating Character Replacement", "slug": "longest-repeating-character-replacement", "difficulty": "Medium"},
            {"id": "567", "title": "Permutation in String", "slug": "permutation-in-string", "difficulty": "Medium"},
            {"id": "209", "title": "Minimum Size Subarray Sum", "slug": "minimum-size-subarray-sum", "difficulty": "Medium"},
            {"id": "904", "title": "Fruit Into Baskets", "slug": "fruit-into-baskets", "difficulty": "Medium"},
            {"id": "1004", "title": "Max Consecutive Ones III", "slug": "max-consecutive-ones-iii", "difficulty": "Medium"},
            {"id": "438", "title": "Find All Anagrams in a String", "slug": "find-all-anagrams-in-a-string", "difficulty": "Medium"},
            {"id": "1456", "title": "Maximum Number of Vowels in a Substring of Given Length", "slug": "maximum-number-of-vowels-in-a-substring-of-given-length", "difficulty": "Medium"},
            {"id": "1343", "title": "Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold", "slug": "number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold", "difficulty": "Medium"},
            {"id": "239", "title": "Sliding Window Maximum", "slug": "sliding-window-maximum", "difficulty": "Hard"},
            {"id": "76", "title": "Minimum Window Substring", "slug": "minimum-window-substring", "difficulty": "Hard"}
        ],
        "linked-list": [
            {"id": "206", "title": "Reverse Linked List", "slug": "reverse-linked-list", "difficulty": "Easy"},
            {"id": "21", "title": "Merge Two Sorted Lists", "slug": "merge-two-sorted-lists", "difficulty": "Easy"},
            {"id": "141", "title": "Linked List Cycle", "slug": "linked-list-cycle", "difficulty": "Easy"},
            {"id": "83", "title": "Remove Duplicates from Sorted List", "slug": "remove-duplicates-from-sorted-list", "difficulty": "Easy"},
            {"id": "234", "title": "Palindrome Linked List", "slug": "palindrome-linked-list", "difficulty": "Easy"},
            {"id": "203", "title": "Remove Linked List Elements", "slug": "remove-linked-list-elements", "difficulty": "Easy"},
            {"id": "160", "title": "Intersection of Two Linked Lists", "slug": "intersection-of-two-linked-lists", "difficulty": "Easy"},
            {"id": "876", "title": "Middle of the Linked List", "slug": "middle-of-the-linked-list", "difficulty": "Easy"},
            {"id": "143", "title": "Reorder List", "slug": "reorder-list", "difficulty": "Medium"},
            {"id": "19", "title": "Remove Nth Node From End of List", "slug": "remove-nth-node-from-end-of-list", "difficulty": "Medium"},
            {"id": "138", "title": "Copy List with Random Pointer", "slug": "copy-list-with-random-pointer", "difficulty": "Medium"},
            {"id": "2", "title": "Add Two Numbers", "slug": "add-two-numbers", "difficulty": "Medium"},
            {"id": "287", "title": "Find the Duplicate Number", "slug": "find-the-duplicate-number", "difficulty": "Medium"},
            {"id": "146", "title": "LRU Cache", "slug": "lru-cache", "difficulty": "Medium"},
            {"id": "23", "title": "Merge k Sorted Lists", "slug": "merge-k-sorted-lists", "difficulty": "Hard"}
        ],
        "tree": [
            {"id": "226", "title": "Invert Binary Tree", "slug": "invert-binary-tree", "difficulty": "Easy"},
            {"id": "104", "title": "Maximum Depth of Binary Tree", "slug": "maximum-depth-of-binary-tree", "difficulty": "Easy"},
            {"id": "543", "title": "Diameter of Binary Tree", "slug": "diameter-of-binary-tree", "difficulty": "Easy"},
            {"id": "110", "title": "Balanced Binary Tree", "slug": "balanced-binary-tree", "difficulty": "Easy"},
            {"id": "100", "title": "Same Tree", "slug": "same-tree", "difficulty": "Easy"},
            {"id": "572", "title": "Subtree of Another Tree", "slug": "subtree-of-another-tree", "difficulty": "Easy"},
            {"id": "235", "title": "Lowest Common Ancestor of a BST", "slug": "lowest-common-ancestor-of-a-binary-search-tree", "difficulty": "Medium"},
            {"id": "102", "title": "Binary Tree Level Order Traversal", "slug": "binary-tree-level-order-traversal", "difficulty": "Medium"},
            {"id": "199", "title": "Binary Tree Right Side View", "slug": "binary-tree-right-side-view", "difficulty": "Medium"},
            {"id": "1448", "title": "Count Good Nodes in Binary Tree", "slug": "count-good-nodes-in-binary-tree", "difficulty": "Medium"},
            {"id": "98", "title": "Validate Binary Search Tree", "slug": "validate-binary-search-tree", "difficulty": "Medium"},
            {"id": "230", "title": "Kth Smallest Element in a BST", "slug": "kth-smallest-element-in-a-bst", "difficulty": "Medium"},
            {"id": "105", "title": "Construct Binary Tree from Preorder and Inorder Traversal", "slug": "construct-binary-tree-from-preorder-and-inorder-traversal", "difficulty": "Medium"},
            {"id": "124", "title": "Binary Tree Maximum Path Sum", "slug": "binary-tree-maximum-path-sum", "difficulty": "Hard"},
            {"id": "297", "title": "Serialize and Deserialize Binary Tree", "slug": "serialize-and-deserialize-binary-tree", "difficulty": "Hard"}
        ],
        "trie": [
            {"id": "208", "title": "Implement Trie (Prefix Tree)", "slug": "implement-trie-prefix-tree", "difficulty": "Medium"},
            {"id": "211", "title": "Design Add and Search Words Data Structure", "slug": "design-add-and-search-words-data-structure", "difficulty": "Medium"},
            {"id": "212", "title": "Word Search II", "slug": "word-search-ii", "difficulty": "Hard"},
            {"id": "720", "title": "Longest Word in Dictionary", "slug": "longest-word-in-dictionary", "difficulty": "Medium"},
            {"id": "677", "title": "Map Sum Pairs", "slug": "map-sum-pairs", "difficulty": "Medium"},
            {"id": "648", "title": "Replace Words", "slug": "replace-words", "difficulty": "Medium"},
            {"id": "421", "title": "Maximum XOR of Two Numbers in an Array", "slug": "maximum-xor-of-two-numbers-in-an-array", "difficulty": "Medium"},
            {"id": "1268", "title": "Search Suggestions System", "slug": "search-suggestions-system", "difficulty": "Medium"},
            {"id": "1032", "title": "Stream of Characters", "slug": "stream-of-characters", "difficulty": "Hard"},
            {"id": "745", "title": "Prefix and Suffix Search", "slug": "prefix-and-suffix-search", "difficulty": "Hard"},
            {"id": "1707", "title": "Maximum XOR With an Element From Array", "slug": "maximum-xor-with-an-element-from-array", "difficulty": "Hard"},
            {"id": "336", "title": "Palindrome Pairs", "slug": "palindrome-pairs", "difficulty": "Hard"},
            {"id": "1804", "title": "Implement Trie II (Prefix Tree)", "slug": "implement-trie-ii-prefix-tree", "difficulty": "Medium"},
            {"id": "472", "title": "Concatenated Words", "slug": "concatenated-words", "difficulty": "Hard"},
            {"id": "139", "title": "Word Break", "slug": "word-break", "difficulty": "Medium"}
        ],
        "backtracking": [
            {"id": "78", "title": "Subsets", "slug": "subsets", "difficulty": "Medium"},
            {"id": "39", "title": "Combination Sum", "slug": "combination-sum", "difficulty": "Medium"},
            {"id": "46", "title": "Permutations", "slug": "permutations", "difficulty": "Medium"},
            {"id": "90", "title": "Subsets II", "slug": "subsets-ii", "difficulty": "Medium"},
            {"id": "40", "title": "Combination Sum II", "slug": "combination-sum-ii", "difficulty": "Medium"},
            {"id": "79", "title": "Word Search", "slug": "word-search", "difficulty": "Medium"},
            {"id": "131", "title": "Palindrome Partitioning", "slug": "palindrome-partitioning", "difficulty": "Medium"},
            {"id": "17", "title": "Letter Combinations of a Phone Number", "slug": "letter-combinations-of-a-phone-number", "difficulty": "Medium"},
            {"id": "51", "title": "N-Queens", "slug": "n-queens", "difficulty": "Hard"},
            {"id": "37", "title": "Sudoku Solver", "slug": "sudoku-solver", "difficulty": "Hard"},
            {"id": "77", "title": "Combinations", "slug": "combinations", "difficulty": "Medium"},
            {"id": "216", "title": "Combination Sum III", "slug": "combination-sum-iii", "difficulty": "Medium"},
            {"id": "47", "title": "Permutations II", "slug": "permutations-ii", "difficulty": "Medium"},
            {"id": "93", "title": "Restore IP Addresses", "slug": "restore-ip-addresses", "difficulty": "Medium"},
            {"id": "52", "title": "N-Queens II", "slug": "n-queens-ii", "difficulty": "Hard"}
        ],
        "heap": [
            {"id": "703", "title": "Kth Largest Element in a Stream", "slug": "kth-largest-element-in-a-stream", "difficulty": "Easy"},
            {"id": "1046", "title": "Last Stone Weight", "slug": "last-stone-weight", "difficulty": "Easy"},
            {"id": "973", "title": "K Closest Points to Origin", "slug": "k-closest-points-to-origin", "difficulty": "Medium"},
            {"id": "215", "title": "Kth Largest Element in an Array", "slug": "kth-largest-element-in-an-array", "difficulty": "Medium"},
            {"id": "621", "title": "Task Scheduler", "slug": "task-scheduler", "difficulty": "Medium"},
            {"id": "355", "title": "Design Twitter", "slug": "design-twitter", "difficulty": "Medium"},
            {"id": "295", "title": "Find Median from Data Stream", "slug": "find-median-from-data-stream", "difficulty": "Hard"},
            {"id": "23", "title": "Merge k Sorted Lists", "slug": "merge-k-sorted-lists", "difficulty": "Hard"},
            {"id": "347", "title": "Top K Frequent Elements", "slug": "top-k-frequent-elements", "difficulty": "Medium"},
            {"id": "378", "title": "Kth Smallest Element in a Sorted Matrix", "slug": "kth-smallest-element-in-a-sorted-matrix", "difficulty": "Medium"},
            {"id": "451", "title": "Sort Characters By Frequency", "slug": "sort-characters-by-frequency", "difficulty": "Medium"},
            {"id": "767", "title": "Reorganize String", "slug": "reorganize-string", "difficulty": "Medium"},
            {"id": "1337", "title": "The K Weakest Rows in a Matrix", "slug": "the-k-weakest-rows-in-a-matrix", "difficulty": "Easy"},
            {"id": "1834", "title": "Single-Threaded CPU", "slug": "single-threaded-cpu", "difficulty": "Medium"},
            {"id": "1985", "title": "Find the Kth Largest Integer in the Array", "slug": "find-the-kth-largest-integer-in-the-array", "difficulty": "Medium"}
        ],
        "intervals": [
            {"id": "57", "title": "Insert Interval", "slug": "insert-interval", "difficulty": "Medium"},
            {"id": "56", "title": "Merge Intervals", "slug": "merge-intervals", "difficulty": "Medium"},
            {"id": "435", "title": "Non-overlapping Intervals", "slug": "non-overlapping-intervals", "difficulty": "Medium"},
            {"id": "252", "title": "Meeting Rooms", "slug": "meeting-rooms", "difficulty": "Easy"},
            {"id": "253", "title": "Meeting Rooms II", "slug": "meeting-rooms-ii", "difficulty": "Medium"},
            {"id": "1851", "title": "Minimum Interval to Include Each Query", "slug": "minimum-interval-to-include-each-query", "difficulty": "Hard"},
            {"id": "228", "title": "Summary Ranges", "slug": "summary-ranges", "difficulty": "Easy"},
            {"id": "452", "title": "Minimum Number of Arrows to Burst Balloons", "slug": "minimum-number-of-arrows-to-burst-balloons", "difficulty": "Medium"},
            {"id": "1288", "title": "Remove Covered Intervals", "slug": "remove-covered-intervals", "difficulty": "Medium"},
            {"id": "986", "title": "Interval List Intersections", "slug": "interval-list-intersections", "difficulty": "Medium"},
            {"id": "729", "title": "My Calendar I", "slug": "my-calendar-i", "difficulty": "Medium"},
            {"id": "731", "title": "My Calendar II", "slug": "my-calendar-ii", "difficulty": "Medium"},
            {"id": "732", "title": "My Calendar III", "slug": "my-calendar-iii", "difficulty": "Hard"},
            {"id": "1272", "title": "Remove Interval", "slug": "remove-interval", "difficulty": "Medium"},
            {"id": "1353", "title": "Maximum Number of Events That Can Be Attended", "slug": "maximum-number-of-events-that-can-be-attended", "difficulty": "Medium"}
        ],
        "greedy": [
            {"id": "53", "title": "Maximum Subarray", "slug": "maximum-subarray", "difficulty": "Medium"},
            {"id": "55", "title": "Jump Game", "slug": "jump-game", "difficulty": "Medium"},
            {"id": "45", "title": "Jump Game II", "slug": "jump-game-ii", "difficulty": "Medium"},
            {"id": "134", "title": "Gas Station", "slug": "gas-station", "difficulty": "Medium"},
            {"id": "846", "title": "Hand of Straights", "slug": "hand-of-straights", "difficulty": "Medium"},
            {"id": "1899", "title": "Merge Triplets to Form Target Triplet", "slug": "merge-triplets-to-form-target-triplet", "difficulty": "Medium"},
            {"id": "763", "title": "Partition Labels", "slug": "partition-labels", "difficulty": "Medium"},
            {"id": "678", "title": "Valid Parenthesis String", "slug": "valid-parenthesis-string", "difficulty": "Medium"},
            {"id": "121", "title": "Best Time to Buy and Sell Stock", "slug": "best-time-to-buy-and-sell-stock", "difficulty": "Easy"},
            {"id": "122", "title": "Best Time to Buy and Sell Stock II", "slug": "best-time-to-buy-and-sell-stock-ii", "difficulty": "Medium"},
            {"id": "409", "title": "Longest Palindrome", "slug": "longest-palindrome", "difficulty": "Easy"},
            {"id": "179", "title": "Largest Number", "slug": "largest-number", "difficulty": "Medium"},
            {"id": "135", "title": "Candy", "slug": "candy", "difficulty": "Hard"},
            {"id": "334", "title": "Increasing Triplet Subsequence", "slug": "increasing-triplet-subsequence", "difficulty": "Medium"},
            {"id": "1871", "title": "Jump Game VII", "slug": "jump-game-vii", "difficulty": "Medium"}
        ],
        "adv_graphs": [
            {"id": "332", "title": "Reconstruct Itinerary", "slug": "reconstruct-itinerary", "difficulty": "Hard"},
            {"id": "1584", "title": "Min Cost to Connect All Points", "slug": "min-cost-to-connect-all-points", "difficulty": "Medium"},
            {"id": "743", "title": "Network Delay Time", "slug": "network-delay-time", "difficulty": "Medium"},
            {"id": "778", "title": "Swim in Rising Water", "slug": "swim-in-rising-water", "difficulty": "Hard"},
            {"id": "269", "title": "Alien Dictionary", "slug": "alien-dictionary", "difficulty": "Hard"},
            {"id": "787", "title": "Cheapest Flights Within K Stops", "slug": "cheapest-flights-within-k-stops", "difficulty": "Medium"},
            {"id": "1135", "title": "Connecting Cities With Minimum Cost", "slug": "connecting-cities-with-minimum-cost", "difficulty": "Medium"},
            {"id": "1192", "title": "Critical Connections in a Network", "slug": "critical-connections-in-a-network", "difficulty": "Hard"},
            {"id": "310", "title": "Minimum Height Trees", "slug": "minimum-height-trees", "difficulty": "Medium"},
            {"id": "210", "title": "Course Schedule II", "slug": "course-schedule-ii", "difficulty": "Medium"},
            {"id": "990", "title": "Satisfiability of Equality Equations", "slug": "satisfiability-of-equality-equations", "difficulty": "Medium"},
            {"id": "721", "title": "Accounts Merge", "slug": "accounts-merge", "difficulty": "Medium"},
            {"id": "802", "title": "Find Eventual Safe States", "slug": "find-eventual-safe-states", "difficulty": "Medium"},
            {"id": "127", "title": "Word Ladder", "slug": "word-ladder", "difficulty": "Hard"},
            {"id": "126", "title": "Word Ladder II", "slug": "word-ladder-ii", "difficulty": "Hard"}
        ],
        "dp_2d": [
            {"id": "62", "title": "Unique Paths", "slug": "unique-paths", "difficulty": "Medium"},
            {"id": "1143", "title": "Longest Common Subsequence", "slug": "longest-common-subsequence", "difficulty": "Medium"},
            {"id": "309", "title": "Best Time to Buy and Sell Stock with Cooldown", "slug": "best-time-to-buy-and-sell-stock-with-cooldown", "difficulty": "Medium"},
            {"id": "518", "title": "Coin Change 2", "slug": "coin-change-2", "difficulty": "Medium"},
            {"id": "494", "title": "Target Sum", "slug": "target-sum", "difficulty": "Medium"},
            {"id": "97", "title": "Interleaving String", "slug": "interleaving-string", "difficulty": "Medium"},
            {"id": "329", "title": "Longest Increasing Path in a Matrix", "slug": "longest-increasing-path-in-a-matrix", "difficulty": "Hard"},
            {"id": "115", "title": "Distinct Subsequences", "slug": "distinct-subsequences", "difficulty": "Hard"},
            {"id": "72", "title": "Edit Distance", "slug": "edit-distance", "difficulty": "Hard"},
            {"id": "312", "title": "Burst Balloons", "slug": "burst-balloons", "difficulty": "Hard"},
            {"id": "10", "title": "Regular Expression Matching", "slug": "regular-expression-matching", "difficulty": "Hard"},
            {"id": "63", "title": "Unique Paths II", "slug": "unique-paths-ii", "difficulty": "Medium"},
            {"id": "64", "title": "Minimum Path Sum", "slug": "minimum-path-sum", "difficulty": "Medium"},
            {"id": "120", "title": "Triangle", "slug": "triangle", "difficulty": "Medium"},
            {"id": "221", "title": "Maximal Square", "slug": "maximal-square", "difficulty": "Medium"}
        ],
        "bit-manipulation": [
            {"id": "136", "title": "Single Number", "slug": "single-number", "difficulty": "Easy"},
            {"id": "191", "title": "Number of 1 Bits", "slug": "number-of-1-bits", "difficulty": "Easy"},
            {"id": "338", "title": "Counting Bits", "slug": "counting-bits", "difficulty": "Easy"},
            {"id": "190", "title": "Reverse Bits", "slug": "reverse-bits", "difficulty": "Easy"},
            {"id": "268", "title": "Missing Number", "slug": "missing-number", "difficulty": "Easy"},
            {"id": "371", "title": "Sum of Two Integers", "slug": "sum-of-two-integers", "difficulty": "Medium"},
            {"id": "7", "title": "Reverse Integer", "slug": "reverse-integer", "difficulty": "Medium"},
            {"id": "231", "title": "Power of Two", "slug": "power-of-two", "difficulty": "Easy"},
            {"id": "342", "title": "Power of Four", "slug": "power-of-four", "difficulty": "Easy"},
            {"id": "1342", "title": "Number of Steps to Reduce a Number to Zero", "slug": "number-of-steps-to-reduce-a-number-to-zero", "difficulty": "Easy"},
            {"id": "461", "title": "Hamming Distance", "slug": "hamming-distance", "difficulty": "Easy"},
            {"id": "1318", "title": "Minimum Flips to Make a OR b Equal to c", "slug": "minimum-flips-to-make-a-or-b-equal-to-c", "difficulty": "Medium"},
            {"id": "201", "title": "Bitwise AND of Numbers Range", "slug": "bitwise-and-of-numbers-range", "difficulty": "Medium"},
            {"id": "137", "title": "Single Number II", "slug": "single-number-ii", "difficulty": "Medium"},
            {"id": "260", "title": "Single Number III", "slug": "single-number-iii", "difficulty": "Medium"}
        ],
        "math": [
            {"id": "202", "title": "Happy Number", "slug": "happy-number", "difficulty": "Easy"},
            {"id": "66", "title": "Plus One", "slug": "plus-one", "difficulty": "Easy"},
            {"id": "172", "title": "Factorial Trailing Zeroes", "slug": "factorial-trailing-zeroes", "difficulty": "Medium"},
            {"id": "69", "title": "Sqrt(x)", "slug": "sqrtx", "difficulty": "Easy"},
            {"id": "50", "title": "Pow(x, n)", "slug": "powx-n", "difficulty": "Medium"},
            {"id": "149", "title": "Max Points on a Line", "slug": "max-points-on-a-line", "difficulty": "Hard"},
            {"id": "43", "title": "Multiply Strings", "slug": "multiply-strings", "difficulty": "Medium"},
            {"id": "204", "title": "Count Primes", "slug": "count-primes", "difficulty": "Medium"},
            {"id": "48", "title": "Rotate Image", "slug": "rotate-image", "difficulty": "Medium"},
            {"id": "54", "title": "Spiral Matrix", "slug": "spiral-matrix", "difficulty": "Medium"},
            {"id": "73", "title": "Set Matrix Zeroes", "slug": "set-matrix-zeroes", "difficulty": "Medium"},
            {"id": "9", "title": "Palindrome Number", "slug": "palindrome-number", "difficulty": "Easy"},
            {"id": "12", "title": "Integer to Roman", "slug": "integer-to-roman", "difficulty": "Medium"},
            {"id": "13", "title": "Roman to Integer", "slug": "roman-to-integer", "difficulty": "Easy"},
            {"id": "1523", "title": "Count Odd Numbers in an Interval Range", "slug": "count-odd-numbers-in-an-interval-range", "difficulty": "Easy"}
        ],
        "dynamic-programming": [
            {"id": "70", "title": "Climbing Stairs", "slug": "climbing-stairs", "difficulty": "Easy"},
            {"id": "746", "title": "Min Cost Climbing Stairs", "slug": "min-cost-climbing-stairs", "difficulty": "Easy"},
            {"id": "198", "title": "House Robber", "slug": "house-robber", "difficulty": "Medium"},
            {"id": "213", "title": "House Robber II", "slug": "house-robber-ii", "difficulty": "Medium"},
            {"id": "5", "title": "Longest Palindromic Substring", "slug": "longest-palindromic-substring", "difficulty": "Medium"},
            {"id": "647", "title": "Palindromic Substrings", "slug": "palindromic-substrings", "difficulty": "Medium"},
            {"id": "91", "title": "Decode Ways", "slug": "decode-ways", "difficulty": "Medium"},
            {"id": "322", "title": "Coin Change", "slug": "coin-change", "difficulty": "Medium"},
            {"id": "152", "title": "Maximum Product Subarray", "slug": "maximum-product-subarray", "difficulty": "Medium"},
            {"id": "139", "title": "Word Break", "slug": "word-break", "difficulty": "Medium"},
            {"id": "300", "title": "Longest Increasing Subsequence", "slug": "longest-increasing-subsequence", "difficulty": "Medium"},
            {"id": "416", "title": "Partition Equal Subset Sum", "slug": "partition-equal-subset-sum", "difficulty": "Medium"},
            {"id": "62", "title": "Unique Paths", "slug": "unique-paths", "difficulty": "Medium"},
            {"id": "1143", "title": "Longest Common Subsequence", "slug": "longest-common-subsequence", "difficulty": "Medium"},
            {"id": "309", "title": "Best Time to Buy and Sell Stock with Cooldown", "slug": "best-time-to-buy-and-sell-stock-with-cooldown", "difficulty": "Medium"}
        ],
        "graph": [
            {"id": "200", "title": "Number of Islands", "slug": "number-of-islands", "difficulty": "Medium"},
            {"id": "695", "title": "Max Area of Island", "slug": "max-area-of-island", "difficulty": "Medium"},
            {"id": "133", "title": "Clone Graph", "slug": "clone-graph", "difficulty": "Medium"},
            {"id": "286", "title": "Walls and Gates", "slug": "walls-and-gates", "difficulty": "Medium"},
            {"id": "994", "title": "Rotting Oranges", "slug": "rotting-oranges", "difficulty": "Medium"},
            {"id": "417", "title": "Pacific Atlantic Water Flow", "slug": "pacific-atlantic-water-flow", "difficulty": "Medium"},
            {"id": "130", "title": "Surrounded Regions", "slug": "surrounded-regions", "difficulty": "Medium"},
            {"id": "207", "title": "Course Schedule", "slug": "course-schedule", "difficulty": "Medium"},
            {"id": "210", "title": "Course Schedule II", "slug": "course-schedule-ii", "difficulty": "Medium"},
            {"id": "261", "title": "Graph Valid Tree", "slug": "graph-valid-tree", "difficulty": "Medium"},
            {"id": "323", "title": "Number of Connected Components in an Undirected Graph", "slug": "number-of-connected-components-in-an-undirected-graph", "difficulty": "Medium"},
            {"id": "684", "title": "Redundant Connection", "slug": "redundant-connection", "difficulty": "Medium"},
            {"id": "127", "title": "Word Ladder", "slug": "word-ladder", "difficulty": "Hard"},
            {"id": "743", "title": "Network Delay Time", "slug": "network-delay-time", "difficulty": "Medium"},
            {"id": "787", "title": "Cheapest Flights Within K Stops", "slug": "cheapest-flights-within-k-stops", "difficulty": "Medium"}
        ]
    }
    
    # 3. Fetch roadmap data (Try DB first, then Fallback)
    db_data = memory.get_roadmap_data()
    
    # Check if DB has valid data (at least one topic with problems)
    has_valid_db_data = False
    if db_data and db_data.get("roadmap"):
        for t in db_data["roadmap"]:
            if t.get("problems") and len(t["problems"]) > 0:
                has_valid_db_data = True
                break
    
    if has_valid_db_data:
        print("Using roadmap data from Database.")
        roadmap_data = db_data["roadmap"]
    else:
        # If DB is empty or invalid, use fallback data and store it
        print("Database empty or incomplete. Initializing roadmap data from Fallback...")
        roadmap_data = []
        
        # Prepare data for storage
        problems_by_tag = FALLBACK_PROBLEMS
        
        # Store in DB
        try:
            memory.store_roadmap_data(topics, problems_by_tag)
            print("Stored roadmap data in DB.")
        except Exception as e:
            print(f"Error storing roadmap data: {e}")
        
        # Construct response structure from fallback
        for topic in topics:
            problems = []
            fallback_list = FALLBACK_PROBLEMS.get(topic["tag"], [])
            for q in fallback_list:
                problems.append({
                    "id": q["id"],
                    "title": q["title"],
                    "slug": q["slug"],
                    "difficulty": q["difficulty"],
                    "url": f"https://leetcode.com/problems/{q['slug']}/",
                    "solved": False
                })
            
            roadmap_data.append({
                "topicId": topic["id"],
                "title": topic["name"],
                "tag": topic["tag"],
                "totalProblems": len(problems),
                "solvedProblems": 0,
                "problems": problems
            })

    # 4. Update with User Progress (Solved Status)
    for topic_data in roadmap_data:
        # Try to fetch live data if needed, but primarily rely on DB + Solved Status
        # (Optional: You could still try to fetch new problems from LeetCode here and update DB)
        
        problems = topic_data["problems"]
        solved_count = 0
        
        for p in problems:
            is_solved = p["slug"] in solved_slugs
            p["solved"] = is_solved
            if is_solved:
                solved_count += 1
        
        topic_data["solvedProblems"] = solved_count
        topic_data["totalProblems"] = len(problems)
        
    return jsonify({
        "success": True,
        "username": username,
        "roadmap": roadmap_data
    })

@app.route("/api/weakness", methods=["GET"])
def get_weakness_api():
    """Get weakness analysis"""
    try:
        return jsonify({"success": True, "weaknesses": []})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Training / Resources API ---

@app.route('/api/training/resources', methods=['GET'])
def get_training_resources():
    from maang_agent.memory_persistence import AgentMemoryManager
    memory = AgentMemoryManager()
    
    # Get progress from DB
    progress_list = memory.get_training_progress()
    progress_map = {p['resource_id']: p for p in progress_list}
    
    resources = []
    
    # 1. DSA (Notion)
    dsa_resource = {
        "id": "dsa_notion",
        "title": "Data Structures and Algorithms (Notion)",
        "type": "dsa",
        "url": "https://www.notion.so/Data-Structures-and-Algorithms-2b168fc54025814592a3f9267989f9b1?source=copy_link",
        "status": progress_map.get("dsa_notion", {}).get("status", "Not Started")
    }
    resources.append(dsa_resource)
    
    # 2. System Design (userData files - filtered list)
    allowed_books = [
        "Cracking-the-Coding-Interview-6th-Edition-189-Programming-Questions-and-Solutions.pdf",
        "competitive.programming.3rd.edition.pdf",
        "Designing Data Intensive Applications by Martin Kleppmann.pdf",
        "System Design Interview by Alex Xu.pdf",
        "System-Design-Alex-Xu-Vol-2.pdf"
    ]
    
    user_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "userData")
    if os.path.exists(user_data_dir):
        for filename in os.listdir(user_data_dir):
            if filename in allowed_books:
                res_id = f"sys_design_{filename}"
                resources.append({
                    "id": res_id,
                    "title": filename.replace('.pdf', '').replace('-', ' '),
                    "type": "system_design",
                    "filename": filename,
                    "url": f"http://localhost:5100/userdata/{filename}",
                    "status": progress_map.get(res_id, {}).get("status", "Not Started")
                })
    
    return jsonify({"success": True, "resources": resources})


# ===== AUTHENTICATION ENDPOINTS =====

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400
    
    user_id = create_user(email, password, full_name)
    if not user_id:
        return jsonify({"success": False, "error": "User already exists"}), 409
    
    # Generate token
    token = generate_token(user_id, email)
    
    return jsonify({
        "success": True,
        "token": token,
        "user": {"id": user_id, "email": email, "full_name": full_name}
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400
    
    user = authenticate_user(email, password)
    if not user:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    
    # Generate token
    token = generate_token(user['id'], user['email'])
    
    return jsonify({
        "success": True,
        "token": token,
        "user": user
    })

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info"""
    user = get_user_by_id(request.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"success": True, "user": user})

# ===== PLATFORM CREDENTIALS =====

@app.route('/api/credentials/leetcode', methods=['POST'])
@require_auth
def save_leetcode_credentials():
    """Save LeetCode credentials and authenticate"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    
    # Authenticate with LeetCode
    result = call_mcp("leetcode_login", {"username": username, "password": password})
    
    if not result.get("ok"):
        return jsonify({"success": False, "error": result.get("error", "Authentication failed")}), 401
    
    session = result.get("session")
    
    # Save credentials
    save_user_credentials(
        user_id=request.user_id,
        platform='leetcode',
        username=username,
        session_cookie=session
    )
    
    # Invalidate cache
    CacheManager.invalidate_user(request.user_id)
    
    return jsonify({"success": True, "message": "LeetCode credentials saved successfully"})

@app.route('/api/credentials/github', methods=['POST'])
@require_auth
def save_github_credentials():
    """Save GitHub credentials"""
    data = request.json
    username = data.get('username')
    token = data.get('token')
    
    if not username:
        return jsonify({"success": False, "error": "Username required"}), 400
    
    save_user_credentials(
        user_id=request.user_id,
        platform='github',
        username=username,
        encrypted_token=token
    )
    
    CacheManager.invalidate_user(request.user_id)
    
    return jsonify({"success": True, "message": "GitHub credentials saved successfully"})

# ===== OPTIMIZED SYNC ENDPOINTS =====

@app.route('/api/sync/leetcode', methods=['POST'])
@require_auth
def sync_leetcode():
    """Sync LeetCode data with intelligent caching"""
    force_refresh = request.json.get('force_refresh', False) if request.json else False
    
    # Run async sync
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(SyncService.sync_leetcode_data(request.user_id, force_refresh))
    loop.close()
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/sync/github', methods=['POST'])
@require_auth
def sync_github():
    """Sync GitHub data with intelligent caching"""
    force_refresh = request.json.get('force_refresh', False) if request.json else False
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(SyncService.sync_github_data(request.user_id, force_refresh))
    loop.close()
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/sync/all', methods=['POST'])
@require_auth
def sync_all():
    """
    Full sync of all platforms with parallel processing
    This is the innovative refresh button endpoint
    """
    force_refresh = request.json.get('force_refresh', False) if request.json else False
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(SyncService.full_sync(request.user_id, force_refresh))
    loop.close()
    
    return jsonify({
        "success": True,
        "data": result,
        "message": "All platforms synced successfully"
    })

@app.route('/api/weaknesses', methods=['GET'])
@require_auth
def api_get_weaknesses():
    """Get AI-analyzed weaknesses for current user"""
    from memory.db import get_user_weaknesses
    weaknesses = get_user_weaknesses(request.user_id)
    return jsonify({"success": True, "weaknesses": weaknesses})

@app.route('/api/user/progress', methods=['GET'])
@require_auth
def api_get_user_progress():
    """Get user progress across all topics"""
    from memory.db import get_user_progress
    progress = get_user_progress(request.user_id)
    return jsonify({"success": True, "progress": progress})

# ===== CACHE MANAGEMENT =====

@app.route('/api/cache/clear', methods=['POST'])
@require_auth
def clear_user_cache():
    """Clear all cache for current user"""
    CacheManager.invalidate_user(request.user_id)
    return jsonify({"success": True, "message": "Cache cleared successfully"})

@app.route('/api/training/progress', methods=['POST'])
def update_training_progress():
    data = request.json
    resource_id = data.get('resource_id')
    title = data.get('title')
    res_type = data.get('type')
    status = data.get('status')
    
    from maang_agent.memory_persistence import AgentMemoryManager
    memory = AgentMemoryManager()
    memory.update_training_progress(resource_id, title, res_type, status)
    
    return jsonify({"success": True})

@app.route('/userdata/<path:filename>')
def serve_userdata(filename):
    user_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "userData")
    return send_from_directory(user_data_dir, filename)

@app.route('/api/training/notes', methods=['POST'])
def save_note():
    data = request.json
    from maang_agent.memory_persistence import AgentMemoryManager
    memory = AgentMemoryManager()
    note_id = memory.save_reading_note(
        data.get('resource_id'),
        data.get('page_number', 0),
        data.get('note_type', 'note'),
        data.get('content', '')
    )
    return jsonify({"success": True, "note_id": note_id})

@app.route('/api/training/notes/<resource_id>', methods=['GET'])
def get_notes(resource_id):
    from maang_agent.memory_persistence import AgentMemoryManager
    memory = AgentMemoryManager()
    notes = memory.get_reading_notes(resource_id)
    return jsonify({"success": True, "notes": notes})

@app.route('/api/leetcode-auth', methods=['POST'])
def leetcode_auth():
    """Authenticate with LeetCode and store session"""
    from memory.db import set_setting
    from tracker.tracker import call_mcp
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    
    # Call MCP login tool
    result = call_mcp("leetcode_login", {"username": username, "password": password})
    
    if result.get("ok"):
        session = result.get("session")
        # Store the session and username
        set_setting('leetcode_user', username)
        set_setting('leetcode_session', session)
        return jsonify({"success": True, "message": "Successfully authenticated with LeetCode"})
    else:
        return jsonify({"success": False, "error": result.get("error", "Authentication failed")}), 401

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    from memory.db import get_setting, set_setting
    if request.method == 'POST':
        data = request.json
        if 'leetcode_user' in data: set_setting('leetcode_user', data['leetcode_user'])
        if 'github_user' in data: set_setting('github_user', data['github_user'])
        if 'leetcode_session' in data: set_setting('leetcode_session', data['leetcode_session'])
        if 'github_token' in data: set_setting('github_token', data['github_token'])
        return jsonify({"success": True})
    else:
        return jsonify({
            "leetcode_user": get_setting('leetcode_user', os.getenv("LEETCODE_USERNAME", "")),
            "github_user": get_setting('github_user', os.getenv("GITHUB_USERNAME", "")),
            # Return empty string for secrets to avoid exposing them, but indicate if set
            "leetcode_session_set": bool(get_setting('leetcode_session')),
            "github_token_set": bool(get_setting('github_token'))
        })

@app.route('/api/sync-stats', methods=['POST', 'GET'])
def sync_stats():
    from memory.db import get_setting
    # Prioritize DB setting, fallback to env, then default
    lc_user = get_setting('leetcode_user', os.getenv("LEETCODE_USERNAME", "arnold-1324"))
    gh_user = get_setting('github_user', os.getenv("GITHUB_USERNAME", "arnold-1324"))
    
    lc_session = get_setting('leetcode_session')
    gh_token = get_setting('github_token')
    
    try:
        # Use the imported snapshot functions with auth
        lc_res = snapshot_leetcode(lc_user, lc_session)
        gh_res = snapshot_github(gh_user, gh_token)
        return jsonify({
            "success": True,
            "leetcode": lc_res,
            "github": gh_res
        })
    except Exception as e:
        print(f"Error syncing stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Use SocketIO if available, otherwise use regular Flask app
    if socketio_instance:
        socketio_instance.run(app, host="0.0.0.0", port=5100, debug=True)
    else:
        app.run(host="0.0.0.0", port=5100, debug=True)
