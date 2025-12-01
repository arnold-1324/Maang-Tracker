'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Play, CheckCircle, Terminal, Lock, Bug, Zap, Brain } from 'lucide-react';

interface CodeEditorProps {
    initialCode?: string;
    language?: string;
    problemId?: string;
    readOnly?: boolean;
    onVisualize?: (code: string) => void;
}

interface TraceStep {
    line: number;
    event: string;
    variables: Record<string, any>;
    func: string;
}

interface AlgoVisualizerProps {
    trace: TraceStep[];
    onStepChange: (line: number) => void;
    onExplainStep: (step: TraceStep) => void;
}

// Syntax highlighter for Python
const SyntaxHighlighter: React.FC<{ code: string; language: string }> = ({ code, language }) => {
    if (language !== 'python') {
        return <pre className="text-slate-300 whitespace-pre-wrap">{code}</pre>;
    }

    const highlightPython = (code: string) => {
        const keywords = ['def', 'class', 'return', 'if', 'else', 'elif', 'for', 'while', 'in', 'and', 'or', 'not', 'import', 'from', 'as', 'True', 'False', 'None', 'try', 'except', 'finally', 'with', 'as'];
        const builtins = ['print', 'range', 'len', 'str', 'int', 'float', 'list', 'dict', 'set'];

        return code.split('\n').map((line, lineIndex) => {
            const parts = line.split(/(\s+|[:=+\-*\/%<>!()\[\]{},.]|->|#.*)/);

            return (
                <div key={lineIndex} className="flex">
                    <span className="text-slate-500 w-8 text-right pr-2 select-none">{lineIndex + 1}</span>
                    <span className="flex-1">
                        {parts.map((part, partIndex) => {
                            if (keywords.includes(part)) {
                                return <span key={partIndex} className="text-purple-400 font-medium">{part}</span>;
                            } else if (builtins.includes(part)) {
                                return <span key={partIndex} className="text-yellow-300">{part}</span>;
                            } else if (part.startsWith('#')) {
                                return <span key={partIndex} className="text-green-600">{part}</span>;
                            } else if (part.match(/^["'].*["']$/)) {
                                return <span key={partIndex} className="text-green-400">{part}</span>;
                            } else if (part.match(/^\d+$/)) {
                                return <span key={partIndex} className="text-orange-400">{part}</span>;
                            } else if (part.match(/^[A-Za-z_][A-Za-z0-9_]*$/)) {
                                return <span key={partIndex} className="text-slate-200">{part}</span>;
                            } else {
                                return <span key={partIndex} className="text-slate-400">{part}</span>;
                            }
                        })}
                    </span>
                </div>
            );
        });
    };

    return <div className="font-mono text-sm leading-relaxed">{highlightPython(code)}</div>;
};

// Auto-fix suggestions for Python
const getSyntaxSuggestions = (code: string, language: string): string[] => {
    if (language !== 'python') return [];

    const suggestions: string[] = [];
    const lines = code.split('\n');

    lines.forEach((line, index) => {
        // Check for missing colons
        if (line.match(/^(def|class|if|elif|else|for|while|with)\s+[^:]+$/) && !line.trim().endsWith(':')) {
            suggestions.push(`Line ${index + 1}: Missing colon at end of statement`);
        }

        // Check for inconsistent indentation
        if (line.length > 0 && line.match(/^[ ]*\t/)) {
            suggestions.push(`Line ${index + 1}: Mixed tabs and spaces`);
        }

        // Check for common syntax issues
        if (line.includes('= =') || line.includes('== =')) {
            suggestions.push(`Line ${index + 1}: Suspicious equality comparison`);
        }
    });

    return suggestions;
};

export default function CodeEditor({ initialCode = "", language = "python", problemId, readOnly = false, onVisualize }: CodeEditorProps) {
    const [code, setCode] = useState(initialCode);
    const [output, setOutput] = useState("");
    const [isRunning, setIsRunning] = useState(false);
    const [activeTab, setActiveTab] = useState<'output' | 'testcases' | 'debug' | 'suggestions'>('output');
    const [debugTrace, setDebugTrace] = useState<TraceStep[]>([]);
    const [currentDebugStep, setCurrentDebugStep] = useState(0);
    const [isDebugging, setIsDebugging] = useState(false);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const preRef = useRef<HTMLPreElement>(null);

    // Update code when initialCode changes
    useEffect(() => {
        if (initialCode) setCode(initialCode);
    }, [initialCode]);

    // Sync scroll between textarea and syntax highlighter
    const handleScroll = () => {
        if (textareaRef.current && preRef.current) {
            preRef.current.scrollTop = textareaRef.current.scrollTop;
            preRef.current.scrollLeft = textareaRef.current.scrollLeft;
        }
    };

    // Generate syntax suggestions
    const updateSuggestions = () => {
        const newSuggestions = getSyntaxSuggestions(code, language);
        setSuggestions(newSuggestions);
    };

    useEffect(() => {
        updateSuggestions();
    }, [code, language]);

    const handleRun = async () => {
        if (readOnly) return;
        setIsRunning(true);
        setOutput("Running...");
        setActiveTab('output');

        try {
            const res = await fetch('/api/compiler/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, language, input: "" })
            });

            const data = await res.json();

            if (data.success) {
                setOutput(data.output || "No output");
            } else {
                setOutput(`Error:\n${data.error}`);
            }
        } catch (e) {
            setOutput(`Network Error: ${e}`);
        } finally {
            setIsRunning(false);
        }
    };

    const handleSubmit = async () => {
        if (readOnly) return;
        if (!problemId) {
            alert("No problem selected to submit against.");
            return;
        }

        setIsRunning(true);
        setActiveTab('testcases');
        setOutput("Running test cases...");

        try {
            const testCases = [
                { input: "2\n3", expected: "5" },
                { input: "10\n5", expected: "15" }
            ];

            const res = await fetch('/api/compiler/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code,
                    language,
                    problem_id: problemId,
                    test_cases: testCases
                })
            });

            const data = await res.json();

            if (data.success) {
                const validation = data.validation;
                let resultText = `Score: ${validation.score.toFixed(1)}%\n\n`;

                validation.details.test_results.forEach((t: any) => {
                    resultText += `Test ${t.test_case_number}: ${t.passed ? 'PASSED' : 'FAILED'}\n`;
                    if (!t.passed) {
                        resultText += `  Expected: ${t.expected}\n  Actual: ${t.actual}\n`;
                    }
                });

                setOutput(resultText);
            } else {
                setOutput(`Submission Error:\n${data.error}`);
            }
        } catch (e) {
            setOutput(`Network Error: ${e}`);
        } finally {
            setIsRunning(false);
        }
    };

    const handleDebug = async () => {
        if (readOnly) return;
        setIsRunning(true);
        setActiveTab('debug');
        setOutput("Starting debugger...");

        try {
            // Mock debug trace - in real app, this would come from backend
            const mockTrace: TraceStep[] = [
                { line: 1, event: 'start', variables: {}, func: 'main' },
                { line: 2, event: 'assign', variables: { x: 5 }, func: 'main' },
                { line: 3, event: 'assign', variables: { x: 5, y: 10 }, func: 'main' },
                { line: 4, event: 'compute', variables: { x: 5, y: 10, result: 15 }, func: 'main' },
                { line: 5, event: 'return', variables: { x: 5, y: 10, result: 15 }, func: 'main' },
            ];

            setDebugTrace(mockTrace);
            setCurrentDebugStep(0);
            setIsDebugging(true);
            setOutput("Debugger ready. Use controls to step through execution.");
        } catch (e) {
            setOutput(`Debug Error: ${e}`);
        } finally {
            setIsRunning(false);
        }
    };

    const handleFixSyntax = () => {
        if (readOnly) return;

        let fixedCode = code;

        // Basic auto-fixes
        fixedCode = fixedCode.replace(/= =/g, '==');
        fixedCode = fixedCode.replace(/== =/g, '==');

        // Add missing colons
        fixedCode = fixedCode.split('\n').map(line => {
            if (line.match(/^(def|class|if|elif|else|for|while|with)\s+[^:]+$/) && !line.trim().endsWith(':')) {
                return line + ':';
            }
            return line;
        }).join('\n');

        setCode(fixedCode);
        updateSuggestions();
    };

    const handleStepChange = (step: number) => {
        setCurrentDebugStep(step);
        if (debugTrace[step]) {
            // Highlight the current line in the editor
            // This would typically scroll to the line and highlight it
        }
    };

    const handleExplainStep = (step: TraceStep) => {
        alert(`Line ${step.line}: ${step.event}\nVariables: ${JSON.stringify(step.variables, null, 2)}`);
    };

    return (
        <div className="flex flex-col h-full bg-[#1e1e1e] rounded-xl overflow-hidden border border-slate-700 shadow-2xl">
            {/* Toolbar */}
            {!readOnly && (
                <div className="flex items-center justify-between px-4 py-2 bg-[#252526] border-b border-slate-700">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{language}</span>
                        {suggestions.length > 0 && (
                            <span className="text-xs text-orange-400">
                                {suggestions.length} issue{suggestions.length > 1 ? 's' : ''}
                            </span>
                        )}
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={handleRun}
                            disabled={isRunning}
                            className="flex items-center gap-2 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-xs rounded transition-colors disabled:opacity-50"
                        >
                            <Play size={14} /> Run
                        </button>
                        <button
                            onClick={handleDebug}
                            disabled={isRunning}
                            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs rounded transition-colors disabled:opacity-50"
                        >
                            <Bug size={14} /> Debug
                        </button>
                        <button
                            onClick={handleFixSyntax}
                            disabled={isRunning || suggestions.length === 0}
                            className="flex items-center gap-2 px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white text-xs rounded transition-colors disabled:opacity-50"
                        >
                            <Zap size={14} /> Fix Syntax
                        </button>
                        <button
                            onClick={handleSubmit}
                            disabled={isRunning}
                            className="flex items-center gap-2 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs rounded transition-colors disabled:opacity-50"
                        >
                            <CheckCircle size={14} /> Submit
                        </button>
                        {onVisualize && (
                            <button
                                onClick={() => onVisualize(code)}
                                disabled={isRunning}
                                className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-xs rounded transition-colors disabled:opacity-50"
                            >
                                <Play size={14} /> Visualize
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Editor Area */}
            <div className="flex-1 flex">
                {/* Code Editor */}
                <div className="flex-1 relative group">
                    {readOnly && (
                        <div className="absolute top-2 right-2 z-10 px-2 py-1 bg-slate-800/80 text-slate-400 text-xs rounded flex items-center gap-1 pointer-events-none">
                            <Lock size={12} /> Read Only
                        </div>
                    )}

                    {/* Syntax Highlighted Background */}
                    <div className="absolute inset-0 overflow-auto">
                        <pre ref={preRef} className="p-4 font-mono text-sm">
                            <SyntaxHighlighter code={code} language={language} />
                        </pre>
                    </div>

                    {/* Textarea Overlay */}
                    <textarea
                        ref={textareaRef}
                        value={code}
                        onChange={(e) => !readOnly && setCode(e.target.value)}
                        onScroll={handleScroll}
                        readOnly={readOnly}
                        className="w-full h-full bg-transparent text-transparent caret-white font-mono text-sm p-4 resize-none focus:outline-none absolute inset-0"
                        spellCheck={false}
                        style={{ zIndex: 10 }}
                    />
                </div>

                {/* Debug/Visualizer Panel */}
                {isDebugging && debugTrace.length > 0 && (
                    <div className="w-1/2 border-l border-slate-700">
                        <AlgoVisualizer
                            trace={debugTrace}
                            onStepChange={handleStepChange}
                            onExplainStep={handleExplainStep}
                        />
                    </div>
                )}
            </div>

            {/* Output Panel */}
            {!readOnly && (
                <div className="h-1/3 bg-[#1e1e1e] border-t border-slate-700 flex flex-col">
                    <div className="flex border-b border-slate-700">
                        <button
                            onClick={() => setActiveTab('output')}
                            className={`px-4 py-2 text-xs font-medium transition-colors ${activeTab === 'output' ? 'text-white border-b-2 border-indigo-500 bg-slate-800/50' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Output
                        </button>
                        <button
                            onClick={() => setActiveTab('testcases')}
                            className={`px-4 py-2 text-xs font-medium transition-colors ${activeTab === 'testcases' ? 'text-white border-b-2 border-indigo-500 bg-slate-800/50' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Test Cases
                        </button>
                        <button
                            onClick={() => setActiveTab('suggestions')}
                            className={`px-4 py-2 text-xs font-medium transition-colors ${activeTab === 'suggestions' ? 'text-white border-b-2 border-indigo-500 bg-slate-800/50' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Suggestions {suggestions.length > 0 && `(${suggestions.length})`}
                        </button>
                        {isDebugging && (
                            <button
                                onClick={() => setActiveTab('debug')}
                                className={`px-4 py-2 text-xs font-medium transition-colors ${activeTab === 'debug' ? 'text-white border-b-2 border-blue-500 bg-slate-800/50' : 'text-slate-500 hover:text-slate-300'}`}
                            >
                                Debug
                            </button>
                        )}
                    </div>

                    <div className="flex-1 p-4 overflow-auto font-mono text-xs text-slate-300">
                        {activeTab === 'suggestions' ? (
                            suggestions.length > 0 ? (
                                <div className="space-y-2">
                                    {suggestions.map((suggestion, index) => (
                                        <div key={index} className="flex items-start gap-2 p-2 bg-amber-500/10 border border-amber-500/20 rounded">
                                            <Zap size={12} className="text-amber-400 mt-0.5 flex-shrink-0" />
                                            <span className="text-amber-300">{suggestion}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-slate-600 italic flex items-center gap-2">
                                    <CheckCircle size={14} />
                                    No syntax issues found!
                                </div>
                            )
                        ) : output ? (
                            <pre className="whitespace-pre-wrap">{output}</pre>
                        ) : (
                            <div className="text-slate-600 italic flex items-center gap-2">
                                <Terminal size={14} />
                                Run code to see output...
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

// Enhanced AlgoVisualizer Component
function AlgoVisualizer({ trace, onStepChange, onExplainStep }: AlgoVisualizerProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [speed, setSpeed] = useState(1000);
    const timerRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (trace.length > 0) {
            onStepChange(trace[currentStep].line);
        }
    }, [currentStep, trace, onStepChange]);

    useEffect(() => {
        if (isPlaying) {
            timerRef.current = setInterval(() => {
                setCurrentStep(prev => {
                    if (prev >= trace.length - 1) {
                        setIsPlaying(false);
                        return prev;
                    }
                    return prev + 1;
                });
            }, speed);
        } else {
            if (timerRef.current) clearInterval(timerRef.current);
        }
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [isPlaying, speed, trace.length]);

    const handleStepChange = (newStep: number) => {
        const step = Math.max(0, Math.min(newStep, trace.length - 1));
        setCurrentStep(step);
    };

    if (!trace || trace.length === 0) {
        return (
            <div className="flex items-center justify-center h-full text-slate-500">
                <p>Run "Debug" to see algorithm execution</p>
            </div>
        );
    }

    const currentData = trace[currentStep];

    const renderVariable = (name: string, value: any) => {
        if (Array.isArray(value)) {
            return (
                <div key={name} className="mb-6">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-mono text-indigo-400">{name}</span>
                        <span className="text-xs text-slate-500">Array[{value.length}]</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                        {value.map((item, idx) => (
                            <div key={idx} className="relative group">
                                <div className={`
                                    min-w-[32px] h-10 flex items-center justify-center 
                                    border border-slate-700 rounded bg-slate-800/50
                                    text-sm font-mono text-slate-200 px-2
                                    transition-all duration-300
                                    ${typeof item === 'number' ? 'hover:bg-indigo-500/20 hover:border-indigo-500' : ''}
                                `}>
                                    {JSON.stringify(item)}
                                </div>
                                <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 text-[10px] text-slate-600 font-mono">
                                    {idx}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        if (typeof value === 'object' && value !== null) {
            return (
                <div key={name} className="mb-4">
                    <div className="text-xs font-mono text-purple-400 mb-1">{name}</div>
                    <div className="bg-slate-900/50 p-2 rounded border border-slate-800 font-mono text-xs text-slate-300">
                        {JSON.stringify(value, null, 2)}
                    </div>
                </div>
            );
        }

        return (
            <div key={name} className="flex justify-between items-center mb-2 p-2 bg-slate-800/30 rounded border border-slate-800/50">
                <span className="text-xs font-mono text-emerald-400">{name}</span>
                <span className="text-sm font-mono text-white">{JSON.stringify(value)}</span>
            </div>
        );
    };

    return (
        <div className="flex flex-col h-full bg-[#1e1e1e] text-slate-200">
            {/* Controls */}
            <div className="flex items-center justify-between p-3 border-b border-slate-800 bg-[#252526]">
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => handleStepChange(0)}
                        className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white"
                    >
                        <SkipBack size={16} />
                    </button>
                    <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="p-1.5 hover:bg-slate-700 rounded text-indigo-400 hover:text-indigo-300"
                    >
                        {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                    </button>
                    <button
                        onClick={() => handleStepChange(trace.length - 1)}
                        className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white"
                    >
                        <SkipForward size={16} />
                    </button>
                </div>

                <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-slate-500">
                        Step {currentStep + 1}/{trace.length}
                    </span>
                    <select
                        value={speed}
                        onChange={(e) => setSpeed(Number(e.target.value))}
                        className="bg-slate-800 text-xs border border-slate-700 rounded px-2 py-1 outline-none"
                    >
                        <option value={2000}>Slow</option>
                        <option value={1000}>Normal</option>
                        <option value={500}>Fast</option>
                    </select>
                </div>
            </div>

            {/* Visualization Area */}
            <div className="flex-1 overflow-y-auto p-4">
                <div className="mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-indigo-500"></div>
                            Variables
                        </h3>
                        <button
                            onClick={() => onExplainStep(currentData)}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 text-xs rounded-full border border-indigo-500/20 transition-colors"
                        >
                            <Brain size={12} /> Explain this step
                        </button>
                    </div>

                    <div className="space-y-2">
                        {Object.entries(currentData.variables).map(([name, value]) =>
                            renderVariable(name, value)
                        )}
                    </div>
                </div>

                {/* Call Stack */}
                <div className="border-t border-slate-800 pt-4">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Call Stack</h3>
                    <div className="bg-slate-900 p-2 rounded border border-slate-800">
                        <div className="text-xs font-mono text-yellow-400">
                            {currentData.func}() <span className="text-slate-600">line {currentData.line}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Timeline Slider */}
            <div className="p-4 border-t border-slate-800 bg-[#252526]">
                <input
                    type="range"
                    min="0"
                    max={trace.length - 1}
                    value={currentStep}
                    onChange={(e) => handleStepChange(Number(e.target.value))}
                    className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                />
            </div>
        </div>
    );
}

// Add missing icon imports
const Pause = ({ size }: { size: number }) => <span>⏸</span>;
const SkipBack = ({ size }: { size: number }) => <span>⏮</span>;
const SkipForward = ({ size }: { size: number }) => <span>⏭</span>;