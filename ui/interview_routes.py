"""
Interview Routes - Flask endpoints for interview platform
Handles interview creation, management, and real-time chat
"""

from flask import Blueprint, request, jsonify, render_template
from flask_socketio import emit, join_room, leave_room, SocketIO
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import logging

from interview.simulation_engine import (
    InterviewSimulationEngine,
    InterviewMode,
    CompanyRole
)
from interview.compiler import CodeCompiler, InterviewCodeValidator
from interview.scheduler import InterviewScheduler, InterviewStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
interview_bp = Blueprint('interview', __name__, url_prefix='/api/interview')

# Global instances
engine = InterviewSimulationEngine()
compiler = CodeCompiler()
validator = InterviewCodeValidator()
scheduler = InterviewScheduler()

# Track active sessions
active_sessions: Dict[int, Dict[str, Any]] = {}
socketio = None


def init_socketio(app):
    """Initialize SocketIO for real-time communication"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect(data):
        logger.info(f"Client connected: {request.sid}")
        emit('response', {'data': 'Connected to interview server'})
    
    @socketio.on('join_session')
    def on_join(data):
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        join_room(f"session_{session_id}")
        logger.info(f"User {user_id} joined session {session_id}")
        
        # Send current interview context
        if session_id in active_sessions:
            emit('session_context', active_sessions[session_id])
    
    @socketio.on('send_message')
    def handle_message(data):
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        message = data.get('message')
        
        if session_id in active_sessions:
            # Store message
            engine.add_chat_message(session_id, user_id, 'user', message)
            
            # Broadcast to session room
            emit('message', {
                'speaker': 'user',
                'message': message,
                'timestamp': datetime.now().isoformat()
            }, room=f"session_{session_id}")
            
            logger.info(f"Message from {user_id} in session {session_id}: {message[:50]}...")
    
    @socketio.on('code_submission')
    def handle_code_submission(data):
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        code = data.get('code')
        language = data.get('language', 'python')
        
        logger.info(f"Code submission from {user_id} in {language}")
        
        # Get problem details from session
        if session_id in active_sessions:
            session = active_sessions[session_id]
            problem_id = session.get('problem_id')
            
            # Run tests
            result = engine.submit_code(session_id, user_id, code, language, 
                                       session.get('test_cases', []))
            
            # Broadcast results
            emit('submission_result', {
                'submission_id': result['submission_id'],
                'validation': result['validation'],
                'timestamp': result['timestamp']
            }, room=f"session_{session_id}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Client disconnected: {request.sid}")


# REST Routes

@interview_bp.route('/problems/<difficulty>', methods=['GET'])
def get_problems_by_difficulty(difficulty):
    """Get coding problems by difficulty"""
    try:
        problems = engine.get_coding_problems_by_difficulty(difficulty)
        return jsonify({
            'success': True,
            'difficulty': difficulty,
            'problems': problems,
            'count': len(problems)
        })
    except Exception as e:
        logger.error(f"Error fetching problems: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/problem/<problem_id>', methods=['GET'])
def get_problem(problem_id):
    """Get specific coding problem"""
    try:
        problem = engine.get_coding_problem(problem_id)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404
        
        return jsonify({
            'success': True,
            'problem': problem
        })
    except Exception as e:
        logger.error(f"Error fetching problem: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/system-design/<topic>', methods=['GET'])
def get_system_design(topic):
    """Get system design problem"""
    try:
        company_role = request.args.get('company_role')
        role_enum = None
        if company_role:
            try:
                role_enum = CompanyRole[company_role.upper()]
            except KeyError:
                pass
        
        problem = engine.get_system_design_problem(topic, role_enum)
        if not problem:
            return jsonify({'success': False, 'error': 'Topic not found'}), 404
        
        return jsonify({
            'success': True,
            'problem': problem
        })
    except Exception as e:
        logger.error(f"Error fetching system design: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/behavioral-question', methods=['GET'])
def get_behavioral():
    """Get behavioral interview question"""
    try:
        question = engine.get_behavioral_question()
        return jsonify({
            'success': True,
            'question': question
        })
    except Exception as e:
        logger.error(f"Error fetching behavioral question: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/session/create', methods=['POST'])
def create_session():
    """Create new interview session"""
    try:
        data = request.json
        user_id = data.get('user_id')
        mode = data.get('mode', 'coding')  # coding, system_design, behavioral
        company_role = data.get('company_role', 'google_sde')
        problem_id = data.get('problem_id')
        
        # Create session
        session_data = engine.create_session(
            user_id=user_id,
            mode=InterviewMode[mode.upper()],
            company_role=CompanyRole[company_role.upper()],
            problem_id=problem_id
        )
        
        session_id = session_data['session_id']
        
        # Load problem if coding interview
        problem = None
        test_cases = []
        if mode == 'coding' and problem_id:
            problem = engine.get_coding_problem(problem_id)
            if problem:
                test_cases = problem.get('test_cases', [])
        
        # Store in active sessions
        active_sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'mode': mode,
            'company_role': company_role,
            'problem_id': problem_id,
            'problem': problem,
            'test_cases': test_cases,
            'started_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        logger.info(f"Created session {session_id} for user {user_id}")
        
        return jsonify({
            'success': True,
            'session': session_data,
            'problem': problem
        })
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/session/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    try:
        if session_id not in active_sessions:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        chat_history = engine.get_chat_history(session_id)
        
        return jsonify({
            'success': True,
            'session': session,
            'chat_history': chat_history
        })
    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/session/<int:session_id>/submit-code', methods=['POST'])
def submit_code(session_id):
    """Submit code for validation"""
    try:
        if session_id not in active_sessions:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        data = request.json
        code = data.get('code')
        language = data.get('language', 'python')
        user_id = data.get('user_id')
        
        session = active_sessions[session_id]
        test_cases = session.get('test_cases', [])
        problem_id = session.get('problem_id')
        
        # Validate solution
        validation = validator.validate_solution(code, language, problem_id, test_cases)
        
        # Submit to engine
        result = engine.submit_code(session_id, user_id, code, language, test_cases)
        
        logger.info(f"Code submission in session {session_id}: {validation['metrics']['all_tests_passed']}")
        
        return jsonify({
            'success': True,
            'submission': result,
            'validation': validation
        })
    except Exception as e:
        logger.error(f"Error submitting code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/session/<int:session_id>/end', methods=['POST'])
def end_session(session_id):
    """End interview session"""
    try:
        if session_id not in active_sessions:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        data = request.json
        score = data.get('score', 0.0)
        feedback = data.get('feedback', '')
        
        # End session in engine
        result = engine.end_session(session_id, score, feedback)
        
        # Remove from active sessions
        active_sessions.pop(session_id, None)
        
        logger.info(f"Ended session {session_id} with score {score}")
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


# Scheduling Routes

@interview_bp.route('/schedule/create', methods=['POST'])
def schedule_interview():
    """Schedule new interview"""
    try:
        data = request.json
        user_id = data.get('user_id')
        mode = data.get('mode', 'coding')
        difficulty = data.get('difficulty', 'medium')
        company_role = data.get('company_role', 'google_sde')
        
        interview = scheduler.schedule_interview(
            user_id=user_id,
            mode=mode,
            difficulty=difficulty,
            company_role=company_role
        )
        
        logger.info(f"Scheduled interview for user {user_id}")
        
        return jsonify({
            'success': True,
            'interview': interview.to_dict()
        })
    except Exception as e:
        logger.error(f"Error scheduling interview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/schedule/next/<user_id>', methods=['GET'])
def get_next_interview(user_id):
    """Get next scheduled interview"""
    try:
        interview = scheduler.get_next_interview(user_id)
        
        if not interview:
            return jsonify({
                'success': True,
                'interview': None,
                'message': 'No scheduled interviews'
            })
        
        countdown = scheduler.get_interview_countdown(interview.id)
        
        return jsonify({
            'success': True,
            'interview': interview.to_dict(),
            'countdown': countdown
        })
    except Exception as e:
        logger.error(f"Error fetching next interview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/schedule/upcoming/<user_id>', methods=['GET'])
def get_upcoming(user_id):
    """Get upcoming interviews"""
    try:
        days = request.args.get('days', 30, type=int)
        interviews = scheduler.get_upcoming_interviews(user_id, days)
        
        return jsonify({
            'success': True,
            'interviews': [i.to_dict() for i in interviews],
            'count': len(interviews)
        })
    except Exception as e:
        logger.error(f"Error fetching upcoming interviews: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/schedule/<interview_id>/complete', methods=['POST'])
def complete_interview(interview_id):
    """Mark interview as completed"""
    try:
        data = request.json
        score = data.get('score', 0.0)
        feedback = data.get('feedback', '')
        
        scheduler.complete_interview(interview_id, score, feedback)
        
        logger.info(f"Completed interview {interview_id} with score {score}")
        
        return jsonify({
            'success': True,
            'message': 'Interview marked as completed'
        })
    except Exception as e:
        logger.error(f"Error completing interview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/schedule/<interview_id>/cancel', methods=['POST'])
def cancel_interview(interview_id):
    """Cancel scheduled interview"""
    try:
        reason = request.json.get('reason', '') if request.json else ''
        scheduler.cancel_interview(interview_id, reason)
        
        logger.info(f"Cancelled interview {interview_id}")
        
        return jsonify({
            'success': True,
            'message': 'Interview cancelled'
        })
    except Exception as e:
        logger.error(f"Error cancelling interview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@interview_bp.route('/schedule/friday-info', methods=['GET'])
def get_friday_info():
    """Get Friday interview information"""
    try:
        next_interview = scheduler._get_next_friday_3pm()
        countdown = (next_interview - datetime.now()).total_seconds()
        
        return jsonify({
            'success': True,
            'next_interview': next_interview.isoformat(),
            'day': 'Friday',
            'time': '3:00 PM IST',
            'countdown_seconds': int(countdown),
            'timezone': 'IST'
        })
    except Exception as e:
        logger.error(f"Error fetching Friday info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


# Health check
@interview_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'Interview service running',
        'active_sessions': len(active_sessions),
        'timestamp': datetime.now().isoformat()
    })
