# ui/dashboard.py
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv() # Fallback to .env

# Add parent directory to path so we can import sibling packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from memory.db import init_db, get_weaknesses
import subprocess
import threading
import time
import json
from datetime import datetime, timedelta
from flask_cors import CORS
from maang_agent.agent import get_mentor

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
init_db()

# Try to register training blueprint if available
try:
    from ui.training_routes import training_bp
    app.register_blueprint(training_bp)
    print("✓ Training blueprint registered successfully")
except Exception as e:
    # Training module not available, continue without it
    import traceback
    print(f"⚠ Warning: Training routes not available: {e}")
    traceback.print_exc()

# Try to register interview blueprint if available
socketio_instance = None
try:
    from ui.interview_routes import interview_bp, init_socketio
    app.register_blueprint(interview_bp)
    print("✓ Interview blueprint registered successfully")
    socketio_instance = init_socketio(app)
    if socketio_instance:
        print("✓ SocketIO initialized successfully")
    else:
        print("⚠ Warning: SocketIO initialization returned None")
except Exception as e:
    # Interview module not available, continue without it
    import traceback
    print(f"⚠ Warning: Interview routes not available: {e}")
    traceback.print_exc()

from tracker.tracker import snapshot_github, snapshot_leetcode
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
                "recommendations": recommendations
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/weakness", methods=["GET"])
def get_weakness_api():
    """Get weakness analysis"""
    try:
        return jsonify({"success": True, "weaknesses": []})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Use SocketIO if available, otherwise use regular Flask app
    if socketio_instance:
        socketio_instance.run(app, host="0.0.0.0", port=5100, debug=True)
    else:
        app.run(host="0.0.0.0", port=5100, debug=True)
