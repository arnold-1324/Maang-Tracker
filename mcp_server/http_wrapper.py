"""
Simple HTTP wrapper for MCP tools to provide REST API endpoints.
This wraps the FastMCP server with a Flask API that tracker.py can call.
"""
import os
import sys
import asyncio
import inspect
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import the MCP server
sys.path.insert(0, os.path.dirname(__file__))
from server import mcp

app = Flask(__name__)
CORS(app)

def run_async(coro):
    """Helper to run async functions in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # If loop is already running, create a new one
        loop = asyncio.new_event_loop()
    
    return loop.run_until_complete(coro)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "MCP HTTP Wrapper"})

@app.route('/tools', methods=['GET'])
def list_tools():
    """List all available MCP tools"""
    try:
        tools_result = mcp.list_tools()
        if inspect.iscoroutine(tools_result):
            tools_result = run_async(tools_result)
        return jsonify({"success": True, "tools": tools_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/call/<tool_name>', methods=['POST'])
def call_tool(tool_name):
    """Call an MCP tool by name"""
    try:
        params = request.json or {}
        result = mcp.call_tool(tool_name, params)
        
        # If result is a coroutine, await it
        if inspect.iscoroutine(result):
            result = run_async(result)
        
        # Extract content from MCP result object
        result_data = extract_mcp_result(result)
            
        return jsonify({"success": True, "result": result_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/invoke', methods=['POST'])
def invoke():
    """Generic invoke endpoint (MCP-style)"""
    try:
        data = request.json
        tool_name = data.get('tool')
        args = data.get('args', {})
        
        if not tool_name:
            return jsonify({"success": False, "error": "Missing 'tool' parameter"}), 400
            
        result = mcp.call_tool(tool_name, args)
        
        # If result is a coroutine, await it
        if inspect.iscoroutine(result):
            result = run_async(result)
        
        # Extract content from MCP result object
        result_data = extract_mcp_result(result)
            
        return jsonify({"success": True, "result": result_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

def extract_mcp_result(result):
    """Extract JSON-serializable data from MCP result objects"""
    import json
    
    # print(f"DEBUG: MCP Result type: {type(result)}")
    # print(f"DEBUG: MCP Result: {result}")

    if isinstance(result, list):
        if len(result) > 0:
            first_item = result[0]
            if hasattr(first_item, 'text'):
                text = first_item.text
                try:
                    return json.loads(text)
                except:
                    return {"text": text}
            elif isinstance(first_item, dict) and 'text' in first_item:
                 # Handle dict representation of TextContent
                text = first_item['text']
                try:
                    return json.loads(text)
                except:
                    return {"text": text}
        return {"value": str(result)}

    if hasattr(result, 'content'):
        # MCP returns a result object with content attribute
        content = result.content
        if isinstance(content, list) and len(content) > 0:
            # Get the first content item
            first_item = content[0]
            if hasattr(first_item, 'text'):
                # Text content - extract the text string
                text = first_item.text
                try:
                    # Try to parse as JSON
                    return json.loads(text)
                except:
                    return {"text": text}
            elif hasattr(first_item, 'type'):
                # Has type attribute, convert to dict
                return {"type": first_item.type, "value": str(first_item)}
            else:
                return {"value": str(first_item)}
        else:
            return {"value": str(content)}
    elif isinstance(result, dict):
        return result
    elif isinstance(result, (str, int, float, bool, type(None))):
        return result
    else:
        return {"value": str(result)}

if __name__ == '__main__':
    port = int(os.getenv('MCP_PORT', 8765))
    print(f"Starting MCP HTTP Wrapper on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
