'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipBack, SkipForward, ChevronRight, ChevronDown, Brain } from 'lucide-react';

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

export default function AlgoVisualizer({ trace, onStepChange, onExplainStep }: AlgoVisualizerProps) {
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
                <p>Run "Visualize" to see algorithm execution</p>
            </div>
        );
    }

    const currentData = trace[currentStep];

    // Helper to render variable visualization
    const renderVariable = (name: string, value: any) => {
        // Array/List Visualization
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

        // Object/Dict Visualization
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

        // Primitive Visualization
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

                {/* Call Stack (Simplified) */}
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
