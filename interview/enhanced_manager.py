"""
Enhanced Interview Simulation with Memory Integration and AI Feedback
Integrates compiler, scheduler, and memory persistence for comprehensive interview experience
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

from interview.simulation_engine import InterviewSimulationEngine, InterviewMode, CompanyRole
from interview.compiler import CodeCompiler
from interview.scheduler import InterviewScheduler
from maang_agent.memory_persistence import get_memory_manager
from maang_agent.agent import get_mentor


class WhiteboardMode(Enum):
    """System design whiteboard modes"""
    ARCHITECTURE = "architecture"
    DATABASE_SCHEMA = "database_schema"
    API_DESIGN = "api_design"
    DEPLOYMENT = "deployment"


class EnhancedInterviewManager:
    """Enhanced interview manager with AI agent integration and memory persistence"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.engine = InterviewSimulationEngine()
        self.compiler = CodeCompiler()
        self.scheduler = InterviewScheduler()
        self.memory_manager = get_memory_manager()
        self.mentor = get_mentor(user_id)
        self.current_session = None
        self.whiteboard_state = {}
    
    # ==================== Coding Interview Flow ====================
    
    def start_coding_interview(
        self,
        difficulty: str = "medium",
        company_role: str = "google_sde",
        custom_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a coding interview session"""
        
        # Create session
        session = self.engine.create_session(
            self.user_id,
            InterviewMode.CODING,
            company_role=company_role,
            problem_id=None
        )
        self.current_session = session
        
        # Get problem based on difficulty
        problem = self.engine.get_coding_problem(difficulty)
        
        # Initialize mentor session
        self.mentor.start_session(
            session_id=session.id,
            session_type='coding',
            context={
                'difficulty': difficulty,
                'company': company_role,
                'problem_id': problem.id,
                'problem_title': problem.title
            }
        )
        
        # Store in memory
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session.id,
            role='system',
            message=f'Coding interview started: {problem.title}',
            metadata={
                'problem_id': problem.id,
                'difficulty': difficulty,
                'company': company_role
            }
        )
        
        return {
            'session_id': session.id,
            'problem': {
                'id': problem.id,
                'title': problem.title,
                'description': problem.description,
                'difficulty': problem.difficulty,
                'time_limit_minutes': problem.time_limit_minutes,
                'examples': problem.examples,
                'constraints': problem.constraints
            },
            'custom_input': custom_input,
            'start_time': datetime.now().isoformat()
        }
    
    def submit_code(
        self,
        session_id: str,
        code: str,
        language: str,
        test_inputs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Submit code with compilation and testing"""
        
        # Store submission
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='user',
            message=f'Code submitted in {language}',
            metadata={'code_length': len(code), 'language': language}
        )
        
        # Compile and run
        compile_result = self.compiler.compile_and_run(code, language)
        
        if not compile_result.success:
            # Store error
            self.memory_manager.store_conversation(
                user_id=self.user_id,
                session_id=session_id,
                role='assistant',
                message=f'Compilation error: {compile_result.error}'
            )
            return {
                'success': False,
                'error': compile_result.error,
                'execution_time_ms': compile_result.execution_time_ms
            }
        
        # Test against cases
        problem = self.engine.get_coding_problem()  # Retrieve current problem
        test_results = self.compiler.test_against_cases(code, language, problem.test_cases)
        
        # Analyze code quality
        complexity = self.compiler.analyze_code_complexity(code)
        
        # Generate AI feedback
        feedback = self._generate_coding_feedback(
            code, 
            test_results, 
            complexity, 
            compile_result
        )
        
        # Store feedback in memory
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='assistant',
            message=feedback['message'],
            metadata={
                'test_results': test_results,
                'complexity': complexity.__dict__,
                'optimization_suggestions': feedback['suggestions']
            }
        )
        
        return {
            'success': True,
            'test_results': test_results,
            'execution_time_ms': compile_result.execution_time_ms,
            'output': compile_result.output,
            'complexity_analysis': complexity.__dict__,
            'ai_feedback': feedback,
            'optimization_score': self._calculate_optimization_score(complexity, test_results)
        }
    
    def _generate_coding_feedback(
        self,
        code: str,
        test_results: Dict,
        complexity: Any,
        compile_result: Any
    ) -> Dict[str, Any]:
        """Generate AI interviewer feedback on code"""
        
        passed = test_results.get('passed_count', 0)
        total = test_results.get('total_count', 0)
        
        message_parts = []
        suggestions = []
        
        if passed == total:
            message_parts.append("✅ All test cases passed! ")
        else:
            message_parts.append(f"⚠️  {passed}/{total} test cases passed. ")
        
        # Complexity feedback
        if complexity.nested_loops >= 3:
            message_parts.append("Your solution has deep nesting. ")
            suggestions.append("Consider reducing nested loops with data structures like hash maps")
        
        if complexity.recursion_detected:
            message_parts.append("Recursion detected. ")
            suggestions.append("Verify stack depth and consider iterative approach if recursion is deep")
        
        if complexity.sorting_detected:
            message_parts.append("Your solution uses sorting. ")
            suggestions.append("Verify if sorting is necessary or if a hash map approach is better")
        
        message_parts.append(f"Execution time: {compile_result.execution_time_ms}ms. ")
        
        # Edge cases check
        if passed == total:
            message_parts.append("Consider edge cases for follow-up improvements.")
        
        return {
            'message': ''.join(message_parts),
            'passed': passed,
            'total': total,
            'suggestions': suggestions,
            'areas_for_improvement': self._identify_improvement_areas(code, complexity)
        }
    
    def _calculate_optimization_score(self, complexity: Any, test_results: Dict) -> float:
        """Calculate optimization score (0-100)"""
        score = 100.0
        
        # Deduct for test failures
        if test_results.get('passed_count', 0) < test_results.get('total_count', 1):
            score -= 20
        
        # Deduct for complexity issues
        if complexity.nested_loops >= 3:
            score -= 15
        elif complexity.nested_loops == 2:
            score -= 10
        
        # Bonus for optimal solutions
        if complexity.nested_loops <= 1 and not complexity.sorting_detected:
            score += 10
        
        return max(0, min(100, score))
    
    def _identify_improvement_areas(self, code: str, complexity: Any) -> List[str]:
        """Identify areas for code improvement"""
        areas = []
        
        if len(code) > 500:
            areas.append("Code length: Consider refactoring into helper functions")
        
        if complexity.nested_loops >= 2:
            areas.append("Nested loops: Explore O(n) or O(n log n) solutions")
        
        if not complexity.hash_maps_detected:
            areas.append("Hash maps: Consider for O(1) lookups")
        
        return areas
    
    # ==================== System Design Interview Flow ====================
    
    def start_system_design_interview(
        self,
        topic: str = "url_shortener",
        company_role: str = "google_sde"
    ) -> Dict[str, Any]:
        """Start a system design interview"""
        
        session = self.engine.create_session(
            self.user_id,
            InterviewMode.SYSTEM_DESIGN,
            company_role=company_role
        )
        self.current_session = session
        
        design_topic = self.engine.get_system_design_topic(topic)
        
        self.mentor.start_session(
            session_id=session.id,
            session_type='system_design',
            context={
                'topic': topic,
                'company': company_role
            }
        )
        
        # Initialize whiteboard
        self.whiteboard_state = {
            'topic': topic,
            'components': [],
            'database_schema': {},
            'api_endpoints': [],
            'deployment_strategy': None
        }
        
        return {
            'session_id': session.id,
            'topic': design_topic.title,
            'requirements': design_topic.requirements,
            'discussion_points': design_topic.discussion_points,
            'company_specific_guidance': design_topic.company_specific_guidance.get(
                company_role, 
                {}
            ),
            'whiteboard_ready': True
        }
    
    def update_whiteboard(
        self,
        session_id: str,
        mode: WhiteboardMode,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update system design whiteboard"""
        
        self.whiteboard_state[mode.value] = content
        
        # Store in memory
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='user',
            message=f'Updated {mode.value}',
            metadata={'content': content}
        )
        
        # Generate feedback
        feedback = self._analyze_design(mode, content)
        
        return {
            'updated': True,
            'feedback': feedback,
            'whiteboard_state': self.whiteboard_state
        }
    
    def _analyze_design(self, mode: WhiteboardMode, content: Dict) -> str:
        """Analyze system design decisions"""
        feedback_messages = {
            WhiteboardMode.ARCHITECTURE: "Consider scalability: Can this handle 1M+ requests/sec?",
            WhiteboardMode.DATABASE_SCHEMA: "Verify normalization and indexing strategies.",
            WhiteboardMode.API_DESIGN: "Ensure RESTful principles and rate limiting.",
            WhiteboardMode.DEPLOYMENT: "Consider multi-region, CDN, and disaster recovery."
        }
        
        return feedback_messages.get(mode, "Good design decision.")
    
    # ==================== Behavioral Interview Flow ====================
    
    def start_behavioral_interview(
        self,
        company_role: str = "google_sde"
    ) -> Dict[str, Any]:
        """Start a behavioral interview"""
        
        session = self.engine.create_session(
            self.user_id,
            InterviewMode.BEHAVIORAL,
            company_role=company_role
        )
        self.current_session = session
        
        question = self.engine.get_behavioral_question()
        
        self.mentor.start_session(
            session_id=session.id,
            session_type='behavioral',
            context={'company': company_role}
        )
        
        return {
            'session_id': session.id,
            'question': question.question,
            'category': question.category,
            'tips': question.tips
        }
    
    def submit_behavioral_response(
        self,
        session_id: str,
        response: str
    ) -> Dict[str, Any]:
        """Evaluate behavioral interview response"""
        
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='user',
            message=response
        )
        
        # Generate assessment
        assessment = self._assess_behavioral_response(response)
        
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='assistant',
            message=assessment['feedback'],
            metadata={'score': assessment['score'], 'assessment': assessment}
        )
        
        return assessment
    
    def _assess_behavioral_response(self, response: str) -> Dict[str, Any]:
        """Assess behavioral interview response using AI"""
        
        score = 0
        feedback_items = []
        
        # Check for STAR method
        has_situation = any(word in response.lower() for word in ['situation', 'context', 'scenario', 'background'])
        has_task = any(word in response.lower() for word in ['task', 'challenge', 'problem', 'responsibility'])
        has_action = any(word in response.lower() for word in ['action', 'did', 'implemented', 'solution'])
        has_result = any(word in response.lower() for word in ['result', 'outcome', 'achieved', 'learned'])
        
        if has_situation:
            score += 25
        else:
            feedback_items.append("Add more context about the situation/background")
        
        if has_task:
            score += 25
        else:
            feedback_items.append("Clarify the task or challenge you faced")
        
        if has_action:
            score += 25
        else:
            feedback_items.append("Detail the specific actions you took")
        
        if has_result:
            score += 25
        else:
            feedback_items.append("Include measurable results or lessons learned")
        
        return {
            'score': score,
            'feedback': f'Score: {score}/100. ' + ' '.join(feedback_items) if feedback_items else 'Excellent STAR response!',
            'star_method': {
                'situation': has_situation,
                'task': has_task,
                'action': has_action,
                'result': has_result
            },
            'response_length': len(response),
            'recommendations': feedback_items
        }
    
    # ==================== Session Management & Memory ====================
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End interview session and store analytics"""
        
        # Calculate session metrics
        conversation = self.memory_manager.get_conversation_history(
            user_id=self.user_id,
            session_id=session_id
        )
        
        # Store session analytics
        session_duration = len(conversation) * 2  # Estimate minutes
        
        return {
            'session_ended': True,
            'duration_minutes': session_duration,
            'messages': len(conversation),
            'progress_saved': True
        }
    
    def get_adaptive_problems(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get adaptive daily problems based on mastery level"""
        
        # Get user's mastery profile
        mastery = self.memory_manager.get_problem_mastery(self.user_id)
        
        # Find weak areas
        weak_categories = {}
        for problem in mastery:
            category = problem['category']
            if problem['mastery_level'] < 2:
                weak_categories[category] = weak_categories.get(category, 0) + 1
        
        # Select problems from weak categories
        adaptive_problems = []
        categories_by_weakness = sorted(weak_categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, _ in categories_by_weakness[:limit]:
            problem = self.engine.get_coding_problem(category)
            adaptive_problems.append({
                'problem_id': problem.id,
                'title': problem.title,
                'difficulty': problem.difficulty,
                'category': category,
                'reason': f'Based on your performance in {category}'
            })
        
        return adaptive_problems
    
    def verify_mastery(self, problem_id: str, follow_up_count: int = 2) -> bool:
        """Verify mastery through follow-up questions"""
        
        if follow_up_count >= 2:
            self.memory_manager.verify_mastery(
                user_id=self.user_id,
                problem_id=problem_id,
                follow_up_questions=follow_up_count
            )
            return True
        
        return False
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get comprehensive learning summary"""
        
        summary = self.memory_manager.get_user_summary(self.user_id)
        recent_progress = self.memory_manager.get_progress_analytics(self.user_id, days=30)
        
        return {
            'overall_summary': summary,
            'recent_progress': recent_progress,
            'next_recommended_topic': self.mentor.recommend_next_topic(),
            'target_date': '2026-03-15',
            'progress_to_target': self._calculate_progress_to_target()
        }
    
    def _calculate_progress_to_target(self) -> float:
        """Calculate progress percentage toward March 2026 target"""
        
        summary = self.memory_manager.get_user_summary(self.user_id)
        
        # Target: 300 problems solved, 15+ topics mastered
        problems_target = 300
        topics_target = 15
        
        problems_progress = min(100, (summary['total_problems_solved'] / problems_target) * 100)
        topics_progress = min(100, (summary['topics_covered'] / topics_target) * 100)
        
        return (problems_progress + topics_progress) / 2


# Global instance factory
_interview_managers = {}

def get_interview_manager(user_id: str) -> EnhancedInterviewManager:
    """Get or create interview manager for user"""
    if user_id not in _interview_managers:
        _interview_managers[user_id] = EnhancedInterviewManager(user_id)
    return _interview_managers[user_id]
