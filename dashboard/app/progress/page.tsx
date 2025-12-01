'use client';

import React, { useEffect, useState } from 'react';
import { TrendingUp, Target, Award, Calendar, Clock, Brain } from 'lucide-react';
import StatsCard from '@/components/StatsCard';
import { useAuth } from '@/context/AuthContext';

interface ProgressData {
    overall_mastery: number;
    problems_solved: number;
    total_problems: number;
    topics_mastered: number;
    total_topics: number;
    avg_time_per_problem: number;
    interview_sessions: number;
    recent_activity: Array<{
        date: string;
        topic: string;
        problems_solved: number;
        time_spent: number;
    }>;
    weak_areas: string[];
    strong_areas: string[];
    recommendations: string[];
}

export default function ProgressPage() {
    const { token, isAuthenticated, isLoading: authLoading } = useAuth();
    const [data, setData] = useState<ProgressData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!authLoading && isAuthenticated && token) {
            fetch('/api/user/progress', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
                .then(res => res.json())
                .then(d => {
                    if (d.success) {
                        setData(d.data);
                    }
                    setLoading(false);
                })
                .catch(err => {
                    console.error(err);
                    setLoading(false);
                });
        } else if (!authLoading && !isAuthenticated) {
            setLoading(false);
        }
    }, [token, isAuthenticated, authLoading]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="text-slate-400 animate-pulse">Loading progress...</div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="min-h-screen bg-slate-950 py-8 flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-xl font-bold text-white mb-2">No Progress Data Available</h2>
                    <p className="text-slate-400">Please sync your LeetCode account in settings to see your progress.</p>
                </div>
            </div>
        );
    }

    const progressData = data;

    return (
        <div className="min-h-screen bg-slate-950 py-8">
            <div className="container mx-auto px-4 max-w-7xl">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">Progress Tracker</h1>
                    <p className="text-slate-400">AI-powered analytics of your interview preparation journey</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                    <StatsCard
                        title="Overall Mastery"
                        value={`${Math.round(progressData.overall_mastery)}%`}
                        icon={Brain}
                        color="indigo"
                        trend={`${progressData.problems_solved}/${progressData.total_problems}`}
                        trendUp={true}
                    />
                    <StatsCard
                        title="Topics Mastered"
                        value={`${progressData.topics_mastered}/${progressData.total_topics}`}
                        icon={Target}
                        color="emerald"
                    />
                    <StatsCard
                        title="Avg Time/Problem"
                        value={`${progressData.avg_time_per_problem}m`}
                        icon={Clock}
                        color="amber"
                    />
                    <StatsCard
                        title="Mock Interviews"
                        value={progressData.interview_sessions.toString()}
                        icon={Award}
                        color="purple"
                    />
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Recent Activity */}
                    <div className="lg:col-span-2 bg-slate-900 rounded-xl p-6 border border-slate-800">
                        <div className="flex items-center gap-2 mb-6">
                            <Calendar size={20} className="text-indigo-400" />
                            <h2 className="text-xl font-bold text-white">Recent Activity</h2>
                        </div>

                        <div className="space-y-4">
                            {progressData.recent_activity.map((activity, idx) => (
                                <div key={idx} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                    <div>
                                        <p className="text-white font-medium">{activity.topic}</p>
                                        <p className="text-sm text-slate-400">{activity.date}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-emerald-400 font-bold">{activity.problems_solved} problems</p>
                                        <p className="text-xs text-slate-500">{activity.time_spent} minutes</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* AI Insights */}
                    <div className="space-y-6">
                        {/* Strong Areas */}
                        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Award size={18} className="text-emerald-400" />
                                <h3 className="font-bold text-white">Strong Areas</h3>
                            </div>
                            <div className="space-y-2">
                                {progressData.strong_areas.map((area, idx) => (
                                    <div key={idx} className="px-3 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-300 text-sm">
                                        {area}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Weak Areas */}
                        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
                            <div className="flex items-center gap-2 mb-4">
                                <Target size={18} className="text-red-400" />
                                <h3 className="font-bold text-white">Needs Improvement</h3>
                            </div>
                            <div className="space-y-2">
                                {progressData.weak_areas.map((area, idx) => (
                                    <div key={idx} className="px-3 py-2 bg-red-500/10 border border-red-500/20 rounded-lg text-red-300 text-sm">
                                        {area}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* AI Recommendations */}
                <div className="mt-8 bg-gradient-to-r from-indigo-900/20 to-purple-900/20 rounded-xl p-6 border border-indigo-500/20">
                    <div className="flex items-center gap-2 mb-4">
                        <Brain size={20} className="text-indigo-400" />
                        <h2 className="text-xl font-bold text-white">AI Recommendations</h2>
                    </div>
                    <div className="space-y-3">
                        {progressData.recommendations.map((rec, idx) => (
                            <div key={idx} className="flex items-start gap-3 text-slate-300">
                                <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <span className="text-indigo-400 text-xs font-bold">{idx + 1}</span>
                                </div>
                                <p className="text-sm leading-relaxed">{rec}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
