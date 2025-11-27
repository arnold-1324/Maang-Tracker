'use client';

import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';

export default function MockInterviewCountdown() {
    const [timeLeft, setTimeLeft] = useState<{ days: number; hours: number; minutes: number; seconds: number } | null>(null);

    useEffect(() => {
        const calculateTimeLeft = () => {
            const now = new Date();
            const nextFriday = new Date();

            // Calculate days until next Friday (Day 5)
            const daysUntilFriday = (5 + 7 - now.getDay()) % 7;

            nextFriday.setDate(now.getDate() + daysUntilFriday);
            nextFriday.setHours(18, 0, 0, 0); // Schedule for 6:00 PM

            // If it's already past 6 PM on Friday, schedule for next week
            if (now > nextFriday) {
                nextFriday.setDate(nextFriday.getDate() + 7);
            }

            const difference = nextFriday.getTime() - now.getTime();

            if (difference > 0) {
                setTimeLeft({
                    days: Math.floor(difference / (1000 * 60 * 60 * 24)),
                    hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
                    minutes: Math.floor((difference / 1000 / 60) % 60),
                    seconds: Math.floor((difference / 1000) % 60),
                });
            }
        };

        calculateTimeLeft();
        const timer = setInterval(calculateTimeLeft, 1000);

        return () => clearInterval(timer);
    }, []);

    if (!timeLeft) return null;

    return (
        <div
            className="fixed bottom-6 right-6 p-4 rounded-xl shadow-2xl border backdrop-blur-md z-40"
            style={{
                backgroundColor: 'var(--card-bg)',
                borderColor: 'var(--accent-primary)',
                boxShadow: '0 0 20px rgba(0,0,0,0.3)'
            }}
        >
            <div className="flex items-center gap-3 mb-2">
                <Clock className="w-4 h-4 animate-pulse" style={{ color: 'var(--accent-primary)' }} />
                <span className="font-bold text-sm uppercase tracking-wider" style={{ color: 'var(--text-secondary)' }}>
                    Next Mock Interview
                </span>
            </div>
            <div className="flex gap-3 text-center">
                {Object.entries(timeLeft).map(([unit, value]) => (
                    <div key={unit} className="flex flex-col min-w-[40px]">
                        <span className="text-2xl font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
                            {String(value).padStart(2, '0')}
                        </span>
                        <span className="text-[10px] uppercase" style={{ color: 'var(--text-secondary)' }}>
                            {unit}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
