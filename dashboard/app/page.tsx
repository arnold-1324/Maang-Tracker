'use client';

import React, { useState, useEffect } from 'react';
import {
  Code2, Brain, Target, Trophy, Activity, Settings, RefreshCw,
  AlertTriangle, CheckCircle2, Sparkles, Flame, BookOpen, Zap,
  TrendingUp, X, Search, Download
} from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

// Topic Selection Modal Component
function TopicSelectionModal({ isOpen, onClose, onSelect, currentTopic }: any) {
  const topics = [
    { id: 'arrays', name: 'Arrays & Hashing', emoji: '📊', color: 'from-blue-500 to-cyan-500' },
    { id: 'two-pointers', name: 'Two Pointers', emoji: '👉👈', color: 'from-purple-500 to-pink-500' },
    { id: 'sliding-window', name: 'Sliding Window', emoji: '🪟', color: 'from-green-500 to-emerald-500' },
    { id: 'stack', name: 'Stack', emoji: '📚', color: 'from-orange-500 to-red-500' },
    { id: 'binary-search', name: 'Binary Search', emoji: '🔍', color: 'from-indigo-500 to-purple-500' },
    { id: 'linked-list', name: 'Linked List', emoji: '🔗', color: 'from-teal-500 to-cyan-500' },
    { id: 'trees', name: 'Trees', emoji: '🌳', color: 'from-green-600 to-lime-500' },
    { id: 'tries', name: 'Tries', emoji: '🌲', color: 'from-emerald-600 to-green-500' },
    { id: 'heap', name: 'Heap / Priority Queue', emoji: '⛰️', color: 'from-amber-500 to-orange-500' },
    { id: 'backtracking', name: 'Backtracking', emoji: '🔙', color: 'from-rose-500 to-pink-500' },
    { id: 'graphs', name: 'Graphs', emoji: '🕸️', color: 'from-violet-500 to-purple-500' },
    { id: 'dp', name: 'Dynamic Programming', emoji: '🧮', color: 'from-fuchsia-500 to-pink-500' },
    { id: 'greedy', name: 'Greedy', emoji: '💰', color: 'from-yellow-500 to-amber-500' },
    { id: 'intervals', name: 'Intervals', emoji: '📏', color: 'from-blue-600 to-indigo-500' },
    { id: 'math', name: 'Math & Geometry', emoji: '📐', color: 'from-cyan-500 to-blue-500' },
    { id: 'bit-manipulation', name: 'Bit Manipulation', emoji: '🔢', color: 'from-slate-500 to-gray-500' },
  ];

  const [searchTerm, setSearchTerm] = useState('');
  const filteredTopics = topics.filter(t =>
    t.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl border border-slate-700 shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
        {/* Header */}
        <div className="p-6 border-b border-slate-700 bg-gradient-to-r from-indigo-900/20 to-purple-900/20">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                <Sparkles className="text-white" size={24} />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">What are you learning?</h2>
                <p className="text-slate-400 text-sm">Select your current focus topic</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <X className="text-slate-400" size={20} />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              type="text"
              placeholder="Search topics..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-600 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>
        </div>

        {/* Topics Grid */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {filteredTopics.map((topic) => (
              <button
                key={topic.id}
                onClick={() => {
                  onSelect(topic);
                  onClose();
                }}
                className={`group relative p-4 rounded-xl border-2 transition-all duration-200 hover:scale-105 ${currentTopic?.id === topic.id
                  ? 'border-indigo-500 bg-indigo-500/10'
                  : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                  }`}
              >
                <div className="text-center">
                  <div className="text-4xl mb-2">{topic.emoji}</div>
                  <div className="text-sm font-semibold text-white group-hover:text-indigo-400 transition-colors">
                    {topic.name}
                  </div>
                </div>
                {currentTopic?.id === topic.id && (
                  <div className="absolute top-2 right-2">
                    <CheckCircle2 className="text-indigo-500" size={16} />
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Enhanced Stats Card with animations
function EnhancedStatsCard({ title, value, icon: Icon, gradient, trend }: any) {
  return (
    <div className={`group relative p-6 rounded-2xl bg-gradient-to-br ${gradient} shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 overflow-hidden`}>
      {/* Animated background */}
      <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      <div className="relative flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="text-sm text-white/80 font-medium mb-1">{title}</div>
          <div className="text-3xl text-white font-black tracking-tight">{value}</div>
          {trend && (
            <div className="flex items-center gap-1 mt-2 text-xs text-white/70">
              <TrendingUp size={14} />
              <span>{trend}</span>
            </div>
          )}
        </div>
        <div className="w-14 h-14 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
          <Icon size={28} className="text-white" />
        </div>
      </div>
    </div>
  );
}

// Daily Task Card
function DailyTaskCard({ task, onStart }: any) {
  return (
    <div className="group p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-indigo-500/50 hover:bg-slate-800/70 transition-all duration-200">
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1">
          <h4 className="font-semibold text-white mb-1">{task.title}</h4>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className={`px-2 py-0.5 rounded-full ${task.difficulty === 'Easy' ? 'bg-green-500/20 text-green-400' :
              task.difficulty === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-red-500/20 text-red-400'
              }`}>
              {task.difficulty}
            </span>
            <span>•</span>
            <span>{task.topic}</span>
          </div>
        </div>
        <button
          onClick={() => onStart(task)}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-colors shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40"
        >
          Start
        </button>
      </div>
    </div>
  );
}

export default function Home() {
  const { theme, toggleTheme } = useTheme();
  const { isAuthenticated, token, logout } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState({ solved: 0, mastery: 0, interviews: 0 });
  const [weaknesses, setWeaknesses] = useState<any[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showTopicModal, setShowTopicModal] = useState(false);
  const [currentTopic, setCurrentTopic] = useState<any>(null);
  const [dailyTasks, setDailyTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState<string>('');
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Load current topic from API
    fetchData();
  }, [isAuthenticated, token]);

  const fetchData = async () => {
    if (!token) return;

    try {
      setLoading(true);

      // Fetch current user info
      try {
        const userRes = await fetch('/api/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const userData = await userRes.json();
        if (userData.success && userData.user) {
          setUserEmail(userData.user.email || '');
        }
      } catch (e) {
        console.error("Failed to fetch user info", e);
      }

      // Fetch User Focus
      try {
        const focusRes = await fetch('/api/user/focus', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const focusData = await focusRes.json();
        if (focusData.success && focusData.focus) {
          setCurrentTopic(focusData.focus);
          localStorage.setItem('currentTopic', JSON.stringify(focusData.focus));
        } else {
          // Fallback to local storage if API returns nothing (first time)
          const saved = localStorage.getItem('currentTopic');
          if (saved) {
            setCurrentTopic(JSON.parse(saved));
          } else {
            setShowTopicModal(true);
          }
        }
      } catch (e) {
        console.error("Failed to fetch focus", e);
      }

      // Fetch LeetCode stats
      const lcRes = await fetch('/api/sync/leetcode', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ force_refresh: false })
      });
      const lcData = await lcRes.json();

      if (lcData.success && lcData.data) {
        setStats(s => ({ ...s, solved: lcData.data.total_solved || 0 }));
      }

      // Fetch Weaknesses
      const weakRes = await fetch('/api/weaknesses', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const weakData = await weakRes.json();
      if (weakData.success) {
        setWeaknesses(weakData.weaknesses);
        generateDailyTasks(weakData.weaknesses);
      }

      setLoading(false);
    } catch (e) {
      console.error("Failed to fetch data", e);
      setLoading(false);
    }
  };

  const generateDailyTasks = (weaknesses: any[]) => {
    // Generate tasks based on weaknesses
    const tasks = [];

    if (weaknesses.length > 0) {
      // Add tasks from weaknesses
      weaknesses.slice(0, 3).forEach((w, i) => {
        const recs = JSON.parse(w.recommendations || '[]');
        if (recs.length > 0) {
          tasks.push({
            id: `weakness-${i}`,
            title: recs[0],
            difficulty: w.severity_score > 7 ? 'Hard' : w.severity_score > 5 ? 'Medium' : 'Easy',
            topic: w.weakness_name,
            leetcodeUrl: '#'
          });
        }
      });
    }

    // Add default tasks if not enough
    if (tasks.length === 0) {
      tasks.push(
        { id: '1', title: 'Two Sum', difficulty: 'Easy', topic: 'Arrays', leetcodeUrl: 'https://leetcode.com/problems/two-sum' },
        { id: '2', title: 'Longest Substring Without Repeating Characters', difficulty: 'Medium', topic: 'Sliding Window', leetcodeUrl: 'https://leetcode.com/problems/longest-substring-without-repeating-characters' }
      );
    }

    setDailyTasks(tasks);
  };

  const handleTopicSelect = async (topic: any) => {
    setCurrentTopic(topic);
    localStorage.setItem('currentTopic', JSON.stringify(topic));

    // Save to API
    if (token) {
      try {
        await fetch('/api/user/focus', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(topic)
        });
      } catch (e) {
        console.error("Failed to save topic", e);
      }
    }
  };

  const handleSync = async () => {
    if (!token) return;

    try {
      await fetch('/api/sync/all', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      fetchData();
    } catch (e) {
      console.error("Sync failed", e);
    }
  };

  const handleDownloadExcel = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch('/api/export/excel', {
        method: 'GET',
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        a.download = `maang_tracker_export_${timestamp}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Export failed');
        alert('Failed to export database. Please try again.');
      }
    } catch (e) {
      console.error("Download failed", e);
      alert('Failed to download Excel file. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400 animate-pulse">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Topic Selection Modal */}
      <TopicSelectionModal
        isOpen={showTopicModal}
        onClose={() => setShowTopicModal(false)}
        onSelect={handleTopicSelect}
        currentTopic={currentTopic}
      />

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 mb-2">
              Welcome Back, Arnold!
            </h1>
            <p className="text-slate-400">Your journey to MAANG starts here. Let's make today count.</p>
          </div>

          <div className="flex items-center gap-3">
            {/* Excel Export Button - Only for arnold */}
            {userEmail === 'arnoldgna765@gmail.com' && (
              <button
                onClick={handleDownloadExcel}
                disabled={isDownloading}
                className="flex items-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 border border-green-500/30 transition-all duration-200 shadow-lg shadow-green-500/20 hover:shadow-green-500/40 disabled:opacity-50 disabled:cursor-not-allowed group"
                title="Download Database Export (Excel)"
              >
                {isDownloading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span className="text-white font-medium text-sm">Exporting...</span>
                  </>
                ) : (
                  <>
                    <Download className="text-white group-hover:scale-110 transition-transform" size={20} />
                    <span className="text-white font-medium text-sm">Export DB</span>
                  </>
                )}
              </button>
            )}
            <button
              onClick={handleSync}
              className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors group"
            >
              <RefreshCw className="text-slate-400 group-hover:text-indigo-400 group-hover:rotate-180 transition-all duration-500" size={20} />
            </button>
            <button
              onClick={() => setShowSettings(true)}
              className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
            >
              <Settings className="text-slate-400" size={20} />
            </button>
          </div>
        </div>

        {/* Current Learning Topic Banner */}
        {currentTopic && (
          <div className={`mb-8 p-6 rounded-2xl bg-gradient-to-r ${currentTopic.color} shadow-lg relative overflow-hidden group cursor-pointer`}
            onClick={() => setShowTopicModal(true)}>
            <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-6xl">{currentTopic.emoji}</div>
                <div>
                  <div className="text-sm text-white/80 font-medium mb-1">Currently Learning</div>
                  <div className="text-2xl font-black text-white">{currentTopic.name}</div>
                </div>
              </div>
              <button className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white font-medium transition-colors">
                Change Topic
              </button>
            </div>
          </div>
        )}

        {!currentTopic && (
          <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-indigo-900/20 to-purple-900/20 border border-indigo-500/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Sparkles className="text-indigo-400" size={32} />
                <div>
                  <div className="text-lg font-bold text-white mb-1">What are you learning today?</div>
                  <div className="text-sm text-slate-400">Select a topic to get personalized recommendations</div>
                </div>
              </div>
              <button
                onClick={() => setShowTopicModal(true)}
                className="px-6 py-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-colors shadow-lg shadow-indigo-500/20"
              >
                Choose Topic
              </button>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <EnhancedStatsCard
            title="Problems Solved"
            value={stats.solved}
            icon={Code2}
            gradient="from-indigo-600 to-purple-600"
            trend="+12 this week"
          />
          <EnhancedStatsCard
            title="Mastery Score"
            value={`${stats.mastery}/100`}
            icon={Trophy}
            gradient="from-amber-500 to-orange-500"
            trend="Top 15%"
          />
          <EnhancedStatsCard
            title="Mock Interviews"
            value={stats.interviews}
            icon={Target}
            gradient="from-emerald-500 to-teal-500"
            trend="2 scheduled"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Daily Tasks & AI Analysis */}
          <div className="lg:col-span-2 space-y-6">
            {/* Recommended Daily Tasks */}
            <section className="p-6 rounded-2xl bg-slate-800/55 border border-slate-700 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                    <Flame className="text-white" size={20} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">Recommended Daily Tasks</h2>
                    <p className="text-xs text-slate-400">Based on your weaknesses</p>
                  </div>
                </div>
                <span className="text-xs font-medium bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full border border-indigo-500/30">
                  {dailyTasks.length} tasks
                </span>
              </div>

              <div className="space-y-3">
                {dailyTasks.map((task) => (
                  <DailyTaskCard
                    key={task.id}
                    task={task}
                    onStart={(t: any) => window.open(t.leetcodeUrl, '_blank')}
                  />
                ))}
              </div>
            </section>

            {/* AI Weakness Analysis */}
            <section className="p-6 rounded-2xl bg-gradient-to-br from-slate-800/55 to-slate-900/55 border border-slate-700 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
                    <Brain className="text-white" size={20} />
                  </div>
                  <h2 className="text-xl font-bold text-white">AI Weakness Analysis</h2>
                </div>
                <span className="text-xs font-medium bg-slate-700 text-slate-300 px-3 py-1 rounded-full">
                  {weaknesses.length} Insights Found
                </span>
              </div>

              <div className="space-y-4">
                {weaknesses.length === 0 ? (
                  <div className="text-center py-8 text-slate-400">
                    <CheckCircle2 size={48} className="mx-auto mb-3 text-green-500/50" />
                    <p>No major weaknesses detected yet. Keep practicing!</p>
                    <p className="text-xs mt-2 opacity-50">Sync your LeetCode data to get insights.</p>
                  </div>
                ) : (
                  weaknesses.slice(0, 3).map((weakness, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-700/50 hover:border-slate-600/50 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-slate-200 flex items-center gap-2">
                          <AlertTriangle size={16} className="text-yellow-500" />
                          {weakness.weakness_name}
                        </h3>
                        <span className={`text-xs font-bold px-2 py-1 rounded ${weakness.severity_score > 7 ? 'bg-red-500/20 text-red-400 border border-red-500/20' :
                          weakness.severity_score > 5 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/20' :
                            'bg-blue-500/20 text-blue-400 border border-blue-500/20'
                          }`}>
                          Severity: {weakness.severity_score}/10
                        </span>
                      </div>
                      <p className="text-sm text-slate-400 mb-3">{weakness.ai_analysis}</p>

                      <div className="space-y-2">
                        {JSON.parse(weakness.recommendations || '[]').slice(0, 2).map((rec: string, i: number) => (
                          <div key={i} className="flex items-center gap-2 text-xs text-slate-300">
                            <Zap size={12} className="text-indigo-400" />
                            {rec}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </div>

          {/* Right Column - MAANG Mentor */}
          <div className="space-y-6">
            <section className="p-6 rounded-2xl bg-gradient-to-br from-indigo-900/20 to-purple-900/20 border border-indigo-500/30 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                  <Brain className="text-white" size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-white">MAANG Mentor</h3>
                  <p className="text-xs text-slate-400">AI-powered guidance</p>
                </div>
              </div>

              <p className="text-sm text-slate-300 mb-4">
                Hello! I can help you with coding problems, system design, or mock interviews.
              </p>

              <div className="space-y-2">
                <button className="w-full px-4 py-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-left text-sm text-white transition-colors border border-slate-700">
                  <BookOpen size={16} className="inline mr-2 text-indigo-400" />
                  Start Mock Interview
                </button>
                <button className="w-full px-4 py-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-left text-sm text-white transition-colors border border-slate-700">
                  <Target size={16} className="inline mr-2 text-emerald-400" />
                  View Roadmap
                </button>
              </div>
            </section>

            {/* Next Mock Interview */}
            <section className="p-6 rounded-2xl bg-slate-800/55 border border-slate-700 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-4">
                <Activity className="text-indigo-400" size={20} />
                <h3 className="font-bold text-white">NEXT MOCK INTERVIEW</h3>
              </div>

              <div className="text-center py-6">
                <div className="flex items-center justify-center gap-4 mb-2">
                  <div className="text-center">
                    <div className="text-3xl font-black text-white">06</div>
                    <div className="text-xs text-slate-400">DAYS</div>
                  </div>
                  <div className="text-2xl text-slate-600">:</div>
                  <div className="text-center">
                    <div className="text-3xl font-black text-white">06</div>
                    <div className="text-xs text-slate-400">HOURS</div>
                  </div>
                  <div className="text-2xl text-slate-600">:</div>
                  <div className="text-center">
                    <div className="text-3xl font-black text-white">58</div>
                    <div className="text-xs text-slate-400">MINUTES</div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
