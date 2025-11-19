"""
Code Execution Sandbox - Safely execute and validate code submissions
"""

import subprocess
import tempfile
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib


@dataclass
class ExecutionResult:
    """Result from code execution"""
    success: bool
    output: str
    error: str = ""
    execution_time_ms: float = 0
    memory_used_mb: float = 0
    exit_code: int = 0


class CodeCompiler:
    """
    Code compilation and execution for multiple languages
    Supports: Python, Java, C++, JavaScript
    """
    
    # Language configurations
    LANGUAGES = {
        "python": {
            "extension": ".py",
            "run_command": ["python", "{file}"],
            "timeout": 30
        },
        "java": {
            "extension": ".java",
            "compile_command": ["javac", "{file}"],
            "run_command": ["java", "-cp", "{dir}", "{class_name}"],
            "timeout": 30
        },
        "cpp": {
            "extension": ".cpp",
            "compile_command": ["g++", "-o", "{output}", "{file}"],
            "run_command": ["{output}"],
            "timeout": 30
        },
        "javascript": {
            "extension": ".js",
            "run_command": ["node", "{file}"],
            "timeout": 30
        },
        "c": {
            "extension": ".c",
            "compile_command": ["gcc", "-o", "{output}", "{file}"],
            "run_command": ["{output}"],
            "timeout": 30
        },
        "csharp": {
            "extension": ".cs",
            "compile_command": ["csc", "/out:{output}.exe", "{file}"],
            "run_command": ["{output}.exe"],
            "timeout": 30
        }
    }
    
    def __init__(self, max_memory_mb: int = 512, max_timeout_seconds: int = 30):
        """Initialize compiler"""
        self.max_memory_mb = max_memory_mb
        self.max_timeout_seconds = max_timeout_seconds
        self.execution_history: List[Dict[str, Any]] = []
    
    def compile_and_run(self, code: str, language: str, 
                       input_data: str = "", stdin_input: bool = False) -> ExecutionResult:
        """
        Compile and execute code
        """
        if language not in self.LANGUAGES:
            return ExecutionResult(
                success=False,
                error=f"Unsupported language: {language}"
            )
        
        lang_config = self.LANGUAGES[language]
        
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write code to file
                code_file = os.path.join(temp_dir, f"solution{lang_config['extension']}")
                with open(code_file, 'w') as f:
                    f.write(code)
                
                # Compile if needed
                if "compile_command" in lang_config:
                    result = self._compile(code_file, lang_config, temp_dir)
                    if not result.success:
                        return result
                
                # Execute
                result = self._execute(code_file, lang_config, temp_dir, input_data, stdin_input)
                
                # Store in history
                self.execution_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "language": language,
                    "code_hash": hashlib.md5(code.encode()).hexdigest(),
                    "result": {
                        "success": result.success,
                        "execution_time_ms": result.execution_time_ms
                    }
                })
                
                return result
                
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    def _compile(self, code_file: str, lang_config: Dict, temp_dir: str) -> ExecutionResult:
        """Compile code"""
        import time
        
        compile_cmd = lang_config["compile_command"].copy()
        compile_cmd = [cmd.format(file=code_file, output=os.path.join(temp_dir, "output"), dir=temp_dir) 
                      for cmd in compile_cmd]
        
        try:
            start = time.time()
            result = subprocess.run(
                compile_cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=self.max_timeout_seconds
            )
            elapsed = (time.time() - start) * 1000
            
            if result.returncode != 0:
                return ExecutionResult(
                    success=False,
                    error=result.stderr,
                    execution_time_ms=elapsed
                )
            
            return ExecutionResult(
                success=True,
                output="Compilation successful",
                execution_time_ms=elapsed
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error="Compilation timeout"
            )
    
    def _execute(self, code_file: str, lang_config: Dict, temp_dir: str, 
                input_data: str = "", stdin_input: bool = False) -> ExecutionResult:
        """Execute code"""
        import time
        
        run_cmd = lang_config["run_command"].copy()
        
        # Format command with placeholders
        run_cmd = [cmd.format(
            file=code_file,
            output=os.path.join(temp_dir, "output"),
            dir=temp_dir,
            class_name=os.path.splitext(os.path.basename(code_file))[0]
        ) for cmd in run_cmd]
        
        try:
            start = time.time()
            
            # Prepare stdin
            stdin_data = input_data if stdin_input else None
            
            result = subprocess.run(
                run_cmd,
                cwd=temp_dir,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=lang_config.get("timeout", self.max_timeout_seconds)
            )
            
            elapsed = (time.time() - start) * 1000
            
            return ExecutionResult(
                success=(result.returncode == 0),
                output=result.stdout,
                error=result.stderr,
                execution_time_ms=elapsed,
                exit_code=result.returncode
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Execution timeout (>{lang_config.get('timeout', self.max_timeout_seconds)}s)"
            )
    
    def test_against_cases(self, code: str, language: str, 
                          test_cases: List[Dict[str, str]],
                          custom_input: Optional[str] = None) -> Dict[str, Any]:
        """
        Test code against multiple test cases with optional custom input
        
        test_cases format:
        [
            {"input": "...", "expected": "..."},
            ...
        ]
        """
        results = {
            "passed": 0,
            "failed": 0,
            "total": len(test_cases),
            "test_results": [],
            "total_execution_time_ms": 0,
            "custom_test_result": None
        }
        
        # If custom input provided, test it first
        if custom_input:
            exec_result = self.compile_and_run(code, language, custom_input, stdin_input=True)
            results["custom_test_result"] = {
                "input": custom_input[:200],
                "output": exec_result.output[:200] if exec_result.output else "(no output)",
                "execution_time_ms": exec_result.execution_time_ms,
                "success": exec_result.success,
                "error": exec_result.error if not exec_result.success else ""
            }
        
        for i, test_case in enumerate(test_cases):
            input_data = test_case.get("input", "")
            expected = test_case.get("expected", "").strip()
            
            # Execute code with input
            exec_result = self.compile_and_run(code, language, input_data, stdin_input=True)
            
            output = exec_result.output.strip()
            passed = (output == expected) and exec_result.success
            
            results["test_results"].append({
                "test_case_number": i + 1,
                "passed": passed,
                "input": input_data[:100] if input_data else "(no input)",
                "expected": expected[:100],
                "actual": output[:100] if output else "(no output)",
                "execution_time_ms": exec_result.execution_time_ms,
                "error": exec_result.error if not exec_result.success else ""
            })
            
            results["total_execution_time_ms"] += exec_result.execution_time_ms
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        # Update passed/failed counts
        results["passed_count"] = results["passed"]
        results["total_count"] = results["total"]
        
        return results
    
    def analyze_code_complexity(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code for complexity hints"""
        analysis = {
            "language": language,
            "lines": len(code.split('\n')),
            "has_nested_loops": "for" in code and code.count("for") >= 2,
            "has_recursion": "def " in code and code.count("return") > 1,
            "has_sorting": "sort" in code.lower(),
            "has_hash_map": ("dict" in code or "HashMap" in code or "{}" in code),
            "suggestions": []
        }
        
        if analysis["has_nested_loops"]:
            analysis["suggestions"].append("Multiple nested loops detected - consider O(n) or O(n log n) alternatives")
        
        if not analysis["has_hash_map"] and ("brute" in code.lower() or "nested" in code.lower()):
            analysis["suggestions"].append("Consider using hash map for O(1) lookups")
        
        return analysis
    
    def get_syntax_errors(self, code: str, language: str) -> List[str]:
        """Check for syntax errors without execution"""
        if language == "python":
            import ast
            try:
                ast.parse(code)
                return []
            except SyntaxError as e:
                return [f"Line {e.lineno}: {e.msg}"]
        
        # For other languages, try compilation
        result = self.compile_and_run(code, language)
        if not result.success and result.error:
            return result.error.split('\n')[:5]  # First 5 error lines
        
        return []


class InterviewCodeValidator:
    """
    Validates interview solutions against specific criteria
    """
    
    def __init__(self):
        self.compiler = CodeCompiler()
    
    def validate_solution(self, code: str, language: str, 
                         problem_id: str, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Comprehensive solution validation
        """
        validation = {
            "problem_id": problem_id,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "syntax_valid": True,
                "all_tests_passed": False,
                "code_efficiency": "unknown",
                "style_quality": "unknown"
            },
            "details": {}
        }
        
        # Check syntax
        syntax_errors = self.compiler.get_syntax_errors(code, language)
        if syntax_errors:
            validation["metrics"]["syntax_valid"] = False
            validation["details"]["syntax_errors"] = syntax_errors
            return validation
        
        # Run tests
        test_results = self.compiler.test_against_cases(code, language, test_cases)
        validation["details"]["test_results"] = test_results
        validation["metrics"]["all_tests_passed"] = (test_results["failed"] == 0)
        
        # Analyze code
        complexity = self.compiler.analyze_code_complexity(code, language)
        validation["details"]["complexity_analysis"] = complexity
        
        # Score solution
        test_score = (test_results["passed"] / test_results["total"]) * 100 if test_results["total"] > 0 else 0
        validation["score"] = test_score
        
        return validation


# Example usage
if __name__ == "__main__":
    compiler = CodeCompiler()
    
    # Python example
    python_code = """
x = input()
y = input()
print(int(x) + int(y))
"""
    
    test_cases = [
        {"input": "5\n3", "expected": "8"},
        {"input": "10\n20", "expected": "30"}
    ]
    
    results = compiler.test_against_cases(python_code, "python", test_cases)
    print("Test Results:", json.dumps(results, indent=2))
    
    # Complexity analysis
    complex_code = """
def solution(nums):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
"""
    
    analysis = compiler.analyze_code_complexity(complex_code, "python")
    print("\nComplexity Analysis:", json.dumps(analysis, indent=2))
