'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Settings, Github, Code2, Save, Loader2 } from 'lucide-react';

export default function SettingsPage() {
    const { token } = useAuth();
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    // LeetCode credentials
    const [leetcodeUsername, setLeetcodeUsername] = useState('');
    const [leetcodePassword, setLeetcodePassword] = useState('');

    // GitHub credentials
    const [githubToken, setGithubToken] = useState('');

    const handleSaveLeetCode = async () => {
        if (!leetcodeUsername || !leetcodePassword) {
            setError('Please enter both username and password');
            return;
        }

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch('/api/credentials/leetcode', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: leetcodeUsername,
                    password: leetcodePassword,
                }),
            });

            const data = await response.json();

            if (data.success) {
                setSuccess('LeetCode credentials saved successfully!');
                setLeetcodePassword(''); // Clear password for security
            } else {
                setError(data.error || 'Failed to save LeetCode credentials');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSaveGitHub = async () => {
        if (!githubToken) {
            setError('Please enter GitHub access token');
            return;
        }

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch('/api/credentials/github', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    access_token: githubToken,
                }),
            });

            const data = await response.json();

            if (data.success) {
                setSuccess('GitHub credentials saved successfully!');
            } else {
                setError(data.error || 'Failed to save GitHub credentials');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-3 mb-2">
                        <Settings className="text-indigo-500" size={32} />
                        <h1 className="text-4xl font-bold text-white">Settings</h1>
                    </div>
                    <p className="text-slate-400">Configure your platform credentials</p>
                </div>

                {/* Success/Error Messages */}
                {success && (
                    <div className="mb-6 bg-emerald-500/10 border border-emerald-500/50 rounded-lg p-4 text-emerald-400">
                        {success}
                    </div>
                )}
                {error && (
                    <div className="mb-6 bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-400">
                        {error}
                    </div>
                )}

                {/* LeetCode Section */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 mb-6 shadow-2xl">
                    <div className="flex items-center gap-3 mb-6">
                        <Code2 className="text-orange-500" size={24} />
                        <h2 className="text-2xl font-bold text-white">LeetCode</h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Username
                            </label>
                            <input
                                type="text"
                                value={leetcodeUsername}
                                onChange={(e) => setLeetcodeUsername(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                                placeholder="Enter your LeetCode username"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Password / Session Cookie
                            </label>
                            <input
                                type="password"
                                value={leetcodePassword}
                                onChange={(e) => setLeetcodePassword(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                                placeholder="Enter password or LEETCODE_SESSION cookie"
                            />
                            <p className="text-xs text-slate-500 mt-2">
                                You can use either your password or LeetCode session cookie
                            </p>
                        </div>

                        <button
                            onClick={handleSaveLeetCode}
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-orange-500/50 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin" size={20} />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save size={20} />
                                    Save LeetCode Credentials
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* GitHub Section */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 shadow-2xl">
                    <div className="flex items-center gap-3 mb-6">
                        <Github className="text-purple-500" size={24} />
                        <h2 className="text-2xl font-bold text-white">GitHub</h2>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Personal Access Token
                            </label>
                            <input
                                type="password"
                                value={githubToken}
                                onChange={(e) => setGithubToken(e.target.value)}
                                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                                placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                            />
                            <p className="text-xs text-slate-500 mt-2">
                                Generate a token at{' '}
                                <a
                                    href="https://github.com/settings/tokens"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-indigo-400 hover:text-indigo-300 underline"
                                >
                                    github.com/settings/tokens
                                </a>
                            </p>
                        </div>

                        <button
                            onClick={handleSaveGitHub}
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/50 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="animate-spin" size={20} />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save size={20} />
                                    Save GitHub Token
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
