'use client';

import React, { useEffect, useState, useRef } from 'react';
import { X, Code, FileText, CheckCircle, Lock, Star, Video, ChevronRight, ExternalLink } from 'lucide-react';
import CodeEditor from './CodeEditor';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';

// --- Types ---

interface RoadmapNode {
    id: string;
    label: string;
    x: number;
    y: number;
    progress: number; // 0 to 100
    total: number;
    solved: number;
}

interface RoadmapEdge {
    from: string;
    to: string;
}

interface ProblemDetail {
    problem_id: string;
    problem_name: string;
    solved: boolean;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    starred?: boolean;
    videoUrl?: string;
    code?: string;
    notes?: string;
    language?: string;
    leetcodeUrl?: string;
}

// --- Static Data for the "NeetCode" Style Layout ---

const NODES: RoadmapNode[] = [
    { id: 'arrays', label: 'Arrays & Hashing', x: 400, y: 50, progress: 0, total: 9, solved: 0 },
    { id: 'two_pointers', label: 'Two Pointers', x: 280, y: 140, progress: 0, total: 6, solved: 0 },
    { id: 'stack', label: 'Stack', x: 520, y: 140, progress: 0, total: 7, solved: 0 },
    { id: 'binary_search', label: 'Binary Search', x: 180, y: 230, progress: 0, total: 7, solved: 0 },
    { id: 'sliding_window', label: 'Sliding Window', x: 340, y: 230, progress: 0, total: 6, solved: 0 },
    { id: 'linked_list', label: 'Linked List', x: 580, y: 230, progress: 0, total: 11, solved: 0 },
    { id: 'trees', label: 'Trees', x: 400, y: 320, progress: 0, total: 15, solved: 0 },
    { id: 'tries', label: 'Tries', x: 200, y: 410, progress: 0, total: 3, solved: 0 },
    { id: 'backtracking', label: 'Backtracking', x: 600, y: 410, progress: 0, total: 9, solved: 0 },
    { id: 'heap', label: 'Heap / Priority Queue', x: 300, y: 500, progress: 0, total: 7, solved: 0 },
    { id: 'graphs', label: 'Graphs', x: 550, y: 500, progress: 0, total: 13, solved: 0 },
    { id: 'dp_1d', label: '1-D DP', x: 720, y: 500, progress: 0, total: 12, solved: 0 },
    { id: 'intervals', label: 'Intervals', x: 150, y: 590, progress: 0, total: 6, solved: 0 },
    { id: 'greedy', label: 'Greedy', x: 300, y: 590, progress: 0, total: 8, solved: 0 },
    { id: 'adv_graphs', label: 'Advanced Graphs', x: 450, y: 590, progress: 0, total: 6, solved: 0 },
    { id: 'dp_2d', label: '2-D DP', x: 600, y: 590, progress: 0, total: 11, solved: 0 },
    { id: 'bit_manip', label: 'Bit Manipulation', x: 750, y: 590, progress: 0, total: 7, solved: 0 },
    { id: 'math', label: 'Math & Geometry', x: 675, y: 680, progress: 0, total: 8, solved: 0 },
];

const EDGES: RoadmapEdge[] = [
    { from: 'arrays', to: 'two_pointers' },
    { from: 'arrays', to: 'stack' },
    { from: 'two_pointers', to: 'binary_search' },
    { from: 'two_pointers', to: 'sliding_window' },
    { from: 'two_pointers', to: 'linked_list' },
    { from: 'binary_search', to: 'trees' },
    { from: 'sliding_window', to: 'trees' },
    { from: 'linked_list', to: 'trees' },
    { from: 'trees', to: 'tries' },
    { from: 'trees', to: 'backtracking' },
    { from: 'trees', to: 'heap' },
    { from: 'backtracking', to: 'graphs' },
    { from: 'backtracking', to: 'dp_1d' },
    { from: 'heap', to: 'intervals' },
    { from: 'heap', to: 'greedy' },
    { from: 'heap', to: 'adv_graphs' },
    { from: 'graphs', to: 'adv_graphs' },
    { from: 'graphs', to: 'dp_2d' },
    { from: 'dp_1d', to: 'dp_2d' },
    { from: 'dp_1d', to: 'bit_manip' },
    { from: 'dp_2d', to: 'math' },
    { from: 'bit_manip', to: 'math' },
];

export default function RoadmapTree() {
    const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
    const [topicDetails, setTopicDetails] = useState<ProblemDetail[]>([]);
    const [loadingDetails, setLoadingDetails] = useState(false);
    const [viewingCode, setViewingCode] = useState<ProblemDetail | null>(null);
    const [nodes, setNodes] = useState(NODES);
    const [roadmapData, setRoadmapData] = useState<any[]>([]);
    const [mounted, setMounted] = useState(false);
    const [currentTopic, setCurrentTopic] = useState<any>(null);

    const { theme } = useTheme();
    const { token } = useAuth();

    useEffect(() => {
        setMounted(true);

        // Fetch focus topic from API
        if (token) {
            fetch('/api/user/focus', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.focus) {
                        setCurrentTopic(data.focus);
                    } else {
                        // Fallback to local storage
                        const saved = localStorage.getItem('currentTopic');
                        if (saved) {
                            try {
                                setCurrentTopic(JSON.parse(saved));
                            } catch (e) { }
                        }
                    }
                })
                .catch(err => console.error("Error fetching focus:", err));
        } else {
            // Fallback to local storage if not logged in
            const saved = localStorage.getItem('currentTopic');
            if (saved) {
                try {
                    setCurrentTopic(JSON.parse(saved));
                } catch (e) { }
            }
        }
    }, [token]);

    // Fetch progress from backend to update nodes
    useEffect(() => {
        fetch('/api/roadmap/leetcode')
            .then(res => res.json())
            .then(d => {
                if (d.success && d.roadmap) {
                    setRoadmapData(d.roadmap);
                    // Map backend progress to our static nodes
                    setNodes(prevNodes => prevNodes.map(node => {
                        const backendNode = d.roadmap.find((n: any) => n.topicId === node.id);

                        if (backendNode) {
                            return {
                                ...node,
                                progress: (backendNode.solvedProblems / Math.max(backendNode.totalProblems, 1)) * 100,
                                solved: backendNode.solvedProblems,
                                total: backendNode.totalProblems
                            };
                        }
                        return node;
                    }));
                }
            })
            .catch(err => console.error("Error fetching roadmap:", err));
    }, []);

    const handleNodeClick = (nodeId: string, label: string) => {
        setSelectedTopic(label);
        setLoadingDetails(false);
        setViewingCode(null);

        const topicData = roadmapData.find(t => t.topicId === nodeId);
        if (topicData) {
            setTopicDetails(topicData.problems.map((p: any) => ({
                problem_id: p.id,
                problem_name: p.title,
                solved: p.solved,
                difficulty: p.difficulty,
                leetcodeUrl: p.url,
                starred: false
            })));
        } else {
            setTopicDetails([]);
        }
    };

    const getDifficultyColor = (diff: string) => {
        switch (diff) {
            case 'Easy': return 'text-emerald-400';
            case 'Medium': return 'text-amber-400';
            case 'Hard': return 'text-red-400';
            default: return 'text-slate-400';
        }
    };

    if (!mounted) return <div className="p-8 text-center text-slate-400">Loading roadmap...</div>;

    return (
        <div className="relative w-full bg-[#0f172a] rounded-xl p-8 shadow-2xl border border-slate-800 overflow-hidden min-h-[800px]">
            <h3 className="text-white text-2xl font-bold mb-8 text-center tracking-tight">Learning Roadmap</h3>

            <div className="overflow-x-auto pb-4">
                <div className="min-w-[850px] flex justify-center relative">
                    <svg width="850" height="750" className="mx-auto">
                        <defs>
                            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                                <polygon points="0 0, 10 3.5, 0 7" fill="#475569" />
                            </marker>
                        </defs>

                        {/* Connections */}
                        {EDGES.map((edge, i) => {
                            const fromNode = nodes.find(n => n.id === edge.from);
                            const toNode = nodes.find(n => n.id === edge.to);
                            if (!fromNode || !toNode) return null;

                            // Calculate control points for curved lines
                            const midY = (fromNode.y + toNode.y) / 2;

                            return (
                                <path
                                    key={i}
                                    d={`M${fromNode.x},${fromNode.y + 25} C${fromNode.x},${midY} ${toNode.x},${midY} ${toNode.x},${toNode.y - 25}`}
                                    stroke="#475569"
                                    strokeWidth="2"
                                    fill="none"
                                    className="transition-all duration-500"
                                />
                            );
                        })}

                        {/* Nodes (rendered as HTML foreignObjects for better styling) */}
                        {nodes.map((node) => {
                            const isCurrentTopic = currentTopic && (
                                node.id === currentTopic.id ||
                                node.label.toLowerCase().includes(currentTopic.name.toLowerCase().split(' ')[0])
                            );

                            return (
                                <foreignObject
                                    key={node.id}
                                    x={node.x - 75}
                                    y={node.y - 25}
                                    width="150"
                                    height="50"
                                    className="overflow-visible"
                                >
                                    <div
                                        onClick={() => handleNodeClick(node.id, node.label)}
                                        className={`w-[150px] h-[50px] ${isCurrentTopic
                                            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 ring-2 ring-yellow-400 ring-offset-2 ring-offset-slate-950'
                                            : 'bg-indigo-600 hover:bg-indigo-500'
                                            } rounded-lg cursor-pointer transition-all duration-300 shadow-lg flex flex-col items-center justify-center relative group border border-indigo-400/30`}
                                    >
                                        <span className="text-white text-xs font-bold text-center px-2 leading-tight">{node.label}</span>

                                        {/* Progress Bar inside Node */}
                                        <div className="absolute bottom-2 w-3/4 h-1 bg-indigo-900/50 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-emerald-400 transition-all duration-500"
                                                style={{ width: `${node.progress}%` }}
                                            ></div>
                                        </div>

                                        {/* Hover Glow */}
                                        <div className="absolute inset-0 rounded-lg ring-2 ring-white/0 group-hover:ring-white/20 transition-all"></div>

                                        {/* Current Topic Avatar/Emoji */}
                                        {isCurrentTopic && currentTopic && (
                                            <div className="absolute -top-12 left-1/2 -translate-x-1/2 animate-bounce z-10">
                                                <div className="relative group/avatar">
                                                    {/* Glow effect */}
                                                    <div className={`absolute inset-0 blur-xl rounded-full ${theme === 'spiderman' ? 'bg-red-500/50' :
                                                            theme === 'batman' ? 'bg-yellow-400/50' :
                                                                'bg-indigo-500/50'
                                                        }`}></div>

                                                    {/* Avatar Image */}
                                                    <div className={`w-12 h-12 rounded-full border-2 shadow-xl flex items-center justify-center overflow-hidden bg-slate-900 ${theme === 'spiderman' ? 'border-red-500' :
                                                            theme === 'batman' ? 'border-yellow-400' :
                                                                'border-indigo-500'
                                                        }`}>
                                                        {theme === 'spiderman' ? (
                                                            <img src="/avatars/spiderman.png" alt="Spiderman" className="w-full h-full object-cover" />
                                                        ) : theme === 'batman' ? (
                                                            <img src="/avatars/batman.png" alt="Batman" className="w-full h-full object-cover" />
                                                        ) : (
                                                            <img src="/avatars/default.png" alt="Default" className="w-full h-full object-cover" />
                                                        )}
                                                    </div>

                                                    {/* Sparkle effect */}
                                                    <div className="absolute -top-1 -right-1 text-yellow-400 animate-pulse">
                                                        ✨
                                                    </div>

                                                    {/* Tooltip */}
                                                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover/avatar:opacity-100 transition-opacity whitespace-nowrap border border-slate-700">
                                                        Current Focus
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </foreignObject>
                            );
                        })}
                    </svg>
                </div>
            </div>

            {/* Topic Detail Popup (NeetCode Style) */}
            {selectedTopic && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                    <div className="bg-[#1e1e1e] w-full max-w-5xl h-[85vh] rounded-xl shadow-2xl border border-slate-700 flex flex-col overflow-hidden relative">

                        {/* Close Button */}
                        <button
                            onClick={() => setSelectedTopic(null)}
                            className="absolute top-4 right-4 p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors z-10"
                        >
                            <X size={20} />
                            <span className="sr-only">Close</span>
                        </button>

                        {/* Header */}
                        <div className="p-8 pb-6 bg-[#1e1e1e]">
                            <h2 className="text-3xl font-bold text-white mb-4">{selectedTopic}</h2>

                            {/* Progress Bar */}
                            <div className="flex items-center gap-4 mb-2">
                                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-emerald-500 rounded-full"
                                        style={{ width: `${(topicDetails.filter(p => p.solved).length / Math.max(topicDetails.length, 1)) * 100}%` }}
                                    ></div>
                                </div>
                                <span className="text-slate-400 text-sm font-medium">
                                    ({topicDetails.filter(p => p.solved).length} / {topicDetails.length})
                                </span>
                            </div>

                            {/* Prerequisites (Mock) */}
                            <div className="mt-6">
                                <h4 className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-3">Prerequisites</h4>
                                <div className="flex gap-3">
                                    <div className="px-4 py-3 bg-slate-800 rounded-lg border border-slate-700 w-48">
                                        <div className="flex justify-between items-start mb-1">
                                            <span className="text-slate-200 text-sm font-medium">Python Basics</span>
                                            <div className="w-3 h-3 rounded border border-slate-500"></div>
                                        </div>
                                        <span className="text-slate-500 text-xs">Language Fundamentals</span>
                                    </div>
                                    <div className="px-4 py-3 bg-slate-800 rounded-lg border border-slate-700 w-48">
                                        <div className="flex justify-between items-start mb-1">
                                            <span className="text-slate-200 text-sm font-medium">Time Complexity</span>
                                            <div className="w-3 h-3 rounded border border-slate-500"></div>
                                        </div>
                                        <span className="text-slate-500 text-xs">Big O Notation</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Content Area */}
                        <div className="flex-1 flex overflow-hidden border-t border-slate-800">

                            {/* Problem List Table */}
                            <div className={`${viewingCode ? 'w-1/2 border-r border-slate-800' : 'w-full'} overflow-y-auto bg-[#1e1e1e] p-6`}>
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="text-slate-500 text-xs border-b border-slate-800">
                                            <th className="py-3 font-medium pl-2">Status</th>
                                            <th className="py-3 font-medium">Star</th>
                                            <th className="py-3 font-medium w-full">Problem</th>
                                            <th className="py-3 font-medium">Difficulty</th>
                                            <th className="py-3 font-medium text-right pr-2">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody className="text-sm">
                                        {loadingDetails ? (
                                            <tr><td colSpan={5} className="py-8 text-center text-slate-500">Loading problems...</td></tr>
                                        ) : topicDetails.length === 0 ? (
                                            <tr><td colSpan={5} className="py-8 text-center text-slate-500">No problems found for this topic.</td></tr>
                                        ) : (
                                            topicDetails.map((prob, idx) => (
                                                <tr
                                                    key={prob.problem_id}
                                                    className={`group border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors ${viewingCode?.problem_id === prob.problem_id ? 'bg-indigo-900/10' : ''}`}
                                                >
                                                    <td className="py-3 pl-2">
                                                        <div className={`w-5 h-5 rounded border flex items-center justify-center ${prob.solved ? 'bg-emerald-500/20 border-emerald-500 text-emerald-500' : 'border-slate-600'}`}>
                                                            {prob.solved && <CheckCircle size={12} />}
                                                        </div>
                                                    </td>
                                                    <td className="py-3">
                                                        <Star size={16} className={`${prob.starred ? 'text-amber-400 fill-amber-400' : 'text-slate-600'}`} />
                                                    </td>
                                                    <td className="py-3">
                                                        <a
                                                            href={prob.leetcodeUrl}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-slate-200 font-medium hover:text-indigo-400 transition-colors text-left flex items-center gap-2"
                                                        >
                                                            {prob.problem_name}
                                                            <ExternalLink size={12} className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-500" />
                                                        </a>
                                                    </td>
                                                    <td className={`py-3 font-medium ${getDifficultyColor(prob.difficulty)}`}>
                                                        {prob.difficulty}
                                                    </td>
                                                    <td className="py-3 text-right pr-2">
                                                        <a
                                                            href={prob.leetcodeUrl}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="inline-flex p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors"
                                                        >
                                                            <ExternalLink size={16} />
                                                        </a>
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>

                            {/* Code & Notes Viewer (Slide-in) */}
                            {viewingCode && (
                                <div className="w-1/2 flex flex-col bg-[#1e1e1e] animate-in slide-in-from-right duration-300">
                                    <div className="p-4 border-b border-slate-800 bg-[#252526] flex justify-between items-center">
                                        <h3 className="font-bold text-slate-200 flex items-center gap-2">
                                            <Code size={16} className="text-indigo-400" />
                                            {viewingCode.problem_name}
                                        </h3>
                                        <button
                                            onClick={() => setViewingCode(null)}
                                            className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
                                        >
                                            Close <X size={12} />
                                        </button>
                                    </div>

                                    <div className="flex-1 overflow-y-auto custom-scrollbar">
                                        {/* Notes Section */}
                                        <div className="p-6 bg-indigo-950/10 border-b border-indigo-500/10">
                                            <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                                                <FileText size={14} /> My Notes & Approach
                                            </h4>
                                            <div className="prose prose-invert prose-sm max-w-none">
                                                <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                                                    {viewingCode.notes || "No notes added for this problem yet."}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Code Editor (Read Only) */}
                                        <div className="h-[400px] relative border-t border-slate-800">
                                            <CodeEditor
                                                initialCode={viewingCode.code || "# Code not available"}
                                                language={viewingCode.language || 'python'}
                                                readOnly={true}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
