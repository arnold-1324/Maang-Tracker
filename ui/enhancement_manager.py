"""
Enhanced UI Integration Module
Adds countdown timer, BST visualization, progress indicators to interview platform
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import json


class UIEnhancementManager:
    """Manages enhanced UI components and visualizations"""
    
    TARGET_DATE = datetime(2026, 3, 15)  # March 3rd week 2026
    
    def __init__(self):
        self.current_date = datetime.now()
    
    def get_countdown_data(self) -> Dict[str, Any]:
        """Calculate countdown to target date (March 2026)"""
        time_remaining = self.TARGET_DATE - self.current_date
        
        days = time_remaining.days
        seconds = time_remaining.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        weeks = days // 7
        months = days // 30
        
        return {
            'target_date': self.TARGET_DATE.isoformat(),
            'days_remaining': days,
            'weeks_remaining': weeks,
            'months_remaining': months,
            'hours_remaining': hours,
            'minutes_remaining': minutes,
            'total_seconds': int(time_remaining.total_seconds()),
            'display_string': f'{months}m {days % 30}d {hours}h',
            'percentage_complete': min(100, (self.current_date - datetime(2025, 11, 16)) / 
                                       (self.TARGET_DATE - datetime(2025, 11, 16)) * 100),
            'urgency_level': self._calculate_urgency(days)
        }
    
    def _calculate_urgency(self, days: int) -> str:
        """Determine urgency level based on days remaining"""
        if days < 30:
            return 'critical'
        elif days < 60:
            return 'high'
        elif days < 120:
            return 'medium'
        else:
            return 'low'
    
    def get_bst_visualization_html(self) -> str:
        """Generate HTML for BST visualization"""
        return '''
        <div id="bst-container" class="bst-visualization">
            <canvas id="bst-canvas" width="400" height="300"></canvas>
            <div id="bst-legend" class="bst-legend">
                <div class="legend-item">
                    <span class="color-box" style="background: #4CAF50;"></span>
                    <span>Completed (100%)</span>
                </div>
                <div class="legend-item">
                    <span class="color-box" style="background: #FFC107;"></span>
                    <span>In Progress (0-99%)</span>
                </div>
                <div class="legend-item">
                    <span class="color-box" style="background: #F44336;"></span>
                    <span>Not Started (0%)</span>
                </div>
            </div>
            <div id="bst-tooltip" class="bst-tooltip" style="display:none;">
                <div class="tooltip-content"></div>
            </div>
        </div>
        '''
    
    def get_progress_indicators_html(self, progress_data: Dict) -> str:
        """Generate HTML for progress indicators"""
        overall_percentage = progress_data.get('completion_percentage', 0)
        problems_solved = progress_data.get('solved_problems', 0)
        total_problems = progress_data.get('total_problems', 0)
        
        return f'''
        <div class="progress-section">
            <div class="progress-header">
                <h3>Overall Progress</h3>
                <span class="progress-percentage">{overall_percentage:.1f}%</span>
            </div>
            
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {overall_percentage}%">
                    <span class="progress-text">{problems_solved}/{total_problems} Problems</span>
                </div>
            </div>
            
            <div class="progress-stats">
                <div class="stat">
                    <div class="stat-value">{progress_data.get('completed_topics', 0)}</div>
                    <div class="stat-label">Topics Completed</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{progress_data.get('in_progress', 0)}</div>
                    <div class="stat-label">In Progress</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{progress_data.get('not_started', 0)}</div>
                    <div class="stat-label">Not Started</div>
                </div>
            </div>
        </div>
        '''
    
    def get_countdown_widget_html(self) -> str:
        """Generate countdown widget HTML"""
        countdown = self.get_countdown_data()
        
        # Color based on urgency
        color_map = {
            'critical': '#F44336',
            'high': '#FF9800',
            'medium': '#FFC107',
            'low': '#4CAF50'
        }
        
        color = color_map.get(countdown['urgency_level'], '#667eea')
        
        return f'''
        <div class="countdown-widget" style="border-color: {color};">
            <div class="countdown-header">
                <span class="countdown-label">Target Date</span>
                <span class="countdown-urgency" style="background: {color};">{countdown['urgency_level'].upper()}</span>
            </div>
            
            <div class="countdown-display">
                <div class="countdown-item">
                    <div class="countdown-number">{countdown['months_remaining']}</div>
                    <div class="countdown-unit">Months</div>
                </div>
                <div class="countdown-separator">:</div>
                <div class="countdown-item">
                    <div class="countdown-number">{countdown['days_remaining'] % 30}</div>
                    <div class="countdown-unit">Days</div>
                </div>
                <div class="countdown-separator">:</div>
                <div class="countdown-item">
                    <div class="countdown-number">{countdown['hours_remaining']}</div>
                    <div class="countdown-unit">Hours</div>
                </div>
            </div>
            
            <div class="countdown-progress">
                <div class="countdown-progress-bar">
                    <div class="countdown-progress-fill" style="width: {countdown['percentage_complete']}%; background: {color};"></div>
                </div>
                <span class="countdown-progress-text">{countdown['percentage_complete']:.1f}% complete</span>
            </div>
            
            <div class="countdown-target">March 15, 2026</div>
        </div>
        '''
    
    def get_daily_tasks_html(self, adaptive_problems: list) -> str:
        """Generate HTML for daily adaptive tasks"""
        tasks_html = '<div class="daily-tasks">'
        tasks_html += '<h3>Today\'s Tasks</h3>'
        
        for i, problem in enumerate(adaptive_problems, 1):
            difficulty_color = {
                'easy': '#4CAF50',
                'medium': '#FFC107',
                'hard': '#F44336'
            }.get(problem.get('difficulty', 'medium'), '#667eea')
            
            tasks_html += f'''
            <div class="task-item" style="border-left-color: {difficulty_color};">
                <div class="task-number">{i}</div>
                <div class="task-content">
                    <div class="task-title">{problem.get('title', 'Problem')}</div>
                    <div class="task-meta">
                        <span class="task-difficulty" style="background: {difficulty_color};">
                            {problem.get('difficulty', 'medium').upper()}
                        </span>
                        <span class="task-category">{problem.get('category', 'General')}</span>
                    </div>
                </div>
                <div class="task-action">
                    <button class="btn-solve" onclick="startProblem('{problem.get('problem_id')}')">
                        Solve
                    </button>
                </div>
            </div>
            '''
        
        tasks_html += '</div>'
        return tasks_html
    
    def get_enhanced_css(self) -> str:
        """Return enhanced CSS for UI components"""
        return '''
        /* Countdown Widget */
        .countdown-widget {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            margin-bottom: 20px;
        }
        
        .countdown-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .countdown-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .countdown-urgency {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
        }
        
        .countdown-display {
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .countdown-item {
            text-align: center;
        }
        
        .countdown-number {
            font-size: 2.5em;
            font-weight: bold;
            line-height: 1;
        }
        
        .countdown-unit {
            font-size: 0.8em;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .countdown-separator {
            font-size: 1.5em;
            opacity: 0.5;
            margin: 0 5px;
        }
        
        .countdown-progress {
            margin-bottom: 10px;
        }
        
        .countdown-progress-bar {
            height: 6px;
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        
        .countdown-progress-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .countdown-progress-text {
            font-size: 0.85em;
            opacity: 0.8;
        }
        
        .countdown-target {
            text-align: center;
            font-size: 0.9em;
            opacity: 0.8;
            border-top: 1px solid rgba(255,255,255,0.2);
            padding-top: 10px;
            margin-top: 10px;
        }
        
        /* Progress Indicators */
        .progress-section {
            margin: 20px 0;
        }
        
        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .progress-header h3 {
            font-size: 1.2em;
            color: #333;
        }
        
        .progress-percentage {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .progress-bar-container {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 15px;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.9em;
            font-weight: bold;
            transition: width 0.3s ease;
        }
        
        .progress-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        
        .stat {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }
        
        /* BST Visualization */
        .bst-visualization {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }
        
        .bst-legend {
            display: flex;
            gap: 15px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9em;
        }
        
        .color-box {
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }
        
        .bst-tooltip {
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            position: absolute;
            z-index: 1000;
            font-size: 0.9em;
        }
        
        /* Daily Tasks */
        .daily-tasks {
            margin: 20px 0;
        }
        
        .daily-tasks h3 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .task-item {
            display: flex;
            align-items: center;
            gap: 15px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }
        
        .task-item:hover {
            background: #e8eef7;
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
        }
        
        .task-number {
            width: 40px;
            height: 40px;
            background: #667eea;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }
        
        .task-content {
            flex: 1;
        }
        
        .task-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .task-meta {
            display: flex;
            gap: 10px;
            font-size: 0.85em;
        }
        
        .task-difficulty {
            padding: 2px 8px;
            border-radius: 4px;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .task-category {
            color: #666;
        }
        
        .btn-solve {
            padding: 8px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .btn-solve:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        '''
    
    def get_enhanced_javascript(self) -> str:
        """Return enhanced JavaScript for interactive features"""
        return '''
        <script>
        // Update countdown every second
        function updateCountdown() {
            const targetDate = new Date('2026-03-15').getTime();
            const now = new Date().getTime();
            const remaining = targetDate - now;
            
            if (remaining > 0) {
                const months = Math.floor(remaining / (1000 * 60 * 60 * 24 * 30));
                const days = Math.floor((remaining % (1000 * 60 * 60 * 24 * 30)) / (1000 * 60 * 60 * 24));
                const hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
                
                const countdownElements = document.querySelectorAll('.countdown-number');
                if (countdownElements.length >= 3) {
                    countdownElements[0].textContent = months;
                    countdownElements[1].textContent = days;
                    countdownElements[2].textContent = hours;
                }
            }
        }
        
        // Draw BST visualization
        function drawBST(data) {
            const canvas = document.getElementById('bst-canvas');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Simple tree visualization
            function drawNode(x, y, node, level) {
                if (!node) return;
                
                const radius = 15;
                const xOffset = 100 / Math.pow(2, level);
                
                // Draw node circle
                const color = node.progress >= 100 ? '#4CAF50' : 
                             node.progress > 0 ? '#FFC107' : '#F44336';
                
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(x, y, radius, 0, 2 * Math.PI);
                ctx.fill();
                
                // Draw label
                ctx.fillStyle = 'white';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.font = 'bold 10px Arial';
                ctx.fillText(Math.round(node.progress) + '%', x, y);
                
                // Draw children
                const yOffset = 50;
                if (node.left) {
                    ctx.strokeStyle = '#ccc';
                    ctx.beginPath();
                    ctx.moveTo(x, y + radius);
                    ctx.lineTo(x - xOffset, y + yOffset - radius);
                    ctx.stroke();
                    drawNode(x - xOffset, y + yOffset, node.left, level + 1);
                }
                
                if (node.right) {
                    ctx.strokeStyle = '#ccc';
                    ctx.beginPath();
                    ctx.moveTo(x, y + radius);
                    ctx.lineTo(x + xOffset, y + yOffset - radius);
                    ctx.stroke();
                    drawNode(x + xOffset, y + yOffset, node.right, level + 1);
                }
            }
            
            if (data.bst_tree && data.bst_tree.root) {
                drawNode(canvas.width / 2, 20, data.bst_tree.root, 0);
            }
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            updateCountdown();
            setInterval(updateCountdown, 60000); // Update every minute
        });
        
        // Handle task button click
        function startProblem(problemId) {
            console.log('Starting problem:', problemId);
            // Integrate with existing interview platform
            submitProblem(problemId);
        }
        </script>
        '''


def get_ui_enhancement_manager() -> UIEnhancementManager:
    """Factory function for UI enhancement manager"""
    return UIEnhancementManager()
