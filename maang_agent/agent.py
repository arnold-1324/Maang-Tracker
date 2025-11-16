import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from maang_agent.memory_persistence import get_memory_manager
from typing import Optional, Dict, List, Any

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
        self.agent = None
        self.user_data_dir = Path("userData")
        self.user_data_dir.mkdir(exist_ok=True)
        self._init_agent()
    
    def _init_agent(self):
        """Initialize Google AI Agent"""
        try:
            # Try to build agent with MCP tools
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.agent = loop.run_until_complete(build_root_agent())
        except Exception as e:
            # Fallback to basic agent
            self.agent = Agent(
                name="maang_mentor",
                model="gemini-2.0-flash",
                instruction=INSTR,
                tools=[]
            )
    
    def start_session(self, session_id: str, session_type: str, context: dict):
        """Start a new interview session with memory tracking"""
        self.current_session_id = session_id
        
        # Get relevant conversation context using RAG
        rag_context = self.memory_manager.get_rag_context(
            user_id=self.user_id,
            session_type=session_type,
            limit=5
        )
        
        # Store session initialization in memory
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=session_id,
            role='system',
            message=f'Session started: {session_type}',
            metadata={
                'session_type': session_type,
                'context': context,
                'rag_context': rag_context,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Backup to userData directory
        self._backup_conversation_to_json()
    
    def process_user_input(self, message: str, context: dict) -> str:
        """Process user input and store in memory, then get AI response"""
        # Store user message
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=self.current_session_id,
            role='user',
            message=message,
            metadata=context
        )
        
        # Get conversation context using RAG
        conversation_history = self.memory_manager.get_conversation_history(
            user_id=self.user_id,
            session_id=self.current_session_id,
            limit=10
        )
        
        # Get relevant past conversations for context
        rag_context = self.memory_manager.get_rag_context(
            user_id=self.user_id,
            query=message,
            limit=3
        )
        
        # Build context for AI agent
        context_prompt = self._build_context_prompt(conversation_history, rag_context, context)
        
        # Get AI response from Google Agent
        try:
            if self.agent:
                # Use agent's chat method if available
                full_message = context_prompt + "\n\nUser: " + message + "\n\nAssistant:"
                # For now, use a simple approach - in production, use agent's actual chat API
                response = self._get_agent_response(full_message)
            else:
                response = "I'm processing your request. Please wait while I analyze your progress."
        except Exception as e:
            response = f"I encountered an issue: {str(e)}. Let me help you with your question."
        
        # Store AI response
        self.memory_manager.store_conversation(
            user_id=self.user_id,
            session_id=self.current_session_id,
            role='assistant',
            message=response,
            metadata={'rag_used': len(rag_context) > 0}
        )
        
        # Backup conversation
        self._backup_conversation_to_json()
        
        return response
    
    def _build_context_prompt(self, history: List[Dict], rag_context: List[Dict], current_context: Dict) -> str:
        """Build context prompt from conversation history and RAG context"""
        prompt_parts = []
        
        # Add RAG context if available
        if rag_context:
            prompt_parts.append("Relevant past conversations:")
            for ctx in rag_context:
                prompt_parts.append(f"- {ctx.get('message', '')[:200]}")
        
        # Add recent conversation history
        if history:
            prompt_parts.append("\nRecent conversation:")
            for msg in history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                msg_text = msg.get('message', '')[:150]
                prompt_parts.append(f"{role.capitalize()}: {msg_text}")
        
        # Add current context
        if current_context:
            prompt_parts.append(f"\nCurrent context: {json.dumps(current_context, indent=2)}")
        
        return "\n".join(prompt_parts)
    
    def _get_agent_response(self, prompt: str) -> str:
        """Get response from Google AI Agent"""
        # This is a placeholder - in production, use the actual agent API
        # For now, return a contextual response
        if "code" in prompt.lower() or "solution" in prompt.lower():
            return "Let me review your code. Focus on time complexity and edge cases. What approach are you considering?"
        elif "help" in prompt.lower() or "stuck" in prompt.lower():
            return "I can help! Let's break down the problem step by step. What part are you finding challenging?"
        else:
            return "I understand. Let's continue working on this together. What would you like to focus on next?"
    
    def _backup_conversation_to_json(self):
        """Backup conversation history to userData directory as JSON"""
        try:
            history = self.memory_manager.get_conversation_history(
                user_id=self.user_id,
                session_id=self.current_session_id,
                limit=1000
            )
            
            backup_file = self.user_data_dir / f"{self.user_id}_conversation_backup.json"
            
            # Load existing backup if it exists
            existing_data = []
            if backup_file.exists():
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []
            
            # Merge with new history (avoid duplicates)
            existing_ids = {msg.get('id') for msg in existing_data if 'id' in msg}
            new_messages = [msg for msg in history if msg.get('id') not in existing_ids]
            
            # Update backup
            updated_data = existing_data + new_messages
            
            # Save backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, default=str)
                
        except Exception as e:
            # Silently fail backup - don't break main functionality
            pass
    
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
