# ui/dashboard.py
import sys
import os

# Add parent directory to path so we can import sibling packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from memory.db import init_db, get_weaknesses
import subprocess
import threading
import time
import json
from datetime import datetime, timedelta

app = Flask(__name__)
init_db()

# Try to register training blueprint if available
try:
    from training_routes import training_bp
    app.register_blueprint(training_bp)
except (ImportError, ModuleNotFoundError):
    # Training module not available, continue without it
    pass

# Try to register interview blueprint if available
try:
    from interview_routes import interview_bp, init_socketio
    app.register_blueprint(interview_bp)
    init_socketio(app)
except (ImportError, ModuleNotFoundError):
    # Interview module not available, continue without it
    pass

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
    github = request.args.get("github") or os.getenv("GITHUB_USERNAME", "")
    leetcode = request.args.get("leetcode") or os.getenv("LEETCODE_USERNAME", "")
    weaknesses = get_weaknesses()
    
    return render_template_string(
        MAIN_LAYOUT + HOME_TEMPLATE,
        github=github,
        leetcode=leetcode,
        weaknesses=weaknesses,
        total_problems=500,
        completed_problems=125,
        success_rate=78
    )

@app.route("/interview", methods=["GET"])
def interview():
    return render_template_string(MAIN_LAYOUT + INTERVIEW_TEMPLATE)

@app.route("/roadmap", methods=["GET"])
def roadmap():
    recommendations = get_recommendations()
    return render_template_string(
        MAIN_LAYOUT + ROADMAP_TEMPLATE,
        roadmap=recommendations
    )

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
    html = """
<div class="section">
    <h2>🎓 Training Mode</h2>
    <p>Learn new concepts with guided lessons and practice problems</p>
    <div class="grid">
        <div class="card">
            <h3>Arrays & Strings</h3>
            <p>Master fundamental data structures</p>
            <button class="btn">Start Training</button>
        </div>
        <div class="card">
            <h3>Dynamic Programming</h3>
            <p>Learn DP patterns and optimizations</p>
            <button class="btn">Start Training</button>
        </div>
        <div class="card">
            <h3>System Design</h3>
            <p>Design large-scale systems</p>
            <button class="btn">Start Training</button>
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)
