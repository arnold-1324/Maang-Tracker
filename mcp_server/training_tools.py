"""
MCP Tools for Adaptive Training Agent
Exposes training functionality through FastMCP
"""

from fastmcp import mcp
from training.adaptive_learning_agent import AdaptiveLearningAgent
import json


# Initialize agent
agent = AdaptiveLearningAgent()


@mcp.tool()
def analyze_dsa_progress(progress_json: str) -> str:
    """
    Analyze your DSA learning progress and identify gaps
    
    Args:
        progress_json: Your TakeUForward progress data (JSON string)
        
    Returns:
        Analysis with topic coverage, gaps, and recommendations
    """
    try:
        progress_data = json.loads(progress_json)
        analysis = agent.analyze_learning_progress(progress_data)
        return json.dumps(analysis, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def generate_training_plan(progress_json: str, duration_days: int = 30,
                          daily_target: int = 5) -> str:
    """
    Generate a personalized 30-day training plan
    
    Args:
        progress_json: Your TakeUForward progress data (JSON string)
        duration_days: How many days to prepare (default: 30)
        daily_target: Target problems per day (default: 5)
        
    Returns:
        Detailed training plan with weekly milestones and specific problems
    """
    try:
        progress_data = json.loads(progress_json)
        analysis = agent.analyze_learning_progress(progress_data)
        plan = agent.generate_training_plan(analysis, duration_days, daily_target)
        return json.dumps(plan, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_custom_problem(topic: str, difficulty: str, focus_area: str = None) -> str:
    """
    Get a custom problem recommendation based on your learning goals
    
    Args:
        topic: DSA topic (arrays, linked-list, binary-search, recursion,
               hashing, sorting, dynamic-programming, graphs)
        difficulty: easy, medium, or hard
        focus_area: Specific weakness to focus on (optional)
        
    Returns:
        Custom problem with hints, time limit, and approach
    """
    try:
        problem = agent.generate_custom_problem(topic, difficulty, focus_area)
        return json.dumps(problem, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def identify_weak_topics(progress_json: str) -> str:
    """
    Identify your weakest DSA topics that need most focus
    
    Args:
        progress_json: Your TakeUForward progress data (JSON string)
        
    Returns:
        Ranked list of weak topics with coverage percentages
    """
    try:
        progress_data = json.loads(progress_json)
        analysis = agent.analyze_learning_progress(progress_data)
        
        gaps = analysis["gaps"]
        sorted_gaps = sorted(
            gaps.items(),
            key=lambda x: x[1]["gap_score"],
            reverse=True
        )
        
        weak_topics = {
            "weak_areas": [
                {
                    "topic": topic,
                    "coverage": gap["coverage_pct"],
                    "gap_score": gap["gap_score"],
                    "priority": gap["priority"]
                }
                for topic, gap in sorted_gaps[:5]
            ],
            "recommended_focus": analysis["next_topics"][:3],
            "total_problems_solved": analysis["total_solved"]
        }
        
        return json.dumps(weak_topics, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_tuf_curriculum(topic: str = None) -> str:
    """
    Get the complete TakeUForward curriculum structure
    
    Args:
        topic: Specific topic to get problems for (optional).
               If not provided, returns all available topics.
               
    Returns:
        Curriculum with easy/medium/hard problems for specified or all topics
    """
    try:
        if topic and topic in agent.TUF_CURRICULUM:
            curriculum = {topic: agent.TUF_CURRICULUM[topic]}
        else:
            curriculum = agent.TUF_CURRICULUM if not topic else {}
        
        # Convert to displayable format
        output = {}
        for t, difficulties in curriculum.items():
            output[t] = {
                d: len(problems) for d, problems in difficulties.items()
            }
        
        return json.dumps(output, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def calculate_study_hours(topics: str, difficulty_level: str = "mixed") -> str:
    """
    Calculate estimated study hours needed for topics
    
    Args:
        topics: Comma-separated list of topics (e.g., "arrays,linked-list,recursion")
        difficulty_level: easy, medium, hard, or mixed
        
    Returns:
        Estimated study hours and resource recommendations
    """
    try:
        topic_list = [t.strip() for t in topics.split(",")]
        
        # Time estimates (hours per problem)
        time_estimates = {
            "easy": 0.5,
            "medium": 1.0,
            "hard": 1.5
        }
        
        total_hours = 0
        problem_count = 0
        
        for topic in topic_list:
            if topic in agent.TUF_CURRICULUM:
                for difficulty, problems in agent.TUF_CURRICULUM[topic].items():
                    if difficulty_level == "mixed" or difficulty == difficulty_level:
                        hours_per_problem = time_estimates.get(difficulty, 1.0)
                        problem_count += len(problems)
                        total_hours += len(problems) * hours_per_problem
        
        # Add review time (20% extra)
        total_with_review = total_hours * 1.2
        
        return json.dumps({
            "topics": topic_list,
            "total_problems": problem_count,
            "estimated_hours": round(total_hours, 1),
            "with_review_and_practice": round(total_with_review, 1),
            "recommended_daily_hours": round(total_with_review / 30, 1),
            "note": "Times are estimates; actual time depends on your familiarity with topics"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def get_interview_prep_roadmap(experience_level: str = "intermediate") -> str:
    """
    Get a MAANG interview preparation roadmap
    
    Args:
        experience_level: beginner, intermediate, or advanced
        
    Returns:
        Complete interview prep roadmap with timeline and focus areas
    """
    try:
        roadmaps = {
            "beginner": {
                "duration_weeks": 16,
                "weekly_problems": 15,
                "phases": [
                    {
                        "week": 1-4,
                        "focus": "Arrays & Strings Fundamentals",
                        "topics": ["arrays", "strings"],
                        "goal": "Master basic operations and patterns"
                    },
                    {
                        "week": 5-8,
                        "focus": "Linked Lists & Sorting",
                        "topics": ["linked-list", "sorting"],
                        "goal": "Pointer manipulation and sorting algorithms"
                    },
                    {
                        "week": 9-12,
                        "focus": "Trees & Graphs Basics",
                        "topics": ["binary-search", "recursion"],
                        "goal": "Recursive thinking and traversals"
                    },
                    {
                        "week": 13-16,
                        "focus": "Dynamic Programming & Review",
                        "topics": ["dynamic-programming", "hashing"],
                        "goal": "Optimization and final preparation"
                    }
                ]
            },
            "intermediate": {
                "duration_weeks": 10,
                "weekly_problems": 20,
                "phases": [
                    {
                        "week": 1-3,
                        "focus": "Advanced Arrays & Strings",
                        "topics": ["arrays", "strings"],
                        "goal": "Hard problems and advanced patterns"
                    },
                    {
                        "week": 4-6,
                        "focus": "Trees, Graphs & DP",
                        "topics": ["graphs", "dynamic-programming"],
                        "goal": "Complex data structures and optimization"
                    },
                    {
                        "week": 7-10,
                        "focus": "System Design & Review",
                        "topics": ["all"],
                        "goal": "Mock interviews and edge cases"
                    }
                ]
            },
            "advanced": {
                "duration_weeks": 6,
                "weekly_problems": 25,
                "phases": [
                    {
                        "week": 1-2,
                        "focus": "Hard Problems Deep Dive",
                        "topics": ["all"],
                        "goal": "Master difficult patterns"
                    },
                    {
                        "week": 3-4,
                        "focus": "Company-Specific Questions",
                        "topics": ["all"],
                        "goal": "LeetCode premium company questions"
                    },
                    {
                        "week": 5-6,
                        "focus": "Mock Interviews & Polish",
                        "topics": ["all"],
                        "goal": "Full mock interview simulation"
                    }
                ]
            }
        }
        
        return json.dumps(roadmaps.get(experience_level, roadmaps["intermediate"]), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# Export for FastMCP server
__all__ = [
    "analyze_dsa_progress",
    "generate_training_plan",
    "get_custom_problem",
    "identify_weak_topics",
    "get_tuf_curriculum",
    "calculate_study_hours",
    "get_interview_prep_roadmap"
]
