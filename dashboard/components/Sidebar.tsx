'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Code, TrendingUp, AlertTriangle, Video, Target, BookOpen, ChevronRight, ChevronLeft, Palette } from 'lucide-react';
import { useTheme, Theme } from '@/context/ThemeContext';

interface SidebarProps {
    collapsed: boolean;
    setCollapsed: (value: boolean) => void;
}

export default function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
    const pathname = usePathname();
    const { theme, setTheme } = useTheme();

    const navItems = [
        { href: '/', label: 'Home', icon: Home },
        { href: '/roadmap', label: 'Roadmap', icon: Target },
        { href: '/training', label: 'Training', icon: BookOpen },
        { href: '/interview', label: 'Interview', icon: Video },
        { href: '/progress', label: 'Progress', icon: TrendingUp },
        { href: '/weakness', label: 'Weakness', icon: AlertTriangle },
    ];

    const themes: { id: Theme; label: string; color: string }[] = [
        { id: 'default', label: 'Default', color: '#4f46e5' },
        { id: 'spiderman', label: 'Spider-Man', color: '#ef4444' },
        { id: 'batman', label: 'Batman', color: '#fbbf24' },
    ];

    return (
        <aside
            className={`fixed left-0 top-0 h-screen transition-all duration-300 z-50 flex flex-col border-r shadow-xl
                ${collapsed ? 'w-20' : 'w-64'}
            `}
            style={{
                backgroundColor: 'var(--bg-secondary)',
                borderColor: 'var(--border-color)'
            }}
        >
            {/* Logo Area */}
            <div className="h-20 flex items-center justify-center border-b" style={{ borderColor: 'var(--border-color)' }}>
                <Link href="/" className="flex items-center gap-3 overflow-hidden px-4">
                    <div className="min-w-[40px] h-10 rounded-lg flex items-center justify-center"
                        style={{ background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))' }}
                    >
                        <Code className="text-white" size={20} />
                    </div>
                    {!collapsed && (
                        <span className="text-xl font-bold whitespace-nowrap" style={{ color: 'var(--text-primary)' }}>
                            MAANG Mentor
                        </span>
                    )}
                </Link>
            </div>

            {/* Navigation Links */}
            <nav className="flex-1 py-6 px-3 space-y-2 overflow-y-auto">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 px-3 py-3 rounded-lg transition-all group relative
                                ${isActive ? 'bg-opacity-20' : 'hover:bg-opacity-10'}
                            `}
                            style={{
                                backgroundColor: isActive ? 'var(--accent-primary)' : 'transparent',
                                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)'
                            }}
                        >
                            <Icon size={20} style={{ color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)' }} />
                            {!collapsed && <span className="font-medium">{item.label}</span>}

                            {/* Tooltip for collapsed state */}
                            {collapsed && (
                                <div className="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
                                    {item.label}
                                </div>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Theme Switcher */}
            <div className="p-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
                {!collapsed ? (
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                            <Palette size={16} />
                            <span>Theme</span>
                        </div>
                        <div className="grid grid-cols-3 gap-2">
                            {themes.map((t) => (
                                <button
                                    key={t.id}
                                    onClick={() => setTheme(t.id)}
                                    className={`h-8 rounded-md border-2 transition-all flex items-center justify-center overflow-hidden ${theme === t.id ? 'scale-110 shadow-lg border-white' : 'opacity-70 hover:opacity-100 border-transparent'}`}
                                    style={{
                                        backgroundColor: t.id === 'default' ? t.color : 'transparent',
                                    }}
                                    title={t.label}
                                >
                                    {t.id === 'default' && <span className="text-[10px] font-bold text-white uppercase tracking-wider">Default</span>}
                                    {t.id === 'spiderman' && <img src="/SpiderMan.jfif" alt="Spider" className="w-full h-full object-cover rounded-md" />}
                                    {t.id === 'batman' && <img src="/BatMan.jfif" alt="Bat" className="w-full h-full object-cover rounded-md" />}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <button
                        onClick={() => setCollapsed(false)}
                        className="w-full flex justify-center p-2 rounded-lg hover:bg-slate-800 transition-colors"
                    >
                        <Palette size={20} style={{ color: 'var(--accent-primary)' }} />
                    </button>
                )}
            </div>

            {/* Collapse Toggle */}
            <button
                onClick={() => setCollapsed(!collapsed)}
                className="absolute -right-3 top-24 w-6 h-6 rounded-full flex items-center justify-center shadow-lg border transition-colors"
                style={{
                    backgroundColor: 'var(--bg-secondary)',
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-primary)'
                }}
            >
                {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            </button>
        </aside>
    );
}
