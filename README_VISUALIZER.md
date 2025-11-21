# 🧠 Algorithm Visualizer & AI Debugger

I've upgraded the platform to include a **LeetCode-style Algorithm Visualizer** with deep AI integration.

## ✨ New Features

### 1. **Step-by-Step Execution Trace**
- **Visualizer Tab**: A new tab in the interview workspace.
- **Trace Execution**: Runs your code and captures every variable change, loop iteration, and function call.
- **Timeline Slider**: Scrub through your code execution like a video.

### 2. **Visual Debugging**
- **Variable Inspector**: See arrays, lists, and objects visualized as blocks (not just text).
- **Real-time Updates**: Watch arrays grow and values change as you step through loops.
- **Call Stack**: See exactly which function and line is currently executing.

### 3. **AI-Powered "Explain This Step"**
- **Contextual AI**: Click the **"Explain this step"** button at any point in the execution.
- **Deep Understanding**: The AI receives the *exact* state of memory (variables, current line) and explains *why* the code is doing what it's doing.
- **Learning Tool**: Perfect for understanding complex algorithms like Dynamic Programming or Recursion.

## 🚀 How to Use

1. **Go to Interview Page**: Navigate to `/interview`.
2. **Write Code**: Enter your Python solution (e.g., for Merge k Sorted Lists).
3. **Click "Visualize"**: Instead of just "Run", click the purple **Visualize** button.
4. **Explore**:
   - Use the **Slider** to move through time.
   - Click **Play** to watch it run.
   - Click **"Explain this step"** to ask the AI for help with the specific logic at that moment.

## 🔧 Technical Implementation

- **Backend Tracer**: Custom Python `sys.settrace` engine to capture execution frames safely.
- **Frontend Visualizer**: React component rendering dynamic variable states.
- **AI Integration**: Direct bridge between the visualizer state and the AI agent's context window.

## ⚠️ Note
Currently supports **Python** for full visualization. Other languages will run but may not support deep tracing yet.
