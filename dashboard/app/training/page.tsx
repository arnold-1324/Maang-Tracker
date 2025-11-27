'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, CheckCircle, Clock, ExternalLink, Award, TrendingUp, Sparkles } from 'lucide-react';
import PdfReaderModal from '@/components/PdfReaderModal';

interface Resource {
    id: string;
    title: string;
    type: 'dsa' | 'system_design';
    url: string;
    filename?: string;
    status: 'Not Started' | 'In Progress' | 'Completed';
}

// Utility functions
const getStatusColor = (status: string) => {
    switch (status) {
        case 'Completed': return 'bg-emerald-500/20 border-emerald-500 text-emerald-400';
        case 'In Progress': return 'bg-amber-500/20 border-amber-500 text-amber-400';
        default: return 'bg-slate-700/50 border-slate-600 text-slate-400';
    }
};

const getStatusIcon = (status: string) => {
    switch (status) {
        case 'Completed': return <CheckCircle className="w-5 h-5" />;
        case 'In Progress': return <Clock className="w-5 h-5" />;
        default: return <BookOpen className="w-5 h-5" />;
    }
};

const calculateProgress = (resources: Resource[]) => {
    if (resources.length === 0) return 0;
    const completed = resources.filter(r => r.status === 'Completed').length;
    return Math.round((completed / resources.length) * 100);
};

export default function TrainingPage() {
    const [resources, setResources] = useState<Resource[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedBook, setSelectedBook] = useState<Resource | null>(null);

    useEffect(() => {
        fetchResources();
    }, []);

    const fetchResources = async () => {
        try {
            const res = await fetch('http://localhost:5100/api/training/resources');
            const data = await res.json();
            if (data.success) {
                setResources(data.resources);
            }
        } catch (error) {
            console.error('Error fetching resources:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateStatus = async (resource: Resource, newStatus: string) => {
        try {
            await fetch('http://localhost:5100/api/training/progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resource_id: resource.id,
                    title: resource.title,
                    type: resource.type,
                    status: newStatus
                })
            });
            // Update local state
            setResources(prev => prev.map(r =>
                r.id === resource.id ? { ...r, status: newStatus as any } : r
            ));
        } catch (error) {
            console.error('Error updating status:', error);
        }
    };

    const dsaResources = resources.filter(r => r.type === 'dsa');
    const sysDesignResources = resources.filter(r => r.type === 'system_design');

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent"></div>
                    <p className="text-slate-400 mt-4">Loading your learning journey...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10"></div>
                <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10"></div>

                <div className="relative max-w-7xl mx-auto px-6 py-16">
                    <div className="text-center mb-12">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full mb-6">
                            <Sparkles className="w-4 h-4 text-indigo-400" />
                            <span className="text-sm text-indigo-300 font-medium">Mastery Center</span>
                        </div>
                        <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                            Your Learning Universe
                        </h1>
                        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                            Master the fundamentals and build expertise with curated resources tracked intelligently.
                        </p>
                    </div>

                    {/* Stats Overview */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-3">
                                <Award className="w-8 h-8 text-emerald-400" />
                                <span className="text-3xl font-bold text-emerald-400">
                                    {resources.filter(r => r.status === 'Completed').length}
                                </span>
                            </div>
                            <p className="text-slate-300 font-medium">Completed</p>
                            <p className="text-sm text-slate-500">Resources mastered</p>
                        </div>

                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-3">
                                <TrendingUp className="w-8 h-8 text-amber-400" />
                                <span className="text-3xl font-bold text-amber-400">
                                    {resources.filter(r => r.status === 'In Progress').length}
                                </span>
                            </div>
                            <p className="text-slate-300 font-medium">In Progress</p>
                            <p className="text-sm text-slate-500">Currently learning</p>
                        </div>

                        <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-3">
                                <BookOpen className="w-8 h-8 text-indigo-400" />
                                <span className="text-3xl font-bold text-indigo-400">
                                    {resources.length}
                                </span>
                            </div>
                            <p className="text-slate-300 font-medium">Total Resources</p>
                            <p className="text-sm text-slate-500">In your library</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-6 pb-16">
                {/* DSA Section */}
                <section className="mb-16">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-3xl font-bold text-white mb-2">Data Structures & Algorithms</h2>
                            <p className="text-slate-400">Build your problem-solving foundation</p>
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-bold text-indigo-400">{calculateProgress(dsaResources)}%</div>
                            <div className="text-sm text-slate-500">Complete</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6">
                        {dsaResources.map((resource) => (
                            <ResourceCard
                                key={resource.id}
                                resource={resource}
                                onStatusChange={updateStatus}
                                onOpenBook={setSelectedBook}
                            />
                        ))}
                    </div>
                </section>

                {/* System Design Section */}
                <section>
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-3xl font-bold text-white mb-2">System Design Mastery</h2>
                            <p className="text-slate-400">Scale your architectural knowledge</p>
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-bold text-purple-400">{calculateProgress(sysDesignResources)}%</div>
                            <div className="text-sm text-slate-500">Complete</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {sysDesignResources.map((resource) => (
                            <ResourceCard
                                key={resource.id}
                                resource={resource}
                                onStatusChange={updateStatus}
                                onOpenBook={setSelectedBook}
                            />
                        ))}
                    </div>
                </section>
            </div>

            {/* PDF Reader Modal */}
            {selectedBook && (
                <PdfReaderModal
                    resource={selectedBook}
                    onClose={() => setSelectedBook(null)}
                />
            )}
        </div>
    );
}

function ResourceCard({ resource, onStatusChange, onOpenBook }: { resource: Resource; onStatusChange: (r: Resource, s: string) => void; onOpenBook: (r: Resource) => void }) {
    const [showMenu, setShowMenu] = useState(false);

    const statuses = ['Not Started', 'In Progress', 'Completed'];

    return (
        <div className="group bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 hover:border-indigo-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/10">
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-indigo-300 transition-colors">
                        {resource.title}
                    </h3>
                    <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg border text-sm font-medium ${getStatusColor(resource.status)}`}>
                            {getStatusIcon(resource.status)}
                            {resource.status}
                        </span>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-3">
                {resource.type === 'system_design' ? (
                    <button
                        onClick={() => onOpenBook(resource)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-lg text-white font-medium transition-all shadow-lg shadow-indigo-500/30"
                    >
                        <Sparkles className="w-4 h-4" />
                        Open Advanced Reader
                    </button>
                ) : (
                    <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-medium transition-colors"
                    >
                        <ExternalLink className="w-4 h-4" />
                        Open Resource
                    </a>
                )}

                <div className="relative">
                    <button
                        onClick={() => setShowMenu(!showMenu)}
                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-slate-300 font-medium transition-colors"
                    >
                        Update Status
                    </button>

                    {showMenu && (
                        <div className="absolute right-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-10">
                            {statuses.map((status) => (
                                <button
                                    key={status}
                                    onClick={() => {
                                        onStatusChange(resource, status);
                                        setShowMenu(false);
                                    }}
                                    className={`w-full text-left px-4 py-2 hover:bg-slate-700 transition-colors first:rounded-t-lg last:rounded-b-lg ${resource.status === status ? 'bg-slate-700 text-indigo-400' : 'text-slate-300'
                                        }`}
                                >
                                    {status}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
