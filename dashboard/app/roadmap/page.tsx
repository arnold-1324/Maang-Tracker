'use client';

import RoadmapTree from '@/components/RoadmapTree';

export default function RoadmapPage() {
    return (
        <div className="min-h-screen bg-slate-950 py-8">
            <div className="container mx-auto px-4">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">Learning Roadmap</h1>
                    <p className="text-slate-400">Track your progress across all DSA topics</p>
                </div>
                <RoadmapTree />
            </div>
        </div>
    );
}
