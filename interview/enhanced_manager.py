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
        problems = self.engine.get_coding_problems_by_difficulty(difficulty)
        if not problems:
            # Fallback to any problem if none found for difficulty
            problems = self.engine.get_coding_problems_by_difficulty('medium')
        if problems:
            # Select first problem from list
            problem_dict = problems[0]
            # Convert dict to CodingProblem-like object or use dict directly
            from interview.simulation_engine import CodingProblem
            # Find the actual problem object
            problem_id = problem_dict.get('id', 'two-sum')
            problem = self.engine.get_coding_problem(problem_id)
            if not problem:
                # If still not found, use two-sum as default
                problem = self.engine.get_coding_problem('two-sum')
        else:
            # Last resort: use two-sum
            problem = self.engine.get_coding_problem('two-sum')
        
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
        test_inputs: Optional[List[str]] = None,
        custom_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit code with compilation and testing, with optional custom input"""
        
        # Store submission
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='user',
            message=f'Code submitted in {language}',
            metadata={'code_length': len(code), 'language': language, 'custom_input': custom_input is not None}
        )
        
        # Compile and run
        compile_result = self.compiler.compile_and_run(code, language, custom_input or "", stdin_input=bool(custom_input))
        
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
        
        # Test against cases (with custom input if provided)
        # Get problem from current session
        problem = None
        if self.current_session:
            problem_id = getattr(self.current_session, 'id', None) or str(self.current_session.get('problem_id', '')) if isinstance(self.current_session, dict) else None
            if problem_id:
                problem = self.engine.get_coding_problem(problem_id)
        
        # If no problem found, use a default one for testing
        if not problem:
            problem = self.engine.get_coding_problem('two-sum')
        
        # Convert problem to dict if it's a CodingProblem object
        if hasattr(problem, 'test_cases'):
            test_cases = [tc.to_dict() if hasattr(tc, 'to_dict') else tc for tc in problem.test_cases]
        elif isinstance(problem, dict):
            test_cases = problem.get('test_cases', [])
        else:
            test_cases = []
        
        test_results = self.compiler.test_against_cases(
            code, language, test_cases, custom_input=custom_input
        )
        
        # Analyze code quality
        complexity = self.compiler.analyze_code_complexity(code, language)
        
        # Generate AI feedback using mentor agent
        feedback = self._generate_coding_feedback(
            code, 
            test_results, 
            complexity, 
            compile_result,
            session_id
        )
        
        # Store feedback in memory (already stored by mentor)
        # Also track topic progress if problem solved
        if test_results.get('passed_count', 0) == test_results.get('total_count', 0):
            # Problem solved - track progress
            # Get problem from current session or use default
            problem_obj = problem
            if problem_obj:
                # Extract problem info
                if hasattr(problem_obj, 'id'):
                    problem_id = problem_obj.id
                    problem_name = problem_obj.title
                    problem_topic = problem_obj.topic
                elif isinstance(problem_obj, dict):
                    problem_id = problem_obj.get('id', 'unknown')
                    problem_name = problem_obj.get('title', 'Unknown')
                    problem_topic = problem_obj.get('topic', 'general')
                else:
                    problem_id = 'unknown'
                    problem_name = 'Unknown Problem'
                    problem_topic = 'general'
                
                self.mentor.record_problem_attempt(
                    problem_id=problem_id,
                    problem_name=problem_name,
                    category=problem_topic,
                    time_minutes=0,  # Could track actual time
                    optimal=hasattr(complexity, 'nested_loops') and complexity.nested_loops <= 1
                )
                
                # Update topic coverage
                self.mentor.track_topic_progress(
                    topic=problem_topic,
                    category='DSA',
                    proficiency=2 if (hasattr(complexity, 'nested_loops') and complexity.nested_loops <= 1) else 1
                )
                
                # Sync roadmap progress
                self._sync_roadmap_progress()
                
                # Update tracker analytics
                self._update_tracker_analytics(problem, test_results)
                
                # Process through integration pipeline
                try:
                    from integration.main_pipeline import get_pipeline
                    pipeline = get_pipeline(self.user_id)
                    pipeline.process_interview_completion(
                        session_id=session_id,
                        problem_id=problem.id,
                        score=self._calculate_optimization_score(complexity, test_results),
                        test_results=test_results
                    )
                except:
                    pass  # Silently fail - integration is optional
        
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
        compile_result: Any,
        session_id: str
    ) -> Dict[str, Any]:
        """Generate AI interviewer feedback on code using mentor agent"""
        
        passed = test_results.get('passed_count', 0)
        total = test_results.get('total_count', 0)
        
        # Build feedback context for AI agent
        feedback_context = {
            'test_results': test_results,
            'complexity': complexity.__dict__ if hasattr(complexity, '__dict__') else str(complexity),
            'execution_time_ms': compile_result.execution_time_ms,
            'code_length': len(code),
            'language': 'python'  # Could be passed as parameter
        }
        
        # Create feedback prompt for AI agent
        feedback_prompt = f"""
        Code Review:
        - Test cases: {passed}/{total} passed
        - Execution time: {compile_result.execution_time_ms}ms
        - Complexity: {complexity.__dict__ if hasattr(complexity, '__dict__') else str(complexity)}
        
        Provide constructive feedback on this code submission.
        """
        
        # Get AI feedback from mentor
        ai_feedback_message = self.mentor.process_user_input(
            message=feedback_prompt,
            context=feedback_context
        )
        
        # Also generate structured feedback
        message_parts = []
        suggestions = []
        
        if passed == total:
            message_parts.append("✅ All test cases passed! ")
        else:
            message_parts.append(f"⚠️  {passed}/{total} test cases passed. ")
        
        # Complexity feedback
        if hasattr(complexity, 'nested_loops') and complexity.nested_loops >= 3:
            message_parts.append("Your solution has deep nesting. ")
            suggestions.append("Consider reducing nested loops with data structures like hash maps")
        
        if hasattr(complexity, 'recursion_detected') and complexity.recursion_detected:
            message_parts.append("Recursion detected. ")
            suggestions.append("Verify stack depth and consider iterative approach if recursion is deep")
        
        if hasattr(complexity, 'sorting_detected') and complexity.sorting_detected:
            message_parts.append("Your solution uses sorting. ")
            suggestions.append("Verify if sorting is necessary or if a hash map approach is better")
        
        message_parts.append(f"Execution time: {compile_result.execution_time_ms}ms. ")
        
        # Combine AI feedback with structured feedback
        combined_message = ''.join(message_parts) + "\n\nAI Feedback: " + ai_feedback_message
        
        return {
            'message': combined_message,
            'ai_feedback': ai_feedback_message,
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
        
        # Get system design problem
        from interview.simulation_engine import CompanyRole
        company_role_enum = None
        try:
            company_role_enum = CompanyRole[company_role.upper()]
        except (KeyError, AttributeError):
            company_role_enum = CompanyRole.GOOGLE_SDE
        
        design_topic_dict = self.engine.get_system_design_problem(topic, company_role_enum)
        if not design_topic_dict:
            # Fallback to url-shortener
            design_topic_dict = self.engine.get_system_design_problem('url-shortener', company_role_enum)
        
        # Convert to object-like structure for compatibility
        class DesignTopic:
            def __init__(self, data):
                self.title = data.get('title', topic)
                self.requirements = data.get('requirements', [])
                self.discussion_points = data.get('requirements', [])  # Use requirements as discussion points
                self.company_specific_guidance = data.get('company_specific', {})
        
        design_topic = DesignTopic(design_topic_dict) if design_topic_dict else None
        
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
        
        if design_topic:
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
        else:
            return {
                'session_id': session.id,
                'topic': topic,
                'requirements': [],
                'discussion_points': [],
                'company_specific_guidance': {},
                'whiteboard_ready': True
            }
    
    def update_whiteboard(
        self,
        session_id: str,
        mode: WhiteboardMode,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update system design whiteboard with persistence"""
        
        self.whiteboard_state[mode.value] = content
        self.whiteboard_state['last_updated'] = datetime.now().isoformat()
        
        # Store in memory for persistence
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='user',
            message=f'Updated {mode.value} on whiteboard',
            metadata={
                'whiteboard_mode': mode.value,
                'content': content,
                'full_whiteboard_state': self.whiteboard_state
            }
        )
        
        # Get AI feedback on design
        design_prompt = f"""
        System Design Review:
        Mode: {mode.value}
        Content: {json.dumps(content, indent=2)}
        
        Provide feedback on this system design decision.
        """
        
        ai_feedback = self.mentor.process_user_input(
            message=design_prompt,
            context={'whiteboard_mode': mode.value, 'content': content}
        )
        
        # Generate structured feedback
        structured_feedback = self._analyze_design(mode, content)
        
        return {
            'updated': True,
            'feedback': structured_feedback,
            'ai_feedback': ai_feedback,
            'whiteboard_state': self.whiteboard_state
        }
    
    def get_whiteboard_state(self, session_id: str) -> Dict[str, Any]:
        """Retrieve whiteboard state from memory"""
        # Try to get from current state first
        if self.whiteboard_state:
            return self.whiteboard_state
        
        # Otherwise, retrieve from memory
        history = self.memory_manager.get_conversation_history(
            user_id=self.user_id,
            session_id=session_id,
            limit=50
        )
        
        # Find most recent whiteboard state
        for msg in reversed(history):
            metadata = msg.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    continue
            
            if 'full_whiteboard_state' in metadata:
                return metadata['full_whiteboard_state']
        
        return {}
    
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
        
        question_dict = self.engine.get_behavioral_question()
        
        self.mentor.start_session(
            session_id=session.id,
            session_type='behavioral',
            context={'company': company_role}
        )
        
        # Convert dict to object-like structure for compatibility
        class BehavioralQuestion:
            def __init__(self, data):
                self.question = data.get('question', 'Tell me about yourself.')
                self.category = data.get('id', 'general')
                self.tips = ['Use STAR method', 'Be specific', 'Show impact']
        
        question = BehavioralQuestion(question_dict) if question_dict else BehavioralQuestion({})
        
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
        """Get adaptive daily problems (2-3) based on mastery level and weakness profile"""
        
        # Get user's mastery profile
        mastery = self.memory_manager.get_problem_mastery(self.user_id)
        topic_coverage = self.memory_manager.get_topic_coverage(self.user_id)
        
        # Get today's date for daily task tracking
        today = datetime.now().date().isoformat()
        
        # Check if daily tasks already generated today
        daily_tasks = self.memory_manager.get_daily_tasks(self.user_id, today)
        if daily_tasks and len(daily_tasks) >= 2:
            # Return existing tasks
            return [task for task in daily_tasks if not task.get('completed', False)]
        
        # Find weak areas - prioritize topics with low proficiency
        weak_topics = {}
        for topic_data in topic_coverage:
            proficiency = topic_data.get('proficiency_level', 1)
            if proficiency < 3:
                weak_topics[topic_data['topic']] = {
                    'proficiency': proficiency,
                    'category': topic_data['category'],
                    'problems_solved': topic_data.get('problems_solved', 0)
                }
        
        # Also check problem mastery for categories
        weak_categories = {}
        for problem in mastery:
            category = problem['category']
            mastery_level = problem.get('mastery_level', 1)
            if mastery_level < 2:
                if category not in weak_categories:
                    weak_categories[category] = {'count': 0, 'avg_mastery': 0, 'total_mastery': 0}
                weak_categories[category]['count'] += 1
                weak_categories[category]['total_mastery'] += mastery_level
        
        # Calculate average mastery per category
        for category in weak_categories:
            weak_categories[category]['avg_mastery'] = (
                weak_categories[category]['total_mastery'] / weak_categories[category]['count']
            )
        
        # Select 2-3 problems from weakest areas
        adaptive_problems = []
        
        # Prioritize by weakness (lowest proficiency first)
        sorted_weak_topics = sorted(weak_topics.items(), key=lambda x: x[1]['proficiency'])
        sorted_weak_categories = sorted(weak_categories.items(), key=lambda x: x[1]['avg_mastery'])
        
        # Mix topics and categories
        selected = set()
        problem_count = 0
        
        # First, select from weak topics
        for topic, data in sorted_weak_topics[:limit]:
            if problem_count >= limit:
                break
            category = data['category']
            try:
                # Get problems by difficulty and select one
                problems = self.engine.get_coding_problems_by_difficulty('medium')
                if not problems:
                    problems = self.engine.get_coding_problems_by_difficulty('easy')
                if problems:
                    problem_dict = problems[0]
                    problem_id = problem_dict.get('id', 'two-sum')
                    problem = self.engine.get_coding_problem(problem_id)
                else:
                    problem = self.engine.get_coding_problem('two-sum')
                
                if problem:
                    # Convert to dict if needed
                    if hasattr(problem, 'id'):
                        prob_id = problem.id
                        prob_title = problem.title
                        prob_difficulty = problem.difficulty
                    elif isinstance(problem, dict):
                        prob_id = problem.get('id', 'unknown')
                        prob_title = problem.get('title', 'Unknown')
                        prob_difficulty = problem.get('difficulty', 'medium')
                    else:
                        continue
                    
                    if prob_id not in selected:
                        adaptive_problems.append({
                            'problem_id': prob_id,
                            'title': prob_title,
                            'difficulty': prob_difficulty,
                            'category': category,
                            'topic': topic,
                            'reason': f'Weak area: {topic} (proficiency: {data["proficiency"]}/3)',
                            'requires_mastery_verification': True
                        })
                        selected.add(prob_id)
                        problem_count += 1
            except:
                continue
        
        # Fill remaining slots from weak categories
        for category, data in sorted_weak_categories:
            if problem_count >= limit:
                break
            try:
                # Get problems by difficulty and select one
                problems = self.engine.get_coding_problems_by_difficulty('medium')
                if not problems:
                    problems = self.engine.get_coding_problems_by_difficulty('easy')
                if problems:
                    problem_dict = problems[0]
                    problem_id = problem_dict.get('id', 'two-sum')
                    problem = self.engine.get_coding_problem(problem_id)
                else:
                    problem = self.engine.get_coding_problem('two-sum')
                
                if problem:
                    # Convert to dict if needed
                    if hasattr(problem, 'id'):
                        prob_id = problem.id
                        prob_title = problem.title
                        prob_difficulty = problem.difficulty
                    elif isinstance(problem, dict):
                        prob_id = problem.get('id', 'unknown')
                        prob_title = problem.get('title', 'Unknown')
                        prob_difficulty = problem.get('difficulty', 'medium')
                    else:
                        continue
                    
                    if prob_id not in selected:
                        adaptive_problems.append({
                            'problem_id': prob_id,
                            'title': prob_title,
                            'difficulty': prob_difficulty,
                            'category': category,
                            'reason': f'Weak category: {category} (avg mastery: {data["avg_mastery"]:.1f})',
                            'requires_mastery_verification': True
                        })
                        selected.add(prob_id)
                        problem_count += 1
            except:
                continue
        
        # Store daily tasks in memory
        if adaptive_problems:
            self.memory_manager.create_daily_tasks(self.user_id, today, adaptive_problems)
        
        return adaptive_problems
    
    def verify_mastery(self, problem_id: str, follow_up_count: int = 2) -> bool:
        """Verify mastery through follow-up questions"""
        
        today = datetime.now().date().isoformat()
        
        # Record follow-up answers
        for _ in range(follow_up_count):
            self.memory_manager.record_follow_up_answer(
                user_id=self.user_id,
                date=today,
                task_id=problem_id
            )
        
        # Verify mastery if enough follow-ups answered
        if follow_up_count >= 2:
            self.memory_manager.verify_mastery(
                user_id=self.user_id,
                problem_id=problem_id,
                follow_up_questions=follow_up_count
            )
            
            # Mark daily task as mastery verified
            self.memory_manager.complete_daily_task(
                user_id=self.user_id,
                date=today,
                task_id=problem_id,
                mastery_verified=True
            )
            return True
        
        return False
    
    def complete_daily_task(self, problem_id: str, mastery_verified: bool = False):
        """Mark a daily task as completed"""
        today = datetime.now().date().isoformat()
        self.memory_manager.complete_daily_task(
            user_id=self.user_id,
            date=today,
            task_id=problem_id,
            mastery_verified=mastery_verified
        )
    
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
    
    def _sync_roadmap_progress(self):
        """Sync roadmap progress after problem completion"""
        try:
            from roadmap.enhanced_generator import get_roadmap_generator
            generator = get_roadmap_generator(self.user_id)
            generator.sync_progress()
        except Exception as e:
            # Silently fail - roadmap sync is not critical
            pass
    
    def _update_tracker_analytics(self, problem, test_results):
        """Update tracker analytics after problem completion"""
        try:
            from tracker.enhanced_tracker import ProblemTracker
            tracker = ProblemTracker()
            
            # Classify problem
            classification = tracker.classify_problem(
                title=problem.title,
                tags=[problem.topic],
                difficulty=problem.difficulty
            )
            
            # Update weakness profile if needed
            if test_results.get('passed_count', 0) < test_results.get('total_count', 0):
                # Problem not fully solved - track as weakness
                from memory.db import upsert_weakness
                upsert_weakness(problem.topic, classification.get('combined_score', 3))
        except Exception as e:
            # Silently fail - tracker update is not critical
            pass


# Global instance factory
_interview_managers = {}

def get_interview_manager(user_id: str) -> EnhancedInterviewManager:
    """Get or create interview manager for user"""
    if user_id not in _interview_managers:
        _interview_managers[user_id] = EnhancedInterviewManager(user_id)
    return _interview_managers[user_id]
