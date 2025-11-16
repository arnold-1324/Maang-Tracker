"""
Integration Tests for Enhanced Interview Preparation Platform
Tests all modules: memory, AI agent, interview simulation, roadmap, and UI
"""

import unittest
import os
import tempfile
from datetime import datetime, timedelta

# Import all enhanced modules
from maang_agent.memory_persistence import AgentMemoryManager, get_memory_manager
from maang_agent.agent import MaangMentorWithMemory, get_mentor
from interview.enhanced_manager import EnhancedInterviewManager, get_interview_manager
from roadmap.enhanced_generator import EnhancedRoadmapGenerator, RoadmapBST
from ui.enhancement_manager import UIEnhancementManager, get_ui_enhancement_manager


class TestMemoryPersistence(unittest.TestCase):
    """Test AI agent memory persistence"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.manager = AgentMemoryManager(self.temp_db.name)
    
    def tearDown(self):
        os.unlink(self.temp_db.name)
    
    def test_conversation_storage(self):
        """Test storing and retrieving conversations"""
        user_id = "test_user"
        session_id = "session_123"
        
        # Store conversation
        msg_id = self.manager.store_conversation(
            user_id=user_id,
            session_id=session_id,
            role='user',
            message='Hello, I have a question about arrays'
        )
        
        self.assertIsNotNone(msg_id)
        
        # Retrieve conversation
        history = self.manager.get_conversation_history(user_id, session_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['message'], 'Hello, I have a question about arrays')
    
    def test_topic_coverage_tracking(self):
        """Test topic coverage tracking"""
        user_id = "test_user"
        
        topic_id = self.manager.track_topic_coverage(
            user_id=user_id,
            topic='Binary Search',
            category='Algorithms',
            status='learning',
            proficiency_level=2
        )
        
        self.assertIsNotNone(topic_id)
        
        # Retrieve topics
        topics = self.manager.get_topic_coverage(user_id, 'Algorithms')
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0]['topic'], 'Binary Search')
    
    def test_progress_analytics(self):
        """Test progress analytics recording"""
        user_id = "test_user"
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.manager.record_daily_progress(
            user_id=user_id,
            date=today,
            problems_attempted=5,
            problems_solved=4,
            avg_difficulty=2.5,
            time_spent_minutes=120
        )
        
        analytics = self.manager.get_progress_analytics(user_id, days=1)
        self.assertGreater(len(analytics), 0)


class TestGoogleAIAgentMemory(unittest.TestCase):
    """Test Google AI agent with memory integration"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.user_id = "test_user"
    
    def tearDown(self):
        os.unlink(self.temp_db.name)
    
    def test_mentor_initialization(self):
        """Test mentor initialization"""
        mentor = MaangMentorWithMemory(self.user_id)
        self.assertIsNotNone(mentor)
        self.assertEqual(mentor.user_id, self.user_id)
    
    def test_session_management(self):
        """Test mentor session management"""
        mentor = MaangMentorWithMemory(self.user_id)
        
        mentor.start_session('session_1', 'coding', {'difficulty': 'medium'})
        self.assertEqual(mentor.current_session_id, 'session_1')
    
    def test_progress_tracking(self):
        """Test mentor progress tracking"""
        mentor = MaangMentorWithMemory(self.user_id)
        
        mentor.track_topic_progress('Arrays', 'DSA', 2)
        mentor.track_topic_progress('Binary Search', 'DSA', 3)
        
        summary = mentor.get_progress_summary()
        self.assertIsNotNone(summary)


class TestEnhancedInterviewSimulation(unittest.TestCase):
    """Test enhanced interview simulation"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.user_id = "test_user"
    
    def tearDown(self):
        os.unlink(self.temp_db.name)
    
    def test_coding_interview_start(self):
        """Test starting a coding interview"""
        manager = EnhancedInterviewManager(self.user_id)
        
        result = manager.start_coding_interview(difficulty='easy')
        
        self.assertIn('session_id', result)
        self.assertIn('problem', result)
        self.assertIn('start_time', result)
    
    def test_system_design_interview_start(self):
        """Test starting a system design interview"""
        manager = EnhancedInterviewManager(self.user_id)
        
        result = manager.start_system_design_interview()
        
        self.assertIn('session_id', result)
        self.assertIn('topic', result)
        self.assertIn('whiteboard_ready', result)
    
    def test_behavioral_interview_start(self):
        """Test starting a behavioral interview"""
        manager = EnhancedInterviewManager(self.user_id)
        
        result = manager.start_behavioral_interview()
        
        self.assertIn('session_id', result)
        self.assertIn('question', result)
        self.assertIn('category', result)


class TestBSTRoadmapVisualization(unittest.TestCase):
    """Test BST-based roadmap visualization"""
    
    def test_bst_creation(self):
        """Test BST node creation and insertion"""
        bst = RoadmapBST()
        
        bst.insert('Arrays', 1, 'DSA', 20)
        bst.insert('Graphs', 4, 'DSA', 30)
        bst.insert('Trees', 3, 'DSA', 25)
        
        self.assertEqual(len(bst.nodes), 3)
    
    def test_bst_ordering(self):
        """Test in-order traversal of BST"""
        bst = RoadmapBST()
        
        bst.insert('Arrays', 1, 'DSA', 20)
        bst.insert('Graphs', 4, 'DSA', 30)
        bst.insert('Trees', 3, 'DSA', 25)
        bst.insert('DP', 5, 'DSA', 35)
        
        in_order = bst.get_in_order()
        difficulties = [node.difficulty for node in in_order]
        
        # Should be in ascending order of difficulty
        self.assertEqual(difficulties, sorted(difficulties))
    
    def test_roadmap_generation(self):
        """Test learning roadmap generation"""
        generator = EnhancedRoadmapGenerator()
        
        roadmap = generator.get_learning_roadmap(weeks=4)
        
        self.assertIn('weekly_plan', roadmap)
        self.assertEqual(len(roadmap['weekly_plan']), 4)
        self.assertIn('bst_visualization', roadmap)


class TestUIEnhancements(unittest.TestCase):
    """Test UI enhancement components"""
    
    def test_countdown_calculation(self):
        """Test countdown to target date"""
        manager = UIEnhancementManager()
        
        countdown = manager.get_countdown_data()
        
        self.assertIn('days_remaining', countdown)
        self.assertIn('weeks_remaining', countdown)
        self.assertIn('months_remaining', countdown)
        self.assertIn('urgency_level', countdown)
        self.assertGreater(countdown['days_remaining'], 0)
    
    def test_progress_indicators_html(self):
        """Test progress indicators HTML generation"""
        manager = UIEnhancementManager()
        
        progress_data = {
            'completion_percentage': 45.5,
            'solved_problems': 50,
            'total_problems': 110,
            'completed_topics': 5,
            'in_progress': 3,
            'not_started': 12
        }
        
        html = manager.get_progress_indicators_html(progress_data)
        
        self.assertIn('45.5%', html)
        self.assertIn('50/110', html)
        self.assertIn('progress-bar', html)
    
    def test_countdown_widget_html(self):
        """Test countdown widget HTML"""
        manager = UIEnhancementManager()
        
        html = manager.get_countdown_widget_html()
        
        self.assertIn('countdown-widget', html)
        self.assertIn('March 15, 2026', html)
        self.assertIn('countdown-display', html)
    
    def test_css_generation(self):
        """Test CSS generation"""
        manager = UIEnhancementManager()
        
        css = manager.get_enhanced_css()
        
        self.assertIn('.countdown-widget', css)
        self.assertIn('.progress-section', css)
        self.assertIn('.task-item', css)
        self.assertIn('.bst-visualization', css)


class TestIntegration(unittest.TestCase):
    """Test integration between all components"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.user_id = "test_user"
    
    def tearDown(self):
        os.unlink(self.temp_db.name)
    
    def test_end_to_end_interview_flow(self):
        """Test complete interview flow with memory integration"""
        mentor = get_mentor(self.user_id)
        interview_mgr = get_interview_manager(self.user_id)
        ui_mgr = get_ui_enhancement_manager()
        
        # Start interview
        result = interview_mgr.start_coding_interview(difficulty='medium')
        session_id = result['session_id']
        
        # Mentor tracks session
        mentor.start_session(session_id, 'coding', result)
        
        # Get countdown
        countdown = ui_mgr.get_countdown_data()
        
        self.assertIsNotNone(session_id)
        self.assertEqual(mentor.current_session_id, session_id)
        self.assertGreater(countdown['days_remaining'], 0)
    
    def test_roadmap_and_interview_integration(self):
        """Test roadmap and interview components working together"""
        roadmap_gen = EnhancedRoadmapGenerator(self.user_id)
        interview_mgr = get_interview_manager(self.user_id)
        
        # Generate roadmap
        roadmap = roadmap_gen.get_learning_roadmap(weeks=12)
        
        # Get adaptive problems
        problems = interview_mgr.get_adaptive_problems()
        
        self.assertIn('weekly_plan', roadmap)
        self.assertIsInstance(problems, list)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing modules"""
    
    def test_roadmap_recommend_function(self):
        """Test backward-compatible recommend function"""
        from roadmap.enhanced_generator import recommend
        
        recs = recommend(limit=3)
        
        self.assertIsInstance(recs, list)
        self.assertLessEqual(len(recs), 3)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
