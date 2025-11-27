'use client';

import React, { useState, useEffect } from 'react';
import { Code2, Brain, Target, Trophy, Activity, SunMoon, Settings } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';

// Placeholder images for themes
const SPIDER_BG = "https://images.unsplash.com/photo-1635805737707-575885ab0820?q=80&w=2000&auto=format&fit=crop";
const BAT_BG = "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=2000&auto=format&fit=crop";

function IconButton({ onClick, children, className = '' }: any) {
  return (
    <button onClick={onClick} className={`p-2 rounded-full shadow-sm transition-transform hover:scale-105 ${className}`}>
      {children}
    </button>
  );
}

function StatsCard({ title, value, icon: Icon, accent }: any) {
  return (
    <div className="p-5 rounded-2xl bg-slate-800/70 border border-slate-700 shadow-md backdrop-blur-sm hover:bg-slate-800/80 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm text-slate-300 font-medium">{title}</div>
          <div className="text-2xl text-white font-extrabold mt-2">{value}</div>
        </div>
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${accent} text-white font-bold`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
}

function ChatInterface() {
  return (
    <div className="p-5 rounded-2xl bg-slate-800/55 border border-slate-700 shadow-sm backdrop-blur-sm">
      <div className="text-sm text-slate-300 mb-3 font-medium">Hello! I'm your MAANG Mentor. What shall we work on today?</div>
      <div className="flex gap-2">
        <input
          className="flex-1 rounded-lg p-3 bg-slate-900/60 border border-slate-700 text-slate-200 focus:outline-none focus:border-slate-500 placeholder:text-slate-500"
          placeholder="Ask about algorithms, system design..."
        />
        <button className="px-4 py-2 rounded-lg bg-yellow-500 text-black font-bold hover:bg-yellow-400 transition-colors shadow-lg shadow-yellow-500/20">Go</button>
      </div>
    </div>
  );
}

function SettingsModal({ isOpen, onClose, onSave }: any) {
  const [lc, setLc] = useState('');
  const [lcPass, setLcPass] = useState('');
  const [gh, setGh] = useState('');
  const [ghToken, setGhToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetch('/api/settings').then(r => r.json()).then(d => {
        setLc(d.leetcode_user || '');
        setGh(d.github_user || '');
      });
      setError('');
      setLcPass('');
      setGhToken('');
    }
  }, [isOpen]);

  const handleSave = async () => {
    setLoading(true);
    setError('');

    try {
      // Authenticate LeetCode if username and password provided
      if (lc && lcPass) {
        const lcAuthRes = await fetch('/api/leetcode-auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: lc, password: lcPass })
        });

        const lcAuthData = await lcAuthRes.json();
        if (!lcAuthData.success) {
          setError(`LeetCode: ${lcAuthData.error}`);
          setLoading(false);
          return;
        }
      }

      // Save GitHub settings
      const payload: any = { github_user: gh };
      if (ghToken) payload.github_token = ghToken;

      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      setLoading(false);
      onSave();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl w-96 max-h-[90vh] overflow-y-auto">
        <h3 className="text-xl font-bold text-white mb-4">Sync Settings</h3>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div className="border-b border-slate-700 pb-4">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">LeetCode</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Username</label>
                <input
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={lc}
                  onChange={e => setLc(e.target.value)}
                  placeholder="username"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Password</label>
                <input
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                  type="password"
                  value={lcPass}
                  onChange={e => setLcPass(e.target.value)}
                  placeholder="password"
                />
                <p className="text-[10px] text-slate-500 mt-1">We'll authenticate and store your session securely.</p>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">GitHub</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Username</label>
                <input
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={gh}
                  onChange={e => setGh(e.target.value)}
                  placeholder="username"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Personal Access Token</label>
                <input
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                  type="password"
                  value={ghToken}
                  onChange={e => setGhToken(e.target.value)}
                  placeholder="ghp_... (optional)"
                />
                <p className="text-[10px] text-slate-500 mt-1">Required for private repos.</p>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-700">
            <button
              onClick={onClose}
              className="px-4 py-2 text-slate-400 hover:text-white"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? 'Authenticating...' : 'Save & Sync'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const { theme, setTheme } = useTheme();
  const [stats, setStats] = useState({ solved: 142, mastery: 78, mocks: 8 });
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const refreshStats = () => {
    fetch('/api/sync-stats', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.leetcode?.data?.matchedUser?.submitStats?.acSubmissionNum) {
          const all = data.leetcode.data.matchedUser.submitStats.acSubmissionNum.find((x: any) => x.difficulty === 'All');
          if (all) setStats(s => ({ ...s, solved: all.count }));
        }
      })
      .catch(e => console.error("Failed to sync stats", e));
  };

  useEffect(() => {
    refreshStats();
  }, []);

  const themeProps: Record<string, any> = {
    default: {
      name: 'Default',
      accent: 'bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_8px_30px_rgba(99,102,241,0.12)]',
      bg: 'none',
      gradient: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
      barColor: 'bg-gradient-to-r from-indigo-500 to-purple-500',
      buttonClass: 'bg-indigo-600 text-white hover:bg-indigo-500'
    },
    spiderman: {
      name: 'Spider-Man',
      accent: 'bg-gradient-to-r from-[#ff6b6b] to-[#4f6ef6] shadow-[0_8px_30px_rgba(79,110,246,0.12)]',
      bg: `url('${SPIDER_BG}')`,
      gradient: `linear-gradient(180deg, rgba(6,10,18,0.96), rgba(10,12,16,0.98))`,
      barColor: 'bg-gradient-to-r from-[#ff6b6b] to-[#4f6ef6]',
      buttonClass: 'bg-gradient-to-r from-[#ff6b6b] to-[#4f6ef6] text-white shadow-lg shadow-red-500/20'
    },
    batman: {
      name: 'Batman',
      accent: 'bg-gradient-to-r from-[#ffd200] to-[#ffeb80] shadow-[0_8px_30px_rgba(255,210,0,0.12)]',
      bg: `url('${BAT_BG}')`,
      gradient: `linear-gradient(180deg, rgba(0,0,0,0.96), rgba(20,20,20,0.98))`,
      barColor: 'bg-gradient-to-r from-[#ffd200] to-[#ffeb80]',
      buttonClass: 'bg-gradient-to-r from-[#ffd200] to-[#ffeb80] text-black shadow-lg shadow-yellow-500/20'
    },
  };

  const props = themeProps[theme] || themeProps.default;

  return (
    <main
      data-theme={theme}
      className="min-h-screen font-sans text-slate-100 relative -m-8 p-8"
      style={{
        backgroundImage: theme === 'default' ? props.gradient : `${props.gradient}, ${props.bg}`,
        backgroundSize: 'cover',
        backgroundPosition: 'center center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed'
      }}
    >
      <style jsx global>{`
        .muted{ color: rgba(203,213,225,0.65); }
        .card-border{ border: 1px solid rgba(255,255,255,0.03); }
        .vignette{ position: absolute; inset: 0; pointer-events: none; background: radial-gradient(ellipse at center, rgba(0,0,0,0.4), rgba(0,0,0,0.7) 70%); z-index: 0; }
        .lift{ box-shadow: 0 10px 30px rgba(2,6,23,0.6); }
        @media (min-width:1024px){ .grid-wide{ grid-template-columns: 1fr 380px; } }
      `}</style>

      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} onSave={refreshStats} />

      <div className="container mx-auto max-w-7xl relative z-10">
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-lg p-3 ${props.accent} flex items-center justify-center text-white shadow-lg`}>
              <span className="font-bold text-xl">MA</span>
            </div>
            <div>
              <h1 className="text-4xl font-extrabold text-white tracking-tight drop-shadow-lg">Welcome Back!</h1>
              <p className="muted text-sm font-medium">Your journey to MAANG starts here. Let's make today count.</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="p-2 text-slate-400 hover:text-white bg-slate-800/50 rounded-lg border border-slate-700/50 transition-colors"
              title="Sync Settings"
            >
              <Settings size={20} />
            </button>

            <div className="flex items-center gap-2 bg-slate-800/50 p-1 rounded-xl border border-slate-700/50 backdrop-blur-sm">
              <button
                onClick={() => setTheme('default')}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${theme === 'default' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
              >
                Default
              </button>

              <button
                onClick={() => setTheme('spiderman')}
                className={`p-1 rounded-lg transition-all ${theme === 'spiderman' ? 'bg-red-600/20 shadow-lg ring-1 ring-red-500' : 'opacity-50 hover:opacity-100'}`}
                title="Spider-Man Theme"
              >
                <img src="/SpiderMan.jfif" alt="Spider-Man" className="w-8 h-8 object-cover rounded-md" />
              </button>

              <button
                onClick={() => setTheme('batman')}
                className={`p-1 rounded-lg transition-all ${theme === 'batman' ? 'bg-yellow-500/20 shadow-lg ring-1 ring-yellow-500' : 'opacity-50 hover:opacity-100'}`}
                title="Batman Theme"
              >
                <img src="/BatMan.jfif" alt="Batman" className="w-8 h-8 object-cover rounded-md" />
              </button>
            </div>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-3 mb-8">
          <div className="lg:col-span-2 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <StatsCard title="Problems Solved" value={stats.solved} icon={Code2} accent={props.accent} />
            <StatsCard title="Mastery Score" value={`${stats.mastery}/100`} icon={Trophy} accent={props.accent} />
            <StatsCard title="Mock Interviews" value={stats.mocks} icon={Brain} accent={props.accent} />
          </div>

          <div className="hidden lg:block">
            <div className="p-5 rounded-2xl bg-slate-800/60 border border-slate-700 lift backdrop-blur-sm h-full flex flex-col justify-center">
              <h3 className="text-slate-200 font-semibold mb-2 text-lg">MAANG Mentor</h3>
              <p className="muted text-sm">Hello! I can help you with coding problems, system design, or mock interviews.</p>
              <div className="mt-4 flex gap-2">
                <button className="px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-slate-100 hover:bg-slate-600 transition-colors">Start Mock</button>
                <button className="px-3 py-2 rounded-lg bg-transparent border border-slate-700 text-slate-200 hover:bg-slate-800 transition-colors">Roadmap</button>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-wide gap-8">
          <section className="p-6 rounded-2xl bg-slate-800/55 border border-slate-700 lift backdrop-blur-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Target className="text-slate-400" size={20} />
                Current Focus: Dynamic Programming
              </h2>
              <span className="muted text-sm font-medium bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700">Week 5 of 12</span>
            </div>

            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium muted">DP Patterns</span>
                  <span className="text-sm muted">65%</span>
                </div>
                <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden border border-slate-700/30">
                  <div style={{ width: '65%' }} className={`h-full rounded-full ${props.barColor} shadow-lg`} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium muted">Graph Theory</span>
                  <span className="text-sm muted">40%</span>
                </div>
                <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden border border-slate-700/30">
                  <div style={{ width: '40%' }} className={`h-full rounded-full ${props.barColor} shadow-lg`} />
                </div>
              </div>

              <div className="mt-8">
                <h3 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <Activity size={18} className="text-slate-400" />
                  Recommended Daily Tasks
                </h3>
                <div className="space-y-3">
                  <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-700 flex items-center justify-between hover:border-slate-600 transition-colors group">
                    <div>
                      <div className="text-slate-100 font-medium group-hover:text-white transition-colors">Climbing Stairs (LeetCode 70)</div>
                      <div className="text-xs muted mt-1">Easy • DP</div>
                    </div>
                    <button className={`px-4 py-2 rounded-lg font-bold text-sm transition-transform hover:scale-105 ${props.buttonClass}`}>Start</button>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-700 flex items-center justify-between hover:border-slate-600 transition-colors group">
                    <div>
                      <div className="text-slate-100 font-medium group-hover:text-white transition-colors">Longest Increasing Subsequence</div>
                      <div className="text-xs muted mt-1">Medium • DP • O(n log n)</div>
                    </div>
                    <button className={`px-4 py-2 rounded-lg font-bold text-sm transition-transform hover:scale-105 ${props.buttonClass}`}>Start</button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <aside className="space-y-6">
            <ChatInterface />

            <div className="p-5 rounded-2xl bg-slate-800/55 border border-slate-700 lift backdrop-blur-sm">
              <h4 className="text-slate-200 font-bold mb-2 flex items-center gap-2">
                <Trophy size={18} className="text-yellow-500" />
                Weekly Challenge
              </h4>
              <p className="muted text-sm mb-4">Complete 5 Medium DP problems to unlock the "Dynamic Dynamo" badge.</p>
              <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden border border-slate-700/30">
                <div className="h-full rounded-full bg-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.5)]" style={{ width: '40%' }} />
              </div>
            </div>
          </aside>
        </div>
      </div>

      <div className="vignette" />
    </main>
  );
}
