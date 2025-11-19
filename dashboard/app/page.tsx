'use client';

import React from 'react';
import ChatInterface from '@/components/ChatInterface';
import StatsCard from '@/components/StatsCard';
import { Code2, Brain, Target, Trophy, Activity } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100">
      {/* Background Gradients */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-[40%] -left-[20%] w-[70%] h-[70%] rounded-full bg-purple-200/30 blur-3xl"></div>
        <div className="absolute top-[20%] -right-[20%] w-[60%] h-[60%] rounded-full bg-indigo-200/30 blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <header className="mb-10">
          <h1 className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 mb-4">
            Welcome Back!
          </h1>
          <p className="text-slate-500 text-lg">Your journey to MAANG starts here. Let's make today count.</p>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <StatsCard
            title="Problems Solved"
            value="142"
            icon={Code2}
            trend="12%"
            trendUp={true}
            color="indigo"
          />
          <StatsCard
            title="Mastery Score"
            value="78/100"
            icon={Trophy}
            trend="5%"
            trendUp={true}
            color="amber"
          />
          <StatsCard
            title="Mock Interviews"
            value="8"
            icon={Brain}
            trend="2"
            trendUp={true}
            color="purple"
          />
          <StatsCard
            title="System Design"
            value="Level 4"
            icon={Activity}
            color="emerald"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-8">
            {/* Progress Section */}
            <section className="bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <Target className="text-indigo-600" />
                  Current Focus: Dynamic Programming
                </h2>
                <span className="text-sm font-medium text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">Week 5 of 12</span>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700">DP Patterns</span>
                    <span className="text-slate-500">65%</span>
                  </div>
                  <div className="h-2.5 bg-slate-200 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 w-[65%] rounded-full"></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700">Graph Theory</span>
                    <span className="text-slate-500">40%</span>
                  </div>
                  <div className="h-2.5 bg-slate-200 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 w-[40%] rounded-full"></div>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-slate-200">
                <h3 className="font-semibold text-slate-800 mb-3">Recommended Daily Tasks</h3>
                <div className="space-y-3">
                  <div className="flex items-center p-3 bg-white rounded-lg border border-slate-100 shadow-sm hover:shadow-md transition-shadow cursor-pointer group">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 mr-3"></div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-800 group-hover:text-indigo-600 transition-colors">Climbing Stairs (LeetCode 70)</p>
                      <p className="text-xs text-slate-500">Easy • Dynamic Programming</p>
                    </div>
                    <button className="text-xs bg-slate-100 hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 px-3 py-1 rounded-md transition-colors">Start</button>
                  </div>

                  <div className="flex items-center p-3 bg-white rounded-lg border border-slate-100 shadow-sm hover:shadow-md transition-shadow cursor-pointer group">
                    <div className="w-2 h-2 rounded-full bg-amber-500 mr-3"></div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-800 group-hover:text-indigo-600 transition-colors">Longest Increasing Subsequence</p>
                      <p className="text-xs text-slate-500">Medium • DP • O(n log n)</p>
                    </div>
                    <button className="text-xs bg-slate-100 hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 px-3 py-1 rounded-md transition-colors">Start</button>
                  </div>
                </div>
              </div>
            </section>

            {/* Recent Activity */}
            <section className="bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg">
              <h2 className="text-xl font-bold text-slate-800 mb-4">Recent Activity</h2>
              <div className="relative border-l-2 border-slate-200 ml-3 space-y-6 pl-6 pb-2">
                <div className="relative">
                  <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-white shadow-sm"></div>
                  <p className="text-sm text-slate-500 mb-1">Today, 10:23 AM</p>
                  <p className="font-medium text-slate-800">Solved "Merge Intervals"</p>
                  <p className="text-sm text-slate-600">Optimized solution using sorting. Time complexity: O(n log n).</p>
                </div>
                <div className="relative">
                  <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-indigo-500 border-2 border-white shadow-sm"></div>
                  <p className="text-sm text-slate-500 mb-1">Yesterday, 4:15 PM</p>
                  <p className="font-medium text-slate-800">System Design Session</p>
                  <p className="text-sm text-slate-600">Designed a URL Shortener service. Focus on database schema and collision handling.</p>
                </div>
              </div>
            </section>
          </div>

          {/* Sidebar / Chat */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <ChatInterface />

              <div className="mt-6 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl p-6 text-white shadow-lg">
                <h3 className="font-bold text-lg mb-2">Weekly Challenge</h3>
                <p className="text-indigo-100 text-sm mb-4">Complete 5 Medium DP problems to unlock the "Dynamic Dynamo" badge.</p>
                <div className="flex justify-between items-center text-sm mb-2">
                  <span>Progress</span>
                  <span>2/5</span>
                </div>
                <div className="h-2 bg-indigo-900/50 rounded-full overflow-hidden">
                  <div className="h-full bg-white w-[40%]"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
