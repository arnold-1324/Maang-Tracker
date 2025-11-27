'use client';

import React, { useState } from 'react';
import Sidebar from './Sidebar';
import MockInterviewCountdown from './MockInterviewCountdown';
import { ThemeProvider } from '@/context/ThemeContext';

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <ThemeProvider>
            <div className="flex min-h-screen transition-colors duration-500">
                <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
                <main
                    className={`flex-1 transition-all duration-300 p-8 ${collapsed ? 'ml-20' : 'ml-64'}`}
                >
                    {children}
                </main>
                <MockInterviewCountdown />
            </div>
        </ThemeProvider>
    );
}
