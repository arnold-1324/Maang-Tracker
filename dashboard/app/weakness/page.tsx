'use client';

import React, { useEffect, useState } from 'react';
import { AlertTriangle, TrendingDown, Target, BookOpen, Zap } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface WeaknessData {
    category: string;
    severity: 'High' | 'Medium' | 'Low';
    problems_attempted: number;
    success_rate: number;
    avg_attempts: number;
    recommended_problems: Array<{
        id: string;
        name: string;
        difficulty: string;
        url: string;
    }>;
    improvement_plan: string[];
}

export default function WeaknessPage() {
    const { token, isAuthenticated, isLoading: authLoading } = useAuth();
    const [weaknesses, setWeaknesses] = useState<WeaknessData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!authLoading && isAuthenticated && token) {
            fetch('/api/weaknesses', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
                .then(res => res.json())
                .then(d => {
                    if (d.success && d.weaknesses) {
                        // Transform from DB format to component format
                        const transformed = d.weaknesses.map((w: any) => ({
                            category: w.weakness_name,
                            severity: w.severity_score > 7 ? 'High' : w.severity_score > 4 ? 'Medium' : 'Low',
                            problems_attempted: 0, // TODO: extract from evidence
                            success_rate: 0, // TODO: extract from evidence
                            avg_attempts: 0, // TODO: extract from evidence
                            recommended_problems: [], // TODO: parse from recommendations
                            improvement_plan: JSON.parse(w.recommendations || '[]')
                        }));
                        setWeaknesses(transformed);
                    }
                    setLoading(false);
                })
                .catch(() => setLoading(false));
        } else if (!authLoading && !isAuthenticated) {
            setLoading(false);
        }
    }, [token, isAuthenticated, authLoading]);

    // Mock data
    const mockWeaknesses: WeaknessData[] = [
        {
            category: 'Dynamic Programming',
            severity: 'High',
            problems_attempted: 15,
            success_rate: 40,
            avg_attempts: 3.2,
            recommended_problems: [
                { id: 'climbing-stairs', name: 'Climbing Stairs', difficulty: 'Easy', url: 'https://leetcode.com/problems/climbing-stairs' },
                { id: 'house-robber', name: 'House Robber', difficulty: 'Medium', url: 'https://leetcode.com/problems/house-robber' },
            ],
            improvement_plan: [
                'Start with 1-D DP problems to build foundation',
                'Practice identifying optimal substructure',
                'Master memoization and tabulation techniques'
            ]
        },
        {
            category: 'Graph Algorithms',
            severity: 'High',
            problems_attempted: 8,
            success_rate: 37.5,
            avg_attempts: 2.8,
            recommended_problems: [
                { id: 'number-of-islands', name: 'Number of Islands', difficulty: 'Medium', url: 'https://leetcode.com/problems/number-of-islands' },
                { id: 'course-schedule', name: 'Course Schedule', difficulty: 'Medium', url: 'https://leetcode.com/problems/course-schedule' },
            ],
            improvement_plan: [
                'Review BFS and DFS traversal patterns',
                'Practice cycle detection in graphs',
                'Master topological sorting'
            ]
        },
        {
            category: 'Backtracking',
            severity: 'Medium',
            problems_attempted: 10,
            success_rate: 60,
            avg_attempts: 2.1,
            recommended_problems: [
                { id: 'subsets', name: 'Subsets', difficulty: 'Medium', url: 'https://leetcode.com/problems/subsets' },
                { id: 'permutations', name: 'Permutations', difficulty: 'Medium', url: 'https://leetcode.com/problems/permutations' },
            ],
            improvement_plan: [
                'Practice decision tree visualization',
                'Master pruning techniques',
                'Improve base case identification'
            ]
        }
    ];

    const data = weaknesses.length > 0 ? weaknesses : mockWeaknesses;

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'High': return 'text-red-400 bg-red-500/10 border-red-500/20';
            case 'Medium': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
            case 'Low': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
            default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="text-slate-400 animate-pulse">Analyzing weaknesses...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 py-8">
            <div className="container mx-auto px-4 max-w-7xl">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
                        <AlertTriangle className="text-red-400" size={36} />
                        Weakness Analysis
                    </h1>
                    <p className="text-slate-400">AI-identified areas for improvement based on your interview performance</p>
                </div>

                {/* Weaknesses List */}
                <div className="space-y-6">
                    {data.map((weakness, idx) => (
                        <div key={idx} className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                            {/* Header */}
                            <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center">
                                        <TrendingDown className="text-red-400" size={24} />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold text-white">{weakness.category}</h2>
                                        <p className="text-sm text-slate-400">
                                            {weakness.problems_attempted} problems attempted • {weakness.success_rate}% success rate
                                        </p>
                                    </div>
                                </div>
                                <div className={`px-4 py-2 rounded-full border font-medium ${getSeverityColor(weakness.severity)}`}>
                                    {weakness.severity} Priority
                                </div>
                            </div>

                            {/* Content */}
                            <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Recommended Problems */}
                                <div>
                                    <div className="flex items-center gap-2 mb-4">
                                        <Target size={18} className="text-indigo-400" />
                                        <h3 className="font-bold text-white">Recommended Problems</h3>
                                    </div>
                                    <div className="space-y-3">
                                        {weakness.recommended_problems.map((problem, i) => (
                                            <a
                                                key={i}
                                                href={problem.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="block p-4 bg-slate-800/50 hover:bg-slate-800 rounded-lg border border-slate-700 transition-all group"
                                            >
                                                <div className="flex justify-between items-start mb-1">
                                                    <span className="text-white font-medium group-hover:text-indigo-400 transition-colors">
                                                        {problem.name}
                                                    </span>
                                                    <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">
                                                        {problem.difficulty}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-slate-500">{problem.id}</p>
                                            </a>
                                        ))}
                                    </div>
                                </div>

                                {/* Improvement Plan */}
                                <div>
                                    <div className="flex items-center gap-2 mb-4">
                                        <BookOpen size={18} className="text-emerald-400" />
                                        <h3 className="font-bold text-white">Improvement Plan</h3>
                                    </div>
                                    <div className="space-y-3">
                                        {weakness.improvement_plan.map((step, i) => (
                                            <div key={i} className="flex items-start gap-3">
                                                <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                                                    <Zap size={14} className="text-emerald-400" />
                                                </div>
                                                <p className="text-sm text-slate-300 leading-relaxed">{step}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Stats Bar */}
                            <div className="px-6 py-4 bg-slate-800/30 border-t border-slate-800 flex items-center justify-between text-sm">
                                <div className="text-slate-400">
                                    Avg. Attempts: <span className="text-white font-medium">{weakness.avg_attempts}</span>
                                </div>
                                <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors font-medium">
                                    Start Practice
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {/* AI Summary */}
                <div className="mt-8 bg-gradient-to-r from-indigo-900/20 to-purple-900/20 rounded-xl p-6 border border-indigo-500/20">
                    <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                        <Zap size={20} className="text-indigo-400" />
                        AI Strategy Recommendation
                    </h3>
                    <p className="text-slate-300 leading-relaxed">
                        Based on your performance analysis, focus on <strong className="text-white">Dynamic Programming</strong> and <strong className="text-white">Graph Algorithms</strong> before your next interview.
                        Dedicate at least 2 hours daily to these topics. Start with Easy problems to build confidence, then progress to Medium difficulty.
                        The AI mentor will adjust your roadmap as you improve.
                    </p>
                </div>
            </div>
        </div>
    );
}
