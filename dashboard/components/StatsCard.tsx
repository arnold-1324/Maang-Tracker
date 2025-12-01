import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    trend?: string;
    trendUp?: boolean;
    color?: string;
}

export default function StatsCard({ title, value, icon: Icon, trend, trendUp, color = "indigo" }: StatsCardProps) {
    const colorClasses = {
        indigo: "from-indigo-500 to-blue-500",
        purple: "from-purple-500 to-pink-500",
        emerald: "from-emerald-500 to-teal-500",
        amber: "from-amber-500 to-orange-500",
    };

    const bgGradient = colorClasses[color as keyof typeof colorClasses] || colorClasses.indigo;

    return (
        <div className="bg-white/80 backdrop-blur-sm p-6 rounded-xl shadow-lg border border-white/50 hover:transform hover:-translate-y-1 transition-all duration-300">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-sm font-medium text-gray-500">{title}</p>
                    <h3 className="text-3xl font-bold text-gray-800 mt-1">{value}</h3>
                </div>
                <div className={`p-3 rounded-lg bg-gradient-to-br ${bgGradient} text-white shadow-md`}>
                    <Icon size={24} />
                </div>
            </div>
            {trend && (
                <div className="mt-4 flex items-center text-sm">
                    <span className={`font-medium ${trendUp ? 'text-emerald-600' : 'text-red-600'}`}>
                        {trendUp ? '↑' : '↓'} {trend}
                    </span>
                    <span className="text-gray-400 ml-2">vs last week</span>
                </div>
            )}
        </div>
    );
}
