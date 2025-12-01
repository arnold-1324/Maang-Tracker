'use client';

import React, { useState } from 'react';
import Sidebar from './Sidebar';
import MockInterviewCountdown from './MockInterviewCountdown';
import { ThemeProvider } from '@/context/ThemeContext';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { usePathname } from 'next/navigation';

function LayoutContent({ children }: { children: React.ReactNode }) {
    const [collapsed, setCollapsed] = useState(false);
    const { isAuthenticated, isLoading } = useAuth();
    const pathname = usePathname();
    const isAuthPage = pathname === '/login' || pathname === '/signup';

    // Prevent flashing of protected content
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-950">
                <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (isAuthPage) {
        return <>{children}</>;
    }

    if (!isAuthenticated) {
        // If not authenticated and not on auth page, the page component (e.g., Home)
        // should handle the redirect to /login. We render children to allow that logic to run.
        return <>{children}</>;
    }

    return (
        <div className="flex min-h-screen transition-colors duration-500">
            <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
            <main
                className={`flex-1 transition-all duration-300 p-8 ${collapsed ? 'ml-20' : 'ml-64'}`}
            >
                {children}
            </main>
            <MockInterviewCountdown />
        </div>
    );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
    return (
        <AuthProvider>
            <ThemeProvider>
                <LayoutContent>{children}</LayoutContent>
            </ThemeProvider>
        </AuthProvider>
    );
}
