"""
Training Dashboard Routes
Visualization of adaptive learning progress
"""

import sys
import os

# Add parent directory to path so we can import sibling packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, jsonify, request, render_template_string
import json
from training.adaptive_learning_agent import AdaptiveLearningAgent
from pathlib import Path

training_bp = Blueprint('training', __name__, url_prefix='/training')
agent = AdaptiveLearningAgent()


@training_bp.route('/progress', methods=['POST'])
def upload_progress():
    """Upload and analyze progress data"""
    try:
        data = request.get_json()
        progress_data = data.get('progress_data')
        
        if not progress_data:
            return jsonify({"error": "No progress data provided"}), 400
        
        # Analyze progress
        analysis = agent.analyze_learning_progress(progress_data)
        
        return jsonify({
            "status": "success",
            "analysis": analysis
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/plan', methods=['POST'])
def create_plan():
    """Generate personalized training plan"""
    try:
        data = request.get_json()
        progress_data = data.get('progress_data')
        duration = data.get('duration_days', 30)
        daily_target = data.get('daily_target', 5)
        
        if not progress_data:
            return jsonify({"error": "No progress data provided"}), 400
        
        analysis = agent.analyze_learning_progress(progress_data)
        plan = agent.generate_training_plan(analysis, duration, daily_target)
        
        return jsonify({
            "status": "success",
            "plan": plan
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/problem', methods=['GET'])
def get_problem():
    """Get custom problem"""
    try:
        topic = request.args.get('topic', 'arrays')
        difficulty = request.args.get('difficulty', 'medium')
        focus = request.args.get('focus')
        
        problem = agent.generate_custom_problem(topic, difficulty, focus)
        
        return jsonify({
            "status": "success",
            "problem": problem
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@training_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Training dashboard HTML"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Training Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                padding: 30px;
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
                text-align: center;
                font-size: 2.5em;
            }
            .section {
                margin-bottom: 40px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .section h2 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.5em;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #555;
            }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .progress-bar {
                width: 100%;
                height: 30px;
                background: #e0e0e0;
                border-radius: 15px;
                overflow: hidden;
                margin-top: 10px;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
                font-size: 12px;
            }
            .topic-card {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }
            .topic-card h3 {
                color: #333;
                margin-bottom: 8px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .stat-box {
                background: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            .stat-number {
                font-size: 2em;
                color: #667eea;
                font-weight: bold;
                margin: 10px 0;
            }
            .stat-label {
                color: #666;
                font-size: 14px;
            }
            .result {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid #ddd;
            }
            .result h3 {
                color: #333;
                margin-bottom: 10px;
            }
            pre {
                background: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
                overflow-x: auto;
            }
            .error {
                color: #d32f2f;
                padding: 10px;
                background: #ffebee;
                border-radius: 5px;
                margin-top: 10px;
            }
            .success {
                color: #388e3c;
                padding: 10px;
                background: #e8f5e9;
                border-radius: 5px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 AI Training Agent Dashboard</h1>
            
            <!-- Upload Progress Section -->
            <div class="section">
                <h2>📊 Analyze Your Progress</h2>
                <div class="form-group">
                    <label>Paste your TakeUForward progress JSON:</label>
                    <textarea id="progressData" rows="6" placeholder='{"success": true, "recentProgress": [...]}' style="font-family: monospace;"></textarea>
                </div>
                <button onclick="analyzeProgress()">Analyze Progress</button>
                <div id="analysisResult"></div>
            </div>
            
            <!-- Generate Plan Section -->
            <div class="section">
                <h2>📅 Generate Training Plan</h2>
                <div class="form-group">
                    <label>Duration (days):</label>
                    <input type="number" id="duration" value="30" min="7" max="90">
                </div>
                <div class="form-group">
                    <label>Daily Target (problems):</label>
                    <input type="number" id="dailyTarget" value="5" min="1" max="20">
                </div>
                <button onclick="generatePlan()">Generate Plan</button>
                <div id="planResult"></div>
            </div>
            
            <!-- Custom Problem Section -->
            <div class="section">
                <h2>🎯 Get Custom Problem</h2>
                <div class="form-group">
                    <label>Topic:</label>
                    <select id="topic">
                        <option>arrays</option>
                        <option>strings</option>
                        <option>linked-list</option>
                        <option>binary-search</option>
                        <option>recursion</option>
                        <option>hashing</option>
                        <option>sorting</option>
                        <option>dynamic-programming</option>
                        <option>graphs</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Difficulty:</label>
                    <select id="difficulty">
                        <option>easy</option>
                        <option selected>medium</option>
                        <option>hard</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Focus Area (optional):</label>
                    <input type="text" id="focus" placeholder="e.g., sliding-window">
                </div>
                <button onclick="getProblem()">Get Problem</button>
                <div id="problemResult"></div>
            </div>
            
            <!-- Statistics Section -->
            <div class="section">
                <h2>📈 Quick Stats</h2>
                <div class="stats" id="statsContainer">
                    <div class="stat-box">
                        <div class="stat-label">Total Topics</div>
                        <div class="stat-number">9</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Total Problems</div>
                        <div class="stat-number">500+</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Avg Time/Problem</div>
                        <div class="stat-number">1hr</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function analyzeProgress() {
                const progressText = document.getElementById('progressData').value;
                if (!progressText.trim()) {
                    showError('analysisResult', 'Please paste progress data');
                    return;
                }
                
                try {
                    const progressData = JSON.parse(progressText);
                    const response = await fetch('/training/progress', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({progress_data: progressData})
                    });
                    
                    const result = await response.json();
                    if (result.status === 'success') {
                        showResult('analysisResult', 'Analysis', result.analysis);
                    } else {
                        showError('analysisResult', result.error);
                    }
                } catch (e) {
                    showError('analysisResult', 'Invalid JSON format');
                }
            }
            
            async function generatePlan() {
                const progressText = document.getElementById('progressData').value;
                const duration = parseInt(document.getElementById('duration').value);
                const dailyTarget = parseInt(document.getElementById('dailyTarget').value);
                
                if (!progressText.trim()) {
                    showError('planResult', 'Please analyze progress first');
                    return;
                }
                
                try {
                    const progressData = JSON.parse(progressText);
                    const response = await fetch('/training/plan', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            progress_data: progressData,
                            duration_days: duration,
                            daily_target: dailyTarget
                        })
                    });
                    
                    const result = await response.json();
                    if (result.status === 'success') {
                        showResult('planResult', 'Training Plan', result.plan);
                    } else {
                        showError('planResult', result.error);
                    }
                } catch (e) {
                    showError('planResult', 'Invalid data');
                }
            }
            
            async function getProblem() {
                const topic = document.getElementById('topic').value;
                const difficulty = document.getElementById('difficulty').value;
                const focus = document.getElementById('focus').value;
                
                try {
                    const url = `/training/problem?topic=${topic}&difficulty=${difficulty}` +
                                (focus ? `&focus=${encodeURIComponent(focus)}` : '');
                    const response = await fetch(url);
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        showResult('problemResult', 'Problem Recommendation', result.problem);
                    } else {
                        showError('problemResult', result.error);
                    }
                } catch (e) {
                    showError('problemResult', e.message);
                }
            }
            
            function showResult(elementId, title, data) {
                const elem = document.getElementById(elementId);
                elem.innerHTML = `
                    <div class="success">✓ ${title} Generated Successfully</div>
                    <div class="result">
                        <h3>${title}</h3>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            }
            
            function showError(elementId, message) {
                const elem = document.getElementById(elementId);
                elem.innerHTML = `<div class="error">✗ Error: ${message}</div>`;
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)


# Export blueprint
__all__ = ['training_bp']
