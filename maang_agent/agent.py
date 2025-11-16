import os
from datetime import datetime
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from maang_agent.memory_persistence import get_memory_manager
from typing import Optional

INSTR = """
You are MAANG Mentor, an expert AI interviewer and career coach for MAANG preparation.

Your responsibilities:
1. Conduct real-time coding interviews with immediate feedback
2. Assess system design capabilities and provide architectural guidance
3. Evaluate behavioral interview responses with empathy and guidance
4. Track user progress across Data Structures, Algorithms, System Design, and Behavioral topics
5. Provide personalized recommendations based on performance patterns
6. Remember user's learning history and adapt difficulty accordingly
7. Verify mastery through follow-up questions before progressing
8. Use MCP tools (GitHub, LeetCode, GFG) to validate external progress

Interview Conduct:
- Be strict but fair in code review - focus on optimization and best practices
- Emphasize complexity analysis for every solution
- Ask follow-up questions to verify deep understanding
- Provide contextual hints, not direct solutions
- Track time efficiency and code quality

Memory Management:
- Store all conversation history for later analysis
- Track topics covered and proficiency levels
- Record performance metrics and improvement areas
- Generate adaptive learning recommendations
- Verify mastery before marking topics as complete
"""

async def build_root_agent():
    """Build the agent with MCP tools from the running MCP server."""
    try:
        conn = StreamableHTTPConnectionParams(url="http://localhost:8765/mcp")
        toolset = await MCPToolset.from_server(connection_params=conn)
        tools = list(toolset.get_tools())
    except Exception:
        # Fallback if MCP server not available
        tools = []

    agent = Agent(
        name="maang_mentor",
        model="gemini-2.0-flash",
        instruction=INSTR,
        tools=tools
    )
    return agent


class MaangMentorWithMemory:
    """Wrapper for Google AI Agent with memory persistence and progress tracking"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memory_manager = get_memory_manager()
        self.current_session_id = None
    
    def start_session(self, session_id: str, session_type: str, context: dict):
        """Start a new interview session with memory tracking"""
        self.current_session_id = session_id
        
        # Store session initialization in memory
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='system',
            message=f'Session started: {session_type}',
            metadata={
                'session_type': session_type,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def process_user_input(self, message: str, context: dict) -> str:
        """Process user input and store in memory"""
        # Store user message
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=self.current_session_id,
            role='user',
            message=message,
            metadata=context
        )
        
        # Here you would integrate with the actual Google AI agent
        # For now, return a placeholder
        return f"Processing: {message}"
    
    def store_feedback(
        self, 
        feedback: str, 
        score: float, 
        assessment: dict
    ):
        """Store interview feedback and assessment"""
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=self.current_session_id,
            role='assistant',
            message=feedback,
            metadata={
                'score': score,
                'assessment': assessment,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def track_topic_progress(self, topic: str, category: str, proficiency: int):
        """Track progress on specific topics"""
        self.memory_manager.track_topic_coverage(
            user_id=self.user_id,
            topic=topic,
            category=category,
            status='learning' if proficiency < 3 else 'mastered',
            proficiency_level=proficiency
        )
    
    def record_problem_attempt(
        self, 
        problem_id: str, 
        problem_name: str,
        category: str,
        time_minutes: int,
        optimal: bool
    ):
        """Record problem solving attempt"""
        self.memory_manager.track_problem_attempt(
            user_id=self.user_id,
            problem_id=problem_id,
            problem_name=problem_name,
            category=category,
            time_to_solve_minutes=time_minutes,
            optimal_solution_found=optimal
        )
    
    def get_progress_summary(self) -> dict:
        """Get user's current progress summary"""
        return self.memory_manager.get_user_summary(self.user_id)
    
    def get_conversation_context(self, limit: int = 10) -> list:
        """Get recent conversation context for AI agent"""
        return self.memory_manager.get_conversation_history(
            user_id=self.user_id,
            limit=limit
        )
    
    def recommend_next_topic(self) -> Optional[str]:
        """AI agent recommends next topic based on progress"""
        summary = self.get_progress_summary()
        history = self.memory_manager.get_topic_coverage(self.user_id)
        
        # Find topics with lowest proficiency
        incomplete = [t for t in history if t['proficiency_level'] < 3]
        if incomplete:
            return incomplete[0]['topic']
        return None


# Module-level root_agent instance so ADK loader finds a BaseAgent at import time
root_agent = Agent(
    name="maang_mentor",
    model="gemini-2.0-flash",
    instruction=INSTR,
    tools=[]
)

# Global mentor instance factory
_mentor_instances = {}

def get_mentor(user_id: str) -> MaangMentorWithMemory:
    """Get or create mentor instance for user"""
    if user_id not in _mentor_instances:
        _mentor_instances[user_id] = MaangMentorWithMemory(user_id)
    return _mentor_instances[user_id]
