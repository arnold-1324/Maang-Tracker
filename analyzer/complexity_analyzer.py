# analyzer/complexity_analyzer.py
"""
Simple static heuristic complexity analyzer for Python-like code.
This is not perfect but flags:
 - nested 'for' loops (likely O(N^2))
 - 'for' inside 'for' inside 'for' (O(N^3))
 - presence of sort() usage (O(N log N))
 - use of recursion (heuristic: 'def' + 'return' calling same name)

Also provides a micro-benchmark runner to estimate time growth for small input sizes.
"""
import re
import textwrap
import timeit

def detect_nested_loops(code: str):
    # crude: count indentation + for occurrences
    lines = code.splitlines()
    depth = 0
    max_depth = 0
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if re.match(r'for\s+.*in\s+.*:', stripped):
            depth += 1
            if depth > max_depth:
                max_depth = depth
        # decrease depth heuristically on dedent (simple)
        if stripped.startswith("return") or stripped.startswith("break") or stripped == "":
            depth = max(depth-1, 0)
    return max_depth

def detect_sort_usage(code: str):
    return bool(re.search(r'\.sort\(|sorted\(', code))

def detect_recursion(code: str):
    # find function names and if they call themselves
    funcs = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    for f in funcs:
        if re.search(r'\b' + re.escape(f) + r'\s*\(', code):
            # naive true (even calls to nested functions count)
            return True
    return False

def static_analysis(code: str):
    depth = detect_nested_loops(code)
    sort_used = detect_sort_usage(code)
    recursion = detect_recursion(code)
    result = {"nested_loop_depth": depth, "sort_used": sort_used, "recursion": recursion}
    # heuristic complexity
    if depth >= 3:
        result["likely_complexity"] = "O(N^3) or worse"
    elif depth == 2:
        result["likely_complexity"] = "O(N^2)"
    elif sort_used:
        result["likely_complexity"] = "O(N log N)"
    elif recursion:
        result["likely_complexity"] = "Recursive - could be exponential or linear depending on memoization"
    else:
        result["likely_complexity"] = "O(N) or O(N log N) or O(1) - needs micro-benchmark"
    return result

def micro_benchmark(code: str, func_name: str, param_generator: str, trials=3):
    """
    code: source code string defining func_name
    param_generator: a string with Python code that returns an argument list for the function call for increasing sizes.
    Example param_generator: 'lambda n: ([i for i in range(n)],)' to produce one list param
    WARNING: executes code via exec; only run trusted snippets (we assume code comes from user).
    """
    local = {}
    exec(textwrap.dedent(code), {}, local)
    f = local.get(func_name)
    if not f:
        raise ValueError("Function not found after exec")
    results = []
    for n in [50, 200, 800][:trials]:
        try:
            t = timeit.timeit(lambda: f(*eval(param_generator)(n)), number=1)
            results.append({"n": n, "time": t})
        except Exception as e:
            results.append({"n": n, "error": str(e)})
    return results
