"""
Adaptive Learning Agent - Personalized DSA Training System
Integrates with TakeUForward curriculum to generate dynamic practice plans
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict
import random


class AdaptiveLearningAgent:
    """AI agent that creates personalized DSA training plans based on learning gaps"""
    
    # TakeUForward DSA Curriculum Structure
    TUF_CURRICULUM = {
        "arrays": {
            "easy": [
                "largest-element", "second-largest-element", "linear-search",
                "move-zeros-to-end", "remove-duplicates-from-sorted-array",
                "left-rotate-array-by-one", "left-rotate-array"
            ],
            "medium": [
                "two-sum", "sort-an-array-of-0s-1s-and-2s", "next-permutation",
                "kadanes-algorithm", "rearrange-array-elements-by-sign",
                "leaders-in-an-array", "merge-overlapping-subintervals",
                "print-the-matrix-in-spiral-manner", "rotate-matrix-by-90-degrees",
                "3-sum", "4-sum", "pascal-triangle", "maximum-consecutive-ones"
            ],
            "hard": [
                "majority-element-ii", "find-the-repeating-and-missing-number",
                "count-inversions", "reverse-pairs", "maximum-product-subarray",
                "merge-two-sorted-arrays-without-extra-space"
            ]
        },
        "strings": {
            "easy": [
                "check-if-palindrome", "remove-outermost-parentheses",
                "isomorphic-strings", "reverse-string"
            ],
            "medium": [
                "longest-substring-without-repeating-chars", "group-anagrams",
                "zigzag-conversion", "longest-palindromic-substring",
                "minimum-window-substring", "basic-calculator-ii"
            ],
            "hard": [
                "regular-expression-matching", "substring-with-concatenation-of-all-words",
                "wildcard-matching"
            ]
        },
        "linked-list": {
            "easy": [
                "introduction-to-singly-ll", "traversal-in-ll", "insertion-in-ll",
                "deletion-in-ll", "introduction-to-doubly-ll"
            ],
            "medium": [
                "reverse-a-ll", "middle-of-ll", "cycle-detection",
                "merge-two-sorted-lists", "add-two-numbers"
            ],
            "hard": [
                "merge-k-sorted-lists", "reverse-k-group", "lru-cache",
                "copy-list-with-random-pointer"
            ]
        },
        "binary-search": {
            "easy": [
                "search-x-in-sorted-array", "lower-bound", "upper-bound",
                "search-insert-position", "floor-and-ceil-in-sorted-array"
            ],
            "medium": [
                "first-and-last-occurrence", "search-in-rotated-sorted-array-i",
                "search-in-rotated-sorted-array-ii", "find-minimum-in-rotated-sorted-array",
                "single-element-in-sorted-array", "find-peak-element",
                "koko-eating-bananas", "minimum-days-to-make-m-bouquets",
                "find-the-smallest-divisor"
            ],
            "hard": [
                "split-array-largest-sum", "median-of-2-sorted-arrays",
                "aggressive-cows", "minimize-max-distance-to-gas-stations"
            ]
        },
        "recursion": {
            "easy": [
                "power-of-x-n", "count-subsequences-with-sum-k",
                "check-subsequence-with-sum-k"
            ],
            "medium": [
                "generate-parentheses", "power-set", "combination-sum",
                "combination-sum-ii", "subsets-i", "subsets-ii",
                "letter-combinations-of-phone-number"
            ],
            "hard": [
                "palindrome-partitioning", "rat-in-a-maze", "n-queens",
                "sudoku-solver", "m-coloring-problem", "word-search"
            ]
        },
        "hashing": {
            "easy": ["basic-hashing"],
            "medium": [
                "majority-element-i", "longest-consecutive-sequence",
                "longest-subarray-with-sum-k", "count-subarrays-with-given-sum",
                "count-subarrays-with-given-xor"
            ],
            "hard": []
        },
        "sorting": {
            "easy": [
                "selection-sort", "bubble-sort", "insertion-sort"
            ],
            "medium": [
                "merge-sort", "quick-sort"
            ],
            "hard": []
        },
        "dynamic-programming": {
            "easy": ["fibonacci", "climbing-stairs"],
            "medium": [
                "house-robber", "coin-change", "longest-increasing-subsequence",
                "edit-distance", "0-1-knapsack", "unbounded-knapsack"
            ],
            "hard": [
                "wildcard-matching-dp", "burst-balloons", "russian-doll-envelopes",
                "minimum-cost-to-cut-stick"
            ]
        },
        "graphs": {
            "easy": ["bfs", "dfs"],
            "medium": [
                "number-of-islands", "surrounded-regions", "rotting-oranges",
                "bipartite-graph", "topological-sort"
            ],
            "hard": [
                "word-ladder", "network-delay-time", "accounts-merge",
                "strongly-connected-components"
            ]
        }
    }
    
    # Difficulty progression weights
    DIFFICULTY_WEIGHTS = {
        "easy": 1.0,
        "medium": 1.5,
        "hard": 2.0
    }
    
    def __init__(self, db_path: str = "memory/memory.db"):
        """Initialize the adaptive learning agent"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize training database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Training session tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                topic TEXT,
                difficulty TEXT,
                problem_name TEXT,
                status TEXT,
                time_spent INTEGER,
                attempts INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning gaps and recommendations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                topic TEXT,
                gap_score FLOAT,
                recommended_problems TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Adaptive learning plan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                plan_type TEXT,
                duration_days INTEGER,
                topics TEXT,
                daily_target INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_learning_progress(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user's learning progress and identify gaps
        
        Args:
            progress_data: User's solved problems data from TakeUForward
            
        Returns:
            Analysis with gaps, strengths, and recommendations
        """
        # Parse problem data
        solved_problems = self._extract_problems(progress_data)
        topic_coverage = self._calculate_topic_coverage(solved_problems)
        
        # Calculate gap score (0-100, higher = more gaps)
        gap_analysis = self._analyze_gaps(topic_coverage)
        
        return {
            "total_solved": len(solved_problems),
            "topic_coverage": topic_coverage,
            "gaps": gap_analysis,
            "strengths": self._identify_strengths(topic_coverage),
            "next_topics": self._recommend_next_topics(gap_analysis),
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_problems(self, progress_data: Dict) -> List[Dict[str, Any]]:
        """Extract solved problems from progress data"""
        problems = []
        if isinstance(progress_data, dict) and "recentProgress" in progress_data:
            problems = progress_data["recentProgress"]
        return problems
    
    def _calculate_topic_coverage(self, problems: List[Dict]) -> Dict[str, float]:
        """Calculate coverage percentage for each topic"""
        topic_count = defaultdict(int)
        
        for problem in problems:
            slug = problem.get("problem_slug", "")
            # Infer topic from problem slug or ID
            topic = self._infer_topic(slug, problem.get("problemId", ""))
            if topic:
                topic_count[topic] += 1
        
        # Calculate coverage (solved / total in curriculum)
        coverage = {}
        for topic in self.TUF_CURRICULUM.keys():
            total = sum(len(probs) for probs in self.TUF_CURRICULUM[topic].values())
            solved = topic_count.get(topic, 0)
            coverage[topic] = round((solved / total) * 100, 2) if total > 0 else 0
        
        return coverage
    
    def _infer_topic(self, slug: str, problem_id: str) -> str:
        """Infer topic from problem slug or ID"""
        # Map slugs/IDs to topics
        topic_keywords = {
            "array": "arrays",
            "string": "strings",
            "linked": "linked-list",
            "ll": "linked-list",
            "binary": "binary-search",
            "search": "binary-search",
            "recursion": "recursion",
            "hash": "hashing",
            "sort": "sorting",
            "dp": "dynamic-programming",
            "graph": "graphs"
        }
        
        combined = f"{slug} {problem_id}".lower()
        for keyword, topic in topic_keywords.items():
            if keyword in combined:
                return topic
        
        return None
    
    def _analyze_gaps(self, coverage: Dict[str, float]) -> Dict[str, Any]:
        """Analyze learning gaps and weak areas"""
        gaps = {}
        for topic, coverage_pct in coverage.items():
            gap_score = 100 - coverage_pct  # Higher = bigger gap
            difficulty_weight = self._estimate_difficulty_gap(topic, coverage_pct)
            
            gaps[topic] = {
                "coverage_pct": coverage_pct,
                "gap_score": gap_score,
                "difficulty_weight": difficulty_weight,
                "priority": self._calculate_priority(gap_score, difficulty_weight)
            }
        
        return gaps
    
    def _estimate_difficulty_gap(self, topic: str, coverage: float) -> float:
        """Estimate gap in hard problems for a topic"""
        if coverage < 40:
            return 2.0  # Major gap - need to focus
        elif coverage < 70:
            return 1.5  # Moderate gap
        else:
            return 1.0  # Well covered
    
    def _calculate_priority(self, gap_score: float, difficulty_weight: float) -> str:
        """Calculate priority for learning a topic"""
        priority_score = gap_score * difficulty_weight
        
        if priority_score > 150:
            return "critical"
        elif priority_score > 100:
            return "high"
        elif priority_score > 50:
            return "medium"
        else:
            return "low"
    
    def _identify_strengths(self, coverage: Dict[str, float]) -> List[str]:
        """Identify well-covered topics"""
        strengths = [
            topic for topic, pct in coverage.items()
            if pct >= 70
        ]
        return sorted(strengths, key=lambda t: coverage[t], reverse=True)
    
    def _recommend_next_topics(self, gaps: Dict[str, Any]) -> List[str]:
        """Recommend next topics to study based on gaps and priority"""
        priorities = defaultdict(list)
        
        for topic, gap_data in gaps.items():
            priority = gap_data["priority"]
            priorities[priority].append(topic)
        
        # Return topics in order: critical > high > medium
        recommendations = (
            priorities.get("critical", []) +
            priorities.get("high", []) +
            priorities.get("medium", [])
        )
        
        return recommendations[:5]  # Top 5 recommendations
    
    def generate_training_plan(self, gap_analysis: Dict[str, Any],
                              duration_days: int = 30,
                              daily_target: int = 5) -> Dict[str, Any]:
        """
        Generate a personalized training plan
        
        Args:
            gap_analysis: Results from analyze_learning_progress
            duration_days: How many days to prepare
            daily_target: Target problems to solve per day
            
        Returns:
            Detailed training plan with daily milestones
        """
        next_topics = gap_analysis["next_topics"]
        
        # Build plan with difficulty progression
        plan = {
            "duration_days": duration_days,
            "daily_target": daily_target,
            "total_problems": duration_days * daily_target,
            "topics": next_topics,
            "weekly_schedule": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Create weekly milestones
        weeks = (duration_days + 6) // 7
        problems_per_week = (duration_days * daily_target) // weeks
        
        for week in range(weeks):
            week_start = week * 7 + 1
            week_end = min((week + 1) * 7, duration_days)
            
            # Distribute topics across weeks
            topic_focus = next_topics[week % len(next_topics)]
            
            week_plan = {
                "week": week + 1,
                "days": f"{week_start}-{week_end}",
                "target_problems": problems_per_week,
                "primary_topic": topic_focus,
                "difficulty_progression": self._get_week_difficulty(week, weeks),
                "problems": self._select_problems_for_week(
                    topic_focus, problems_per_week, week, weeks
                )
            }
            
            plan["weekly_schedule"].append(week_plan)
        
        return plan
    
    def _get_week_difficulty(self, week: int, total_weeks: int) -> List[str]:
        """Get difficulty progression for the week"""
        if week < total_weeks // 3:
            return ["easy", "easy", "medium"]
        elif week < 2 * total_weeks // 3:
            return ["medium", "medium", "hard"]
        else:
            return ["hard", "hard", "hard"]
    
    def _select_problems_for_week(self, topic: str, count: int,
                                  week: int, total_weeks: int) -> List[Dict[str, str]]:
        """Select specific problems for the week"""
        if topic not in self.TUF_CURRICULUM:
            return []
        
        difficulties = self._get_week_difficulty(week, total_weeks)
        problems = []
        
        for difficulty in difficulties:
            if difficulty in self.TUF_CURRICULUM[topic]:
                available = self.TUF_CURRICULUM[topic][difficulty]
                prob_count = count // len(difficulties)
                selected = random.sample(available, min(prob_count, len(available)))
                
                for prob in selected:
                    problems.append({
                        "name": prob,
                        "difficulty": difficulty,
                        "topic": topic,
                        "url": f"https://takeuforward.org/{topic}/{prob}"
                    })
        
        return problems[:count]
    
    def generate_custom_problem(self, topic: str, difficulty: str,
                               focus_area: str = None) -> Dict[str, Any]:
        """
        Generate a custom problem prompt based on learning gaps
        
        Args:
            topic: DSA topic (arrays, linked-list, etc.)
            difficulty: easy/medium/hard
            focus_area: Specific weakness to focus on
            
        Returns:
            Custom problem statement and solution hints
        """
        if topic not in self.TUF_CURRICULUM:
            return {"error": f"Unknown topic: {topic}"}
        
        if difficulty not in self.TUF_CURRICULUM[topic]:
            return {"error": f"No {difficulty} problems for {topic}"}
        
        problem_name = random.choice(self.TUF_CURRICULUM[topic][difficulty])
        
        return {
            "topic": topic,
            "difficulty": difficulty,
            "problem_name": problem_name,
            "problem_url": f"https://takeuforward.org/{topic}/{problem_name}",
            "focus_area": focus_area or f"Master {topic} with {difficulty} problems",
            "hints": self._generate_hints(topic, difficulty),
            "time_limit_minutes": self._get_time_limit(difficulty),
            "expected_approach": self._get_approach(topic, difficulty)
        }
    
    def _generate_hints(self, topic: str, difficulty: str) -> List[str]:
        """Generate learning hints for the topic"""
        hints_map = {
            "arrays": {
                "easy": [
                    "Think about linear traversal",
                    "Consider space-time tradeoffs",
                    "Look for index manipulation patterns"
                ],
                "medium": [
                    "Two-pointer technique might help",
                    "Consider prefix/suffix arrays",
                    "Sliding window could optimize"
                ],
                "hard": [
                    "Combine multiple techniques",
                    "Think about edge cases",
                    "Optimize space and time complexity"
                ]
            },
            "linked-list": {
                "easy": [
                    "Draw out the linked list",
                    "Think about pointer updates",
                    "Handle edge cases (null pointers)"
                ],
                "medium": [
                    "Use slow/fast pointer technique",
                    "Track previous node",
                    "Consider recursion"
                ],
                "hard": [
                    "Complex pointer manipulations",
                    "Merge sorted structures",
                    "Cycle detection patterns"
                ]
            },
            "binary-search": {
                "easy": [
                    "Search space halves each step",
                    "Define search boundaries clearly",
                    "Be careful with mid calculation"
                ],
                "medium": [
                    "Modified binary search needed",
                    "Search answer space",
                    "Think about invariants"
                ],
                "hard": [
                    "Complex search conditions",
                    "2D binary search",
                    "Non-obvious search space"
                ]
            }
        }
        
        return hints_map.get(topic, {}).get(difficulty, [
            "Break down the problem",
            "Start with brute force",
            "Optimize incrementally"
        ])
    
    def _get_time_limit(self, difficulty: str) -> int:
        """Get time limit in minutes based on difficulty"""
        return {"easy": 15, "medium": 30, "hard": 45}.get(difficulty, 30)
    
    def _get_approach(self, topic: str, difficulty: str) -> str:
        """Get recommended approach for solving"""
        approaches = {
            "arrays": "Consider position, values, and relationships. Use two-pointer, sliding window, or prefix sum techniques.",
            "linked-list": "Visualize nodes and pointers. Use slow-fast pointer for cycles. Be careful with pointer reassignments.",
            "binary-search": "Identify search space. Define mid and compare. Handle edge cases in boundaries.",
            "recursion": "Define base case clearly. Think about problem reduction. Consider memoization for optimization.",
            "hashing": "Use hash maps/sets for O(1) lookups. Be mindful of collisions and space complexity.",
            "sorting": "Consider comparison vs counting sort. Think about stability and in-place requirements.",
            "dynamic-programming": "Define states clearly. Find recurrence relation. Identify overlapping subproblems.",
            "graphs": "Model as graph. Choose BFS/DFS. Track visited nodes and handle cycles."
        }
        
        return approaches.get(topic, "Analyze the problem systematically and build incrementally.")
    
    def track_training_session(self, user_id: str, topic: str, problem: str,
                              difficulty: str, status: str = "completed",
                              time_spent: int = 0, attempts: int = 1):
        """Track a training session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_sessions
            (user_id, topic, difficulty, problem_name, status, time_spent, attempts)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, topic, difficulty, problem, status, time_spent, attempts))
        
        conn.commit()
        conn.close()
    
    def get_training_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get training statistics for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM training_sessions'
        params = []
        
        if user_id:
            query += ' WHERE user_id = ?'
            params.append(user_id)
        
        cursor.execute(query, params)
        sessions = cursor.fetchall()
        conn.close()
        
        if not sessions:
            return {"total_sessions": 0, "topics": {}}
        
        stats = {
            "total_sessions": len(sessions),
            "topics": defaultdict(dict),
            "total_time_minutes": 0,
            "avg_attempts": 0
        }
        
        for session in sessions:
            topic = session[2]
            stats["topics"][topic] = stats["topics"].get(topic, 0) + 1
            stats["total_time_minutes"] += session[6] or 0
            stats["avg_attempts"] += session[7] or 0
        
        stats["avg_attempts"] = round(stats["avg_attempts"] / len(sessions), 2)
        
        return stats


def main():
    """Example usage"""
    agent = AdaptiveLearningAgent()
    
    # Example with sample progress data
    progress_sample = {
        "success": True,
        "totalProblems": 131,
        "recentProgress": [
            {
                "problemId": "arrays_arrays_faqs_twosum",
                "problem_slug": "two-sum",
                "problemName": "Two Sum",
                "difficulty": "Easy",
                "date": 1756126266133
            }
        ]
    }
    
    # Analyze progress
    analysis = agent.analyze_learning_progress(progress_sample)
    print("\n=== Learning Analysis ===")
    print(f"Total Solved: {analysis['total_solved']}")
    print(f"Next Topics: {analysis['next_topics'][:3]}")
    print(f"Strengths: {analysis['strengths'][:3]}")
    
    # Generate training plan
    plan = agent.generate_training_plan(analysis, duration_days=30, daily_target=5)
    print("\n=== Training Plan ===")
    print(f"Total Problems: {plan['total_problems']}")
    print(f"Duration: {plan['duration_days']} days")
    
    # Generate custom problem
    custom_prob = agent.generate_custom_problem("arrays", "medium", "sliding-window")
    print("\n=== Custom Problem ===")
    print(f"Topic: {custom_prob['topic']}")
    print(f"Problem: {custom_prob['problem_name']}")
    print(f"Hints: {custom_prob['hints'][:2]}")


if __name__ == "__main__":
    main()
