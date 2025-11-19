'use client';

import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, Terminal, Lock } from 'lucide-react';

interface CodeEditorProps {
    initialCode?: string;
    language?: string;
    problemId?: string;
    readOnly?: boolean;
}

export default function CodeEditor({ initialCode = "", language = "python", problemId, readOnly = false }: CodeEditorProps) {
    const [code, setCode] = useState(initialCode);
    const [output, setOutput] = useState("");
    const [isRunning, setIsRunning] = useState(false);
    const [activeTab, setActiveTab] = useState<'output' | 'testcases'>('output');

    // Update code when initialCode changes (e.g. when loading a solution)
    useEffect(() => {
        if (initialCode) setCode(initialCode);
    }, [initialCode]);

    const handleRun = async () => {
        if (readOnly) return;
        setIsRunning(true);
        setOutput("Running...");

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
            // Mock test cases for now - in real app, fetch from DB
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

    return (
        <div className="flex flex-col h-full bg-[#1e1e1e] rounded-xl overflow-hidden border border-slate-700 shadow-2xl">
            {/* Toolbar */}
            {!readOnly && (
                <div className="flex items-center justify-between px-4 py-2 bg-[#252526] border-b border-slate-700">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{language}</span>
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
                            onClick={handleSubmit}
                            disabled={isRunning}
                            className="flex items-center gap-2 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs rounded transition-colors disabled:opacity-50"
                        >
                            <CheckCircle size={14} /> Submit
                        </button>
                    </div>
                </div>
            )}

            {/* Editor Area */}
            <div className="flex-1 relative group">
                {readOnly && (
                    <div className="absolute top-2 right-2 z-10 px-2 py-1 bg-slate-800/80 text-slate-400 text-xs rounded flex items-center gap-1 pointer-events-none">
                        <Lock size={12} /> Read Only
                    </div>
                )}
                <textarea
                    value={code}
                    onChange={(e) => !readOnly && setCode(e.target.value)}
                    readOnly={readOnly}
                    className={`w-full h-full bg-[#1e1e1e] text-slate-300 font-mono text-sm p-4 resize-none focus:outline-none ${readOnly ? 'cursor-default' : ''}`}
                    spellCheck={false}
                />
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
                    </div>
                    <div className="flex-1 p-4 overflow-auto font-mono text-xs text-slate-300">
                        {output ? (
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
