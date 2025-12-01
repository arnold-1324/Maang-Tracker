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

    
    # Ensure env vars are loaded
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    load_dotenv()

    agent = Agent(
        name="maang_mentor",
        model="gemini-2.0-flash",
        instruction=INSTR,
        tools=tools,
        api_key=os.getenv("GOOGLE_API_KEY")
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
        try:
            # Use the Google ADK agent
            if self.agent:
                # Try to run the agent with the prompt
                try:
                    # The agent needs to be run in an async context
                    import asyncio
                    
                    async def get_response():
                        # Send message to agent
                        response = await self.agent.send_message(prompt)
                        return response
                    
                    # Run the async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(get_response())
                    loop.close()
                    
                    # Extract text from response
                    if hasattr(result, 'text'):
                        return result.text
                    elif isinstance(result, str):
                        return result
                    else:
                        return str(result)
                    
                except Exception as e:
                    print(f"Agent call error: {e}")
                    # Fallback to contextual response
                    return self._get_contextual_fallback(prompt)
            else:
                return self._get_contextual_fallback(prompt)
        except Exception as e:
            print(f"Response generation error: {e}")
            return "I'm here to help. Could you rephrase your question?"
    
    def _get_contextual_fallback(self, prompt: str) -> str:
        """Provide contextual fallback responses based on prompt analysis"""
        prompt_lower = prompt.lower()
        
        # Educational requests - teach me X
        if any(word in prompt_lower for word in ["teach", "explain", "learn", "what is", "tell me about"]):
            # Linked List teaching
            if "linked list" in prompt_lower or "linkedlist" in prompt_lower:
                return """**Linked List - Complete Guide**

A Linked List is a linear data structure where elements (nodes) are connected via pointers.

**Structure:**
Each node contains:
- Data (value)
- Pointer to next node

**Types:**
1. **Singly Linked List**: Each node points to the next
2. **Doubly Linked List**: Each node has prev & next pointers
3. **Circular Linked List**: Last node points back to first

**Key Operations & Time Complexity:**
- Access: O(n) - must traverse from head
- Search: O(n) - linear search
- Insert at head: O(1)
- Insert at tail: O(n) without tail pointer, O(1) with tail
- Delete: O(n) to find, O(1) to remove

**When to Use:**
✓ Frequent insertions/deletions at beginning
✓ Unknown size, dynamic growth
✓ Don't need random access

**Common Problems:**
1. Reverse a Linked List
2. Detect Cycle (Floyd's Algorithm)
3. Merge Two Sorted Lists
4. Find Middle Node (Fast & Slow Pointers)

**Practice:** Start with reversing a list, then try cycle detection!

What specific aspect would you like to dive deeper into?"""
            
            # Array teaching
            elif "array" in prompt_lower:
                return """**Arrays - Comprehensive Guide**

Arrays are contiguous memory blocks storing elements of the same type.

**Characteristics:**
- Fixed size (in most languages)
- O(1) random access via index
- Cache-friendly (contiguous memory)

**Operations & Complexity:**
- Access: O(1)
- Search: O(n) unsorted, O(log n) sorted (binary search)
- Insert at end: O(1) amortized
- Insert at middle: O(n) due to shifting
- Delete: O(n) due to shifting

**Common Patterns:**
1. **Two Pointers**: Two Sum, Container With Most Water
2. **Sliding Window**: Max sum subarray, Longest substring
3. **Kadane's Algorithm**: Maximum subarray sum
4. **Prefix Sum**: Range queries

**Interview Tips:**
- Always ask: sorted? duplicates allowed?
- Consider in-place operations to save space
- Watch for edge cases: empty, single element

Ready to practice? Try "Two Sum" or "Best Time to Buy Stock"!"""
            
            # Tree teaching
            elif "tree" in prompt_lower or "binary tree" in prompt_lower:
                return """**Binary Trees - Master Guide**

A hierarchical data structure with nodes connected by edges.

**Key Concepts:**
- **Root**: Top node
- **Parent/Child**: Direct connections
- **Leaf**: Node with no children
- **Depth**: Distance from root
- **Height**: Longest path to leaf

**Types:**
1. **Binary Tree**: Each node has ≤ 2 children
2. **BST**: Left < Node < Right (sorted property)
3. **Balanced Tree**: Height difference ≤ 1 (AVL, Red-Black)
4. **Complete Tree**: All levels filled except possibly last

**Traversals:**
- **Preorder**: Root → Left → Right (DFS)
- **Inorder**: Left → Root → Right (sorted for BST)
- **Postorder**: Left → Right → Root
- **Level Order**: BFS, level by level

**Common Problems:**
1. Invert Binary Tree
2. Maximum Depth
3. Validate BST
4. Lowest Common Ancestor (LCA)

**Master Pattern:** Most tree problems use recursion!

Which tree concept should we explore?"""
            
            # Graph teaching
            elif "graph" in prompt_lower:
                return """**Graphs - Complete Masterclass**

Non-linear data structure with vertices (nodes) and edges (connections).

**Representations:**
1. **Adjacency Matrix**: 2D array, O(V²) space, O(1) edge check
2. **Adjacency List**: Dict/Array of lists, O(V+E) space, better for sparse

**Graph Types:**
- **Directed** vs **Undirected**
- **Weighted** vs **Unweighted**
- **Cyclic** vs **Acyclic** (DAG)
- **Connected** vs **Disconnected**

**Essential Algorithms:**
1. **DFS (Depth-First Search)**: Stack/Recursion, O(V+E)
   - Use: Cycle detection, path finding, topological sort
   
2. **BFS (Breadth-First Search)**: Queue, O(V+E)
   - Use: Shortest path (unweighted), level-order

3. **Dijkstra's Algorithm**: Shortest path (weighted, no negative)
4. **Bellman-Ford**: Handles negative weights
5. **Topological Sort**: Order for prerequisites

**Common Patterns:**
- Number of Islands (DFS/BFS + visited set)
- Course Schedule (Cycle detection in DAG)
- Clone Graph (DFS with HashMap)

**Start Here:** Implement DFS and BFS, then solve "Number of Islands"!

What graph topic interests you most?"""
            
            # Dynamic Programming
            elif "dynamic programming" in prompt_lower or "dp" in prompt_lower:
                return """**Dynamic Programming - The Ultimate Guide**

DP optimizes recursive solutions by storing overlapping subproblem results.

**When to Use DP:**
1. **Optimal Substructure**: Solution built from subproblems
2. **Overlapping Subproblems**: Same calculations repeated

**Approaches:**
1. **Top-Down (Memoization)**: Recursion + cache
   - More intuitive
   - Only computes needed states
   
2. **Bottom-Up (Tabulation)**: Iterative DP table
   - Usually faster (no recursion overhead)
   - Computes all states

**DP Steps:**
1. Define state: `dp[i]` = ?
2. Find recurrence relation: `dp[i] = f(dp[i-1], dp[i-2], ...)`
3. Base cases: `dp[0] = ?`
4. Iteration order: Bottom-up or top-down?
5. Final answer: `dp[n]` or `max(dp)`

**Classic Patterns:**
1. **1D DP**: Fibonacci, Climbing Stairs, House Robber
2. **2D DP**: Longest Common Subsequence, Edit Distance
3. **Knapsack**: 0/1 Knapsack, Coin Change
4. **Strings**: Palindrome, Subsequence problems

**Learning Path:**
1. Start: Climbing Stairs, Fibonacci
2. Then: House Robber, Coin Change
3. Advanced: LCS, Edit Distance, Knapsack

**Pro Tip:** First solve recursively, then add memoization!

Which DP pattern should we tackle first?"""
            
            # Hash Map/Hash Table
            elif "hash" in prompt_lower:
                return """**Hash Maps - Complete Tutorial**

Hash Maps (Hash Tables) store key-value pairs with O(1) average operations.

**How It Works:**
1. Hash function converts key → index
2. Handle collisions (chaining or open addressing)
3. Resize when load factor exceeds threshold

**Operations:**
- Insert: O(1) average
- Lookup: O(1) average
- Delete: O(1) average
- Worst case: O(n) if many collisions

**Python Types:**
- `dict`: Hash map
- `set`: Hash set (keys only)
- `Counter`: Count frequencies
- `defaultdict`: Auto-initialize values

**Common Patterns:**
1. **Frequency Counter**: Count occurrences
2. **Complement Pattern**: Two Sum (store complement)
3. **Grouping**: Group anagrams
4. **Caching**: Seen elements, memoization

**Top Problems:**
1. Two Sum
2. Group Anagrams
3. Longest Substring Without Repeating
4. Subarray Sum Equals K

**Interview Gold:** Hash maps are THE solution for O(n) time complexity!

Want to solve Two Sum together?"""
            
            # Stack and Queue
            elif "stack" in prompt_lower or "queue" in prompt_lower:
                return """**Stacks & Queues - Essential Guide**

**STACK (LIFO - Last In First Out)**
Operations: `push()`, `pop()`, `peek()`
- All O(1) operations
- Uses: Function calls, undo/redo, DFS, expression evaluation

**QUEUE (FIFO - First In First Out)**
Operations: `enqueue()`, `dequeue()`, `front()`
- All O(1) operations  
- Uses: BFS, task scheduling, buffering

**Implementations:**
- Stack: Array or Linked List
- Queue: Linked List (efficient) or Circular Array
- Deque: Double-ended queue (both ends)

**Classic Problems:**
**Stack:**
1. Valid Parentheses
2. Min Stack (track minimum)
3. Daily Temperatures
4. Largest Rectangle in Histogram

**Queue:**
1. Implement Queue using Stacks
2. Moving Average
3. Design Circular Queue

**Pro Pattern:** Use stack for matching/balancing, queue for ordering/scheduling!

Which would you like to implement?"""
            
            # Default teaching response
            else:
                return f"I'd love to teach you about this topic! Could you be more specific? For example:\n- 'Teach me Linked Lists'\n- 'Explain dynamic programming'\n- 'How do binary search trees work?'\n\nI can provide detailed explanations for algorithms and data structures!"

        # Code review and optimization
        elif any(word in prompt_lower for word in ["code", "solution", "algorithm", "implement", "optimize"]):
            if "optimize" in prompt_lower or "improve" in prompt_lower:
                return """Let me help you optimize! Here's my approach:

1. **Analyze Current Solution:**
   - What's the time complexity? (O(n²)? O(n)?)
   - What's the space complexity?
   - Are there nested loops?

2. **Optimization Strategies:**
   - Can we use a hash map to reduce O(n²) → O(n)?
   - Is sorting beneficial? (O(n log n) acceptable?)
   - Can we use two pointers instead of nested loops?
   - Would a graph/tree traversal work better?

3. **Common Patterns:**
   - Sliding window for subarrays
   - Hash map for lookups/complements
   - Binary search for sorted data
   - DP for overlapping subproblems

Share your current code and I'll guide you to optimal solution!"""
            else:
                return """I'm ready to help with your code! To provide the best guidance:

1. **Share your approach:** What algorithm are you using?
2. **Current issues:** Where are you stuck?
3. **Test cases:** What inputs fail?

**Common Debugging Tips:**
- Print intermediate values
- Check edge cases (empty, single element)
- Verify loop boundaries (off-by-one errors)
- Test with simple examples first

What problem are you working on?"""
        
        # Problem-solving help
        elif any(word in prompt_lower for word in ["stuck", "help", "confused", "don't understand"]):
            return """No worries! Let's break this down step by step.

**My Problem-Solving Framework:**

1. **Understand the Problem:**
   - What are the inputs and outputs?
   - Any constraints? (time limit, space limit)
   - Edge cases? (empty input, duplicates, negatives)

2. **Think of Patterns:**
   - Does this look like a known pattern?
   - Similar problems you've solved?

3. **Start Simple:**
   - Can you solve it with brute force first?
   - What's the time complexity?

4. **Optimize:**
   - Which data structure helps? (hash map, heap, stack?)
   - Can you reduce time complexity?

Tell me which part is confusing and I'll help you think through it!"""
        
        # Complexity analysis
        elif any(word in prompt_lower for word in ["time complexity", "space complexity", "big o", "complexity"]):
            return """**Time & Space Complexity - Quick Guide**

**Common Time Complexities (Best → Worst):**
- O(1): Constant - hash map lookup, array access
- O(log n): Logarithmic - binary search, balanced tree
- O(n): Linear - single loop, traversal
- O(n log n): Log-linear - merge sort, heap sort
- O(n²): Quadratic - nested loops
- O(2ⁿ): Exponential - recursive fibonacci (no memo)
- O(n!): Factorial - permutations

**How to Calculate:**
1. Count loops (nested = multiply)
2. Recursive calls (draw recursion tree)
3. Ignore constants: O(2n) = O(n)
4. Take worst term: O(n² + n) = O(n²)

**Space Complexity:**
- Recursion depth counts!
- Extra data structures (arrays, hash maps)
- In-place operations = O(1) space

**Example Analysis:**
```python
for i in range(n):        # O(n)
    for j in range(n):    # O(n)
        hash_map[i] = j   # O(1)
# Total: O(n²) time, O(n) space
```

Which algorithm do you want to analyze?"""
        
        # System design
        elif any(word in prompt_lower for word in ["system design", "architecture", "scale", "design"]):
            return """**System Design Framework**

**Step-by-Step Approach:**

1. **Requirements (5 min)**
   - Functional: What features?
   - Non-functional: Scale? Availability? Latency?
   - Estimate: Users? QPS? Storage?

2. **High-Level Design (10 min)**
   - Client → Load Balancer → Servers → Database
   - Which database? (SQL vs NoSQL)
   - Caching layer? (Redis, Memcached)

3. **Deep Dive (15 min)**
   - Database schema
   - API design (REST endpoints)
   - Scaling strategy (horizontal vs vertical)
   - Caching strategy (Cache-aside, Write-through)

4. **Trade-offs (5 min)**
   - CAP theorem (Consistency, Availability, Partition tolerance)
   - SQL vs NoSQL choice
   - Discuss bottlenecks

**Common Systems:**
- URL Shortener, Pastebin
- Twitter, Instagram feed
- Rate Limiter
- Web Crawler

**Key Components:**
- Load Balancer, CDN, Cache
- Message Queue (Kafka, RabbitMQ)
- Database (Sharding, Replication)

Which system would you like to design?"""
        
        # Behavioral questions
        elif any(word in prompt_lower for word in ["interview", "behavioral", "tell me about", "describe a time"]):
            return """**Behavioral Interview - STAR Method**

Use STAR to structure your answers:

**S - Situation:** Set the scene (project, team, context)
**T - Task:** What was your responsibility?
**A - Action:** What did YOU specifically do?
**R - Result:** Quantifiable outcome

**Example:**
"Tell me about a time you faced a challenge"

❌ Bad: "I worked on a hard project and it went well"

✅ Good:
- **S:** "Our API was timing out under load (P95 > 5s)"
- **T:** "As tech lead, I needed to fix this before launch"
- **A:** "I profiled the code, found N+1 query issue, implemented caching, added indexes"
- **R:** "Reduced P95 latency to 200ms, launched successfully to 1M users"

**Common Questions:**
1. Tell me about yourself
2. Why this company?
3. Biggest challenge
4. Conflict with teammate
5. Failure/mistake

**Tips:**
- Be specific with numbers
- Focus on YOUR actions
- Show leadership/ownership
- Demonstrate learning from failures

Which question should we prepare for?"""
        
        # General fallback - more helpful now
        else:
            return """I'm your MAANG Interview Mentor! I can help with:

**📚 Learn & Understand:**
- "Teach me Linked Lists"
- "Explain dynamic programming"
- "How does binary search work?"

**💻 Solve Problems:**
- "Help me solve Two Sum"
- "I'm stuck on this graph problem"
- "How do I optimize my solution?"

**📊 System Design:**
- "Design a URL shortener"
- "How to scale Instagram?"
- "Explain microservices architecture"

**🎤 Behavioral Prep:**
- "Practice STAR method"
- "Tell me about yourself"
- "Handle conflict questions"

**🔍 Complexity Analysis:**
- "Explain Big O notation"
- "What's the time complexity of..."

What would you like to work on today?"""
    
    
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
