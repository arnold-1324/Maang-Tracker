# maang_agent/agent.py

import asyncio
import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

INSTR = """
You are MAANG Mentor — strict, technical, complexity-focused.
You MUST use MCP tools when asked: GitHub, LeetCode, GeeksforGeeks.
"""

async def build_agent():
    conn = StreamableHTTPConnectionParams(
        url="http://localhost:9000/mcp"   # <-- your MCP server
    )

    mcp_toolset = await MCPToolset.from_server(connection_params=conn)
    tools = list(mcp_toolset.get_tools())
    tools.append(PreloadMemoryTool())

    agent = Agent(
        name="maang_agent",
        model="gemini-2.0-flash",  # works with ADK
        instruction=INSTR,
        tools=tools,
        description="MAANG Mentor Root Agent"
    )
    return agent

async def root_agent():
    return await build_agent()
