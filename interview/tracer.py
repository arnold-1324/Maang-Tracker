import sys
import json
import traceback
from typing import List, Dict, Any

class CodeTracer:
    def __init__(self):
        self.trace_data = []
        self.max_steps = 1000  # Prevent infinite loops
        self.steps = 0

    def trace_calls(self, frame, event, arg):
        if event != 'call':
            return
        return self.trace_lines

    def trace_lines(self, frame, event, arg):
        if event not in ['line', 'return']:
            return
        
        if self.steps >= self.max_steps:
            return

        self.steps += 1
        
        # Extract variables
        variables = {}
        for name, value in frame.f_locals.items():
            if name.startswith('__'): continue
            if callable(value): continue
            if isinstance(value, (int, float, str, bool, list, dict, set, tuple)):
                try:
                    # Create a safe copy for visualization
                    if isinstance(value, (list, dict, set)):
                        variables[name] = json.loads(json.dumps(value, default=str))
                    else:
                        variables[name] = value
                except:
                    variables[name] = str(value)

        self.trace_data.append({
            'line': frame.f_lineno,
            'event': event,
            'variables': variables,
            'func': frame.f_code.co_name
        })
        
        return self.trace_lines

    def run_trace(self, code: str, input_data: str = "") -> Dict[str, Any]:
        # Capture stdout
        from io import StringIO
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        try:
            # Prepare environment
            global_env = {}
            
            # If input provided, mock input()
            if input_data:
                inputs = input_data.split('\n')
                input_iter = iter(inputs)
                global_env['input'] = lambda: next(input_iter)

            # Start tracing
            sys.settrace(self.trace_calls)
            exec(code, global_env)
            sys.settrace(None)

            return {
                "success": True,
                "trace": self.trace_data,
                "output": redirected_output.getvalue()
            }
        except Exception as e:
            sys.settrace(None)
            return {
                "success": False,
                "error": str(e),
                "trace": self.trace_data,  # Return partial trace
                "output": redirected_output.getvalue()
            }
        finally:
            sys.settrace(None)
            sys.stdout = old_stdout
