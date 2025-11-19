import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

INSTR = """
You are MAANG Mentor, an expert AI interviewer and career coach for MAANG preparation.

Your responsibilities:
1. Conduct real-time coding interviews with immediate feedback
2. Assess system design capabilities and provide architectural guidance
3. Evaluate behavioral interview responses with empathy and guidance
4. Track user progress across Data Structures, Algorithms, System Design, and Behavioral topics
5. Provide personalized recommendations based on performance patterns

Interview Conduct:
- Be strict but fair in code review - focus on optimization and best practices
- Emphasize complexity analysis for every solution
- Ask follow-up questions to verify deep understanding
- Provide contextual hints, not direct solutions
- Track time efficiency and code quality
"""

async def build_agent():
    """Build the MAANG Mentor agent with MCP tools"""
    # Try to connect to MCP server
    tools = []
    try:
        # Try port 8765 first (current MCP server)
        conn = StreamableHTTPConnectionParams(url="http://localhost:8765/mcp")
        mcp_toolset = await MCPToolset.from_server(connection_params=conn)
        tools = list(mcp_toolset.get_tools())
        print(f"✓ Connected to MCP server, loaded {len(tools)} tools")
    except Exception as e:
        print(f"⚠ MCP server not available: {e}")
        print("Agent will run without MCP tools")
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠ WARNING: GOOGLE_API_KEY not found in environment!")
        print("  Please set it in .env.local file")
    
    # Build agent with API key
    agent = Agent(
        name="maang_mentor",
        model="gemini-2.0-flash-exp",
        instruction=INSTR,
        tools=tools,
        description="MAANG Mentor - Your AI Interview Coach",
        api_key=api_key  # Explicitly pass API key
    )
    
    return agent

async def root_agent():
    """Entry point for ADK"""
    return await build_agent()

# For direct testing
if __name__ == "__main__":
    async def test():
        agent = await build_agent()
        print(f"✓ Agent created: {agent.name}")
        print(f"✓ Model: {agent.model}")
        print(f"✓ Tools: {len(agent.tools) if hasattr(agent, 'tools') else 0}")
    
    asyncio.run(test())
