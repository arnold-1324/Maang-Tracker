"""
Enhanced Roadmap Generator with Binary Search Tree Visualization
Interactive BST with progress tracking and adaptive learning path
"""

import sys
import os

# Add parent directory to path so we can import sibling packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from memory.db import get_weaknesses
from maang_agent.memory_persistence import get_memory_manager


class BSTNode:
    """Binary Search Tree node for roadmap visualization"""
    
    def __init__(self, topic: str, difficulty: int, category: str, problems_count: int = 0):
        self.topic = topic
        self.difficulty = difficulty
        self.category = category
        self.problems_count = problems_count
        self.solved = 0
        self.progress = 0.0
        self.left = None
        self.right = None
        self.parent = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for JSON serialization"""
        return {
            'topic': self.topic,
            'difficulty': self.difficulty,
            'category': self.category,
            'problems_count': self.problems_count,
            'solved': self.solved,
            'progress': round(self.progress, 1),
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None
        }


class RoadmapBST:
    """Binary Search Tree for organizing learning roadmap"""
    
    def __init__(self):
        self.root = None
        self.nodes = {}
    
    def insert(self, topic: str, difficulty: int, category: str, problems_count: int) -> BSTNode:
        """Insert topic into BST by difficulty"""
        node = BSTNode(topic, difficulty, category, problems_count)
        self.nodes[topic] = node
        
        if self.root is None:
            self.root = node
        else:
            self._insert_recursive(self.root, node)
        
        return node
    
    def _insert_recursive(self, parent: BSTNode, new_node: BSTNode):
        """Recursively insert node maintaining BST property"""
        if new_node.difficulty < parent.difficulty:
            if parent.left is None:
                parent.left = new_node
                new_node.parent = parent
            else:
                self._insert_recursive(parent.left, new_node)
        else:
            if parent.right is None:
                parent.right = new_node
                new_node.parent = parent
            else:
                self._insert_recursive(parent.right, new_node)
    
    def get_in_order(self) -> List[BSTNode]:
        """Get topics in order of difficulty (in-order traversal)"""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node: Optional[BSTNode], result: List):
        """In-order traversal: left -> node -> right"""
        if node is None:
            return
        
        self._inorder_recursive(node.left, result)
        result.append(node)
        self._inorder_recursive(node.right, result)
    
    def to_visualization(self) -> Dict[str, Any]:
        """Convert BST to visualization format"""
        return {
            'root': self.root.to_dict() if self.root else None,
            'nodes_count': len(self.nodes),
            'categories': self._get_category_stats()
        }
    
    def _get_category_stats(self) -> Dict[str, Dict]:
        """Get statistics by category"""
        stats = {}
        
        for node in self.nodes.values():
            if node.category not in stats:
                stats[node.category] = {
                    'total_topics': 0,
                    'total_problems': 0,
                    'solved_problems': 0,
                    'avg_progress': 0.0
                }
            
            stats[node.category]['total_topics'] += 1
            stats[node.category]['total_problems'] += node.problems_count
            stats[node.category]['solved_problems'] += node.solved
        
        for category in stats:
            total = stats[category]['total_problems']
            solved = stats[category]['solved_problems']
            stats[category]['avg_progress'] = (solved / total * 100) if total > 0 else 0
        
        return stats


class EnhancedRoadmapGenerator:
    """Generate adaptive roadmaps with BST visualization"""
    
    TOPIC_DATABASE = {
        'Two Pointers': {'difficulty': 1, 'category': 'Arrays', 'problems': 15},
        'Sliding Window': {'difficulty': 2, 'category': 'Arrays', 'problems': 20},
        'String Manipulation': {'difficulty': 2, 'category': 'Strings', 'problems': 18},
        'Hash Maps': {'difficulty': 2, 'category': 'Data Structures', 'problems': 25},
        'Binary Trees': {'difficulty': 3, 'category': 'Trees', 'problems': 30},
        'BST Operations': {'difficulty': 3, 'category': 'Trees', 'problems': 20},
        'Tree Traversal': {'difficulty': 2, 'category': 'Trees', 'problems': 15},
        'BFS/DFS': {'difficulty': 3, 'category': 'Graphs', 'problems': 25},
        'Shortest Path': {'difficulty': 3, 'category': 'Graphs', 'problems': 15},
        'Topological Sort': {'difficulty': 4, 'category': 'Graphs', 'problems': 10},
        'Union Find': {'difficulty': 3, 'category': 'Graphs', 'problems': 12},
        'DP Fundamentals': {'difficulty': 3, 'category': 'DP', 'problems': 30},
        'DP Patterns': {'difficulty': 4, 'category': 'DP', 'problems': 35},
        'DP Optimization': {'difficulty': 5, 'category': 'DP', 'problems': 20},
        'Scalability Basics': {'difficulty': 4, 'category': 'System Design', 'problems': 10},
        'Database Design': {'difficulty': 4, 'category': 'System Design', 'problems': 12},
        'API Design': {'difficulty': 4, 'category': 'System Design', 'problems': 8},
        'Distributed Systems': {'difficulty': 5, 'category': 'System Design', 'problems': 15},
        'Caching Strategies': {'difficulty': 4, 'category': 'System Design', 'problems': 10},
    }
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.memory_manager = get_memory_manager() if user_id else None
        self.bst = RoadmapBST()
        self._build_initial_bst()
        if user_id:
            self._sync_progress_with_memory()
    
    def _build_initial_bst(self):
        """Build initial BST from topic database"""
        for topic, metadata in self.TOPIC_DATABASE.items():
            self.bst.insert(
                topic=topic,
                difficulty=metadata['difficulty'],
                category=metadata['category'],
                problems_count=metadata['problems']
            )
    
    def _sync_progress_with_memory(self):
        """Sync BST node progress with memory manager data"""
        if not self.user_id or not self.memory_manager:
            return
        
        # Get problem mastery data
        mastery = self.memory_manager.get_problem_mastery(self.user_id)
        topic_coverage = self.memory_manager.get_topic_coverage(self.user_id)
        
        # Create mapping of topics to solved problems
        topic_to_solved = {}
        for problem in mastery:
            category = problem.get('category', '')
            # Map category to topic
            for topic, metadata in self.TOPIC_DATABASE.items():
                if metadata['category'] == category:
                    if topic not in topic_to_solved:
                        topic_to_solved[topic] = 0
                    topic_to_solved[topic] += 1
        
        # Update BST nodes with progress
        for topic, node in self.bst.nodes.items():
            # Update solved count
            solved = topic_to_solved.get(topic, 0)
            node.solved = solved
            
            # Calculate progress percentage
            if node.problems_count > 0:
                node.progress = min(100.0, (solved / node.problems_count) * 100)
            
            # Update from topic coverage if available
            for topic_data in topic_coverage:
                if topic_data['topic'] == topic:
                    proficiency = topic_data.get('proficiency_level', 1)
                    # Adjust progress based on proficiency
                    if proficiency >= 3:
                        node.progress = 100.0
                    elif proficiency == 2:
                        node.progress = max(node.progress, 50.0)
                    break
    
    def sync_progress(self):
        """Public method to sync progress (call after problem completions)"""
        if self.user_id:
            self._sync_progress_with_memory()
    
    def get_learning_roadmap(self, weeks: int = 12) -> Dict[str, Any]:
        """Generate personalized learning roadmap"""
        all_topics = self.bst.get_in_order()
        weekly_plan = []
        week_duration = max(1, len(all_topics) // weeks)
        
        for week in range(1, weeks + 1):
            start_idx = (week - 1) * week_duration
            end_idx = min(start_idx + week_duration, len(all_topics))
            
            week_topics = all_topics[start_idx:end_idx]
            
            week_plan = {
                'week': week,
                'focus_areas': [node.topic for node in week_topics],
                'categories': list(set(node.category for node in week_topics)),
                'estimated_problems': sum(node.problems_count for node in week_topics),
                'difficulty_range': f'{week_topics[0].difficulty}-{week_topics[-1].difficulty}',
                'recommendations': self._generate_week_recommendations(week_topics)
            }
            
            weekly_plan.append(week_plan)
            
            if self.memory_manager and self.user_id:
                self.memory_manager.create_learning_path(
                    user_id=self.user_id,
                    week_number=week,
                    primary_focus=week_topics[0].category if week_topics else 'General',
                    recommended_topics=[node.topic for node in week_topics],
                    target_problems=sum(node.problems_count for node in week_topics)
                )
        
        return {
            'user_id': self.user_id,
            'total_weeks': weeks,
            'target_date': (datetime.now() + timedelta(weeks=weeks)).isoformat(),
            'weekly_plan': weekly_plan,
            'bst_visualization': self.bst.to_visualization(),
            'progress_summary': self._get_progress_summary()
        }
    
    def _generate_week_recommendations(self, topics: List[BSTNode]) -> List[str]:
        """Generate specific recommendations for week"""
        recommendations = []
        
        for topic in topics:
            progress_pct = topic.progress
            
            if progress_pct == 0:
                recommendations.append(f'Start learning {topic.topic}')
            elif progress_pct < 50:
                recommendations.append(f'Complete {topic.topic} - {100-progress_pct:.0f}% remaining')
            elif progress_pct < 100:
                recommendations.append(f'Master {topic.topic} with follow-ups')
            else:
                recommendations.append(f'Review {topic.topic} for interview')
        
        return recommendations
    
    def _get_progress_summary(self) -> Dict[str, Any]:
        """Get overall progress summary"""
        total_topics = len(self.bst.nodes)
        completed_topics = sum(1 for node in self.bst.nodes.values() if node.progress >= 100)
        in_progress = sum(1 for node in self.bst.nodes.values() if 0 < node.progress < 100)
        not_started = sum(1 for node in self.bst.nodes.values() if node.progress == 0)
        
        total_problems = sum(node.problems_count for node in self.bst.nodes.values())
        solved_problems = sum(node.solved for node in self.bst.nodes.values())
        
        return {
            'total_topics': total_topics,
            'completed_topics': completed_topics,
            'in_progress': in_progress,
            'not_started': not_started,
            'total_problems': total_problems,
            'solved_problems': solved_problems,
            'completion_percentage': (completed_topics / total_topics * 100) if total_topics > 0 else 0,
            'estimated_hours': (total_problems * 30) // 60
        }
    
    def visualize_progress(self) -> Dict[str, Any]:
        """Get visualization data for progress display with updated progress"""
        # Sync progress before visualization
        if self.user_id:
            self._sync_progress_with_memory()
        
        category_stats = self.bst.to_visualization()['categories']
        
        by_difficulty = {
            'Easy': [],
            'Medium': [],
            'Hard': []
        }
        
        # Build node data with LeetCode/GFG URLs
        nodes_data = []
        for node in self.bst.get_in_order():
            if node.difficulty <= 2:
                difficulty = 'Easy'
            elif node.difficulty <= 3:
                difficulty = 'Medium'
            else:
                difficulty = 'Hard'
            
            node_data = {
                'topic': node.topic,
                'progress': round(node.progress, 1),
                'solved': node.solved,
                'total': node.problems_count,
                'difficulty': difficulty,
                'difficulty_score': node.difficulty,
                'category': node.category,
                'leetcode_url': f"https://leetcode.com/tag/{node.topic.lower().replace(' ', '-')}/",
                'gfg_url': f"https://www.geeksforgeeks.org/{node.topic.lower().replace(' ', '-')}/"
            }
            
            by_difficulty[difficulty].append(node_data)
            nodes_data.append(node_data)
        
        # Calculate overall progress
        total_problems = sum(node.problems_count for node in self.bst.nodes.values())
        total_solved = sum(node.solved for node in self.bst.nodes.values())
        overall_progress = (total_solved / total_problems * 100) if total_problems > 0 else 0
        
        return {
            'bst_tree': self.bst.to_visualization(),
            'category_progress': category_stats,
            'difficulty_distribution': by_difficulty,
            'nodes_data': nodes_data,
            'overall_progress': round(overall_progress, 1),
            'total_solved': total_solved,
            'total_problems': total_problems,
            'visualization_metadata': {
                'chart_type': 'bst',
                'color_scheme': 'progress-gradient',
                'hover_shows': ['progress', 'solved_problems', 'difficulty'],
                'click_redirects': True
            }
        }


_roadmap_generators = {}

def get_roadmap_generator(user_id: str = None) -> EnhancedRoadmapGenerator:
    """Get or create roadmap generator for user"""
    if user_id and user_id not in _roadmap_generators:
        _roadmap_generators[user_id] = EnhancedRoadmapGenerator(user_id)
    return _roadmap_generators.get(user_id) or EnhancedRoadmapGenerator()


def recommend(limit: int = 5) -> List[Dict]:
    """Get recommendations (backward compatible)"""
    generator = EnhancedRoadmapGenerator()
    roadmap = generator.get_learning_roadmap(weeks=12)
    
    if roadmap['weekly_plan']:
        week_plan = roadmap['weekly_plan'][0]
        return [
            {
                'topic': topic,
                'recommendations': [f'Practice {topic} problems']
            }
            for topic in week_plan['focus_areas']
        ][:limit]
    
    return []
