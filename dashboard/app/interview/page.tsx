'use client';

import React, { useState } from 'react';
import CodeEditor from '@/components/CodeEditor';
import ChatInterface from '@/components/ChatInterface';
import Whiteboard from '@/components/Whiteboard';
import { Code2, PenTool, MessageSquare, Building2, ChevronDown, Clock, LogOut } from 'lucide-react';

export default function InterviewPage() {
    const [activeView, setActiveView] = useState<'code' | 'whiteboard'>('code');
    const [company, setCompany] = useState('Google');
    const [role, setRole] = useState('Software Engineer (L4)');
    const [language, setLanguage] = useState('python');

    const languages = [
        { id: 'python', name: 'Python 3' },
        { id: 'java', name: 'Java' },
        { id: 'cpp', name: 'C++' },
        { id: 'csharp', name: 'C#' },
        { id: 'javascript', name: 'JavaScript' }
    ];

    const getInitialCode = (lang: string) => {
        switch (lang) {
            case 'python': return `class Solution:\n    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:\n        # Write your solution here\n        pass`;
            case 'java': return `class Solution {\n    public ListNode mergeKLists(ListNode[] lists) {\n        // Write your solution here\n        return null;\n    }\n}`;
            case 'cpp': return `class Solution {\npublic:\n    ListNode* mergeKLists(vector<ListNode*>& lists) {\n        // Write your solution here\n        return nullptr;\n    }\n};`;
            case 'csharp': return `public class Solution {\n    public ListNode MergeKLists(ListNode[] lists) {\n        // Write your solution here\n        return null;\n    }\n}`;
            case 'javascript': return `/**\n * @param {ListNode[]} lists\n * @return {ListNode}\n */\nvar mergeKLists = function(lists) {\n    // Write your solution here\n};`;
            default: return '';
        }
    };

    return (
        <div className="flex flex-col h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
            {/* Header */}
            <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-6 shadow-lg z-10">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse absolute top-0 right-0 -mt-1 -mr-1"></div>
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white">
                                IV
                            </div>
                        </div>
                        <h1 className="font-bold text-lg text-white tracking-tight">Live Session</h1>
                    </div>

                    <div className="h-8 w-px bg-slate-700/50"></div>

                    <div className="flex items-center gap-4">
                        <div className="relative group">
                            <Building2 size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-indigo-400 transition-colors" />
                            <select
                                value={company}
                                onChange={(e) => setCompany(e.target.value)}
                                className="pl-9 pr-8 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-sm font-medium text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none appearance-none cursor-pointer hover:bg-slate-750 transition-colors"
                            >
                                <option>Google</option>
                                <option>Meta</option>
                                <option>Amazon</option>
                                <option>Netflix</option>
                                <option>Apple</option>
                            </select>
                            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
                        </div>

                        <div className="relative group">
                            <select
                                value={role}
                                onChange={(e) => setRole(e.target.value)}
                                className="pl-4 pr-8 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-sm font-medium text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none appearance-none cursor-pointer hover:bg-slate-750 transition-colors"
                            >
                                <option>Software Engineer (L3)</option>
                                <option>Software Engineer (L4)</option>
                                <option>Senior SWE (L5)</option>
                                <option>System Design Lead</option>
                            </select>
                            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 rounded-md border border-slate-700/50">
                        <Clock size={14} className="text-emerald-400" />
                        <span className="text-sm font-mono text-emerald-400 font-medium">00:45:23</span>
                    </div>
                    <button className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 text-sm font-medium rounded-lg border border-red-500/20 transition-all">
                        <LogOut size={16} />
                        End Session
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left Panel: Problem Description */}
                <div className="w-1/4 min-w-[320px] bg-slate-900 border-r border-slate-800 flex flex-col">
                    <div className="p-6 border-b border-slate-800">
                        <div className="flex justify-between items-start mb-4">
                            <h2 className="font-bold text-white text-xl leading-tight">Merge k Sorted Lists</h2>
                        </div>
                        <div className="flex flex-wrap gap-2 mb-6">
                            <span className="px-2.5 py-1 bg-red-500/10 text-red-400 text-xs font-medium rounded-full border border-red-500/20">Hard</span>
                            <span className="px-2.5 py-1 bg-slate-800 text-slate-300 text-xs font-medium rounded-full border border-slate-700">Linked List</span>
                            <span className="px-2.5 py-1 bg-slate-800 text-slate-300 text-xs font-medium rounded-full border border-slate-700">Heap</span>
                            <span className="px-2.5 py-1 bg-slate-800 text-slate-300 text-xs font-medium rounded-full border border-slate-700">Divide & Conquer</span>
                        </div>
                        <div className="prose prose-invert prose-sm max-w-none">
                            <p className="text-slate-300 leading-relaxed">
                                You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.
                            </p>
                            <p className="text-slate-300 leading-relaxed mt-2">
                                Merge all the linked-lists into one sorted linked-list and return it.
                            </p>
                        </div>
                    </div>
                    <div className="flex-1 p-6 overflow-y-auto">
                        <div className="mb-6">
                            <h3 className="text-sm font-bold text-slate-200 mb-3">Example 1:</h3>
                            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed">
                                <span className="text-indigo-400">Input:</span> lists = [[1,4,5],[1,3,4],[2,6]]<br />
                                <span className="text-emerald-400">Output:</span> [1,1,2,3,4,4,5,6]
                            </div>
                        </div>

                        <div>
                            <h3 className="text-sm font-bold text-slate-200 mb-3">Constraints:</h3>
                            <ul className="space-y-2 text-xs text-slate-400 font-mono bg-slate-800/30 p-4 rounded-lg border border-slate-800/50">
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-indigo-500"></div>k == lists.length</li>
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-indigo-500"></div>0 &lt;= k &lt;= 10^4</li>
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-indigo-500"></div>0 &lt;= lists[i].length &lt;= 500</li>
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-indigo-500"></div>-10^4 &lt;= lists[i][j] &lt;= 10^4</li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Middle Panel: Workspace */}
                <div className="flex-1 flex flex-col min-w-[500px] bg-[#1e1e1e]">
                    {/* Tabs & Language Selector */}
                    <div className="flex justify-between items-center border-b border-slate-800 bg-[#1e1e1e] px-2">
                        <div className="flex">
                            <button
                                onClick={() => setActiveView('code')}
                                className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-all border-b-2 ${activeView === 'code' ? 'text-white border-indigo-500 bg-slate-800/30' : 'text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/20'}`}
                            >
                                <Code2 size={16} /> Code Editor
                            </button>
                            <button
                                onClick={() => setActiveView('whiteboard')}
                                className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-all border-b-2 ${activeView === 'whiteboard' ? 'text-white border-indigo-500 bg-slate-800/30' : 'text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/20'}`}
                            >
                                <PenTool size={16} /> Whiteboard
                            </button>
                        </div>

                        {activeView === 'code' && (
                            <div className="pr-4">
                                <select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                    className="bg-slate-800 text-slate-300 text-xs border border-slate-700 rounded px-3 py-1.5 focus:ring-1 focus:ring-indigo-500 outline-none cursor-pointer"
                                >
                                    {languages.map(lang => (
                                        <option key={lang.id} value={lang.id}>{lang.name}</option>
                                    ))}
                                </select>
                            </div>
                        )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 relative">
                        {activeView === 'code' ? (
                            <CodeEditor
                                language={language}
                                problemId="merge-k-sorted-lists"
                                initialCode={getInitialCode(language)}
                            />
                        ) : (
                            <Whiteboard />
                        )}
                    </div>
                </div>

                {/* Right Panel: AI Mentor */}
                <div className="w-[380px] border-l border-slate-800 bg-slate-900 flex flex-col shadow-xl z-10">
                    <div className="p-4 border-b border-slate-800 bg-slate-900 flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                            <MessageSquare size={18} />
                        </div>
                        <div>
                            <h3 className="font-bold text-sm text-white">AI Interviewer</h3>
                            <p className="text-xs text-slate-500">Always here to help</p>
                        </div>
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <ChatInterface />
                    </div>
                </div>
            </div>
        </div>
    );
}
