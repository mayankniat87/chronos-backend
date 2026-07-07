'use client';

import React, { useState } from 'react';
import { useSettingsStore } from '@/store/settingsStore';
import { useAuthStore } from '@/store/authStore';
import {
  Settings,
  User,
  Database,
  Bell
} from 'lucide-react';

export default function SettingsPage() {
  const {
    apiBaseUrl,
    demoMode,
    notificationsEnabled,
    setApiBaseUrl,
    setDemoMode,
    setNotificationsEnabled
  } = useSettingsStore();

  const { user } = useAuthStore();

  const [inputUrl, setInputUrl] = useState(apiBaseUrl);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSaveApiUrl = (e: React.FormEvent) => {
    e.preventDefault();
    setApiBaseUrl(inputUrl);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  return (
    <div className="space-y-8 font-sans max-w-4xl mx-auto">
      
      {/* Top Header */}
      <div>
        <h1 className="text-3xl font-extrabold font-outfit text-white tracking-tight">System Settings</h1>
        <p className="text-slate-400 text-xs mt-1 font-medium">
          Configure API endpoints, user profile contexts, alerts, and toggle mock sandbox engines.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
        
        {/* Navigation Sidebar Panel shortcuts */}
        <div className="glass-card p-4 rounded-2xl space-y-2">
          <button className="w-full text-left p-3 rounded-xl border border-blue-500/20 bg-blue-500/5 text-blue-400 text-xs font-semibold flex items-center gap-2.5">
            <Settings className="h-4.5 w-4.5" />
            <span>Terminal Configurations</span>
          </button>
          <button className="w-full text-left p-3 rounded-xl border border-transparent hover:bg-slate-900/40 text-slate-400 hover:text-slate-200 text-xs font-semibold flex items-center gap-2.5">
            <User className="h-4.5 w-4.5" />
            <span>Operator Identity</span>
          </button>
        </div>

        {/* Configurations Forms */}
        <div className="md:col-span-2 space-y-6">
          
          {/* Target API configurations */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-4">
              <Database className="h-4.5 w-4.5 text-blue-400" />
              <h3 className="text-sm font-bold font-outfit text-white uppercase tracking-wider">FastAPI Endpoint Routing</h3>
            </div>

            <form onSubmit={handleSaveApiUrl} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Base URL Address</label>
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={inputUrl}
                    onChange={(e) => setInputUrl(e.target.value)}
                    placeholder="http://localhost:8000"
                    className="flex-1 px-4 py-2.5 rounded-xl text-xs glass-input text-slate-200"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all shadow-md shadow-blue-500/10 cursor-pointer"
                  >
                    Save Routing
                  </button>
                </div>
                {saveSuccess && (
                  <p className="text-[10px] text-emerald-400 font-semibold mt-1">API routing address updated successfully.</p>
                )}
              </div>
            </form>

            <div className="flex items-center justify-between p-4 rounded-xl border border-slate-800 bg-slate-900/10 text-xs text-slate-400">
              <div className="space-y-0.5 pr-2">
                <span className="font-bold text-slate-300 block">Sandbox Mock Engine (Demo Mode)</span>
                <p className="text-[11px] leading-relaxed">
                  Bypass standard API requests and serve pre-compiled mockup arrays for demo evaluation.
                </p>
              </div>
              <button
                onClick={() => setDemoMode(!demoMode)}
                className={`px-4 py-2 rounded-xl border text-xs font-bold uppercase transition-all cursor-pointer ${
                  demoMode
                    ? 'bg-amber-500/10 border-amber-500/25 text-amber-400'
                    : 'border-slate-850 hover:bg-slate-800 text-slate-500 hover:text-slate-350'
                }`}
              >
                {demoMode ? 'Sandbox Active' : 'Sandbox Off'}
              </button>
            </div>
          </div>

          {/* User profile segment */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-4">
              <User className="h-4.5 w-4.5 text-blue-400" />
              <h3 className="text-sm font-bold font-outfit text-white uppercase tracking-wider">Operator Profile</h3>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-[10px] text-slate-500 font-bold block mb-1">NAME</span>
                <span className="text-xs font-semibold text-slate-200">{user?.name || 'Chronos Administrator'}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 font-bold block mb-1">EMAIL</span>
                <span className="text-xs font-semibold text-slate-250 truncate block">{user?.email || 'admin@chronos.ai'}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 font-bold block mb-1">ASSIGNED ROLE</span>
                <span className="text-xs font-semibold text-slate-300">{user?.role || 'Restaurant Operator'}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 font-bold block mb-1">ENVIRONMENT</span>
                <span className="text-xs font-semibold text-blue-400">Development v1.0.0</span>
              </div>
            </div>
          </div>

          {/* Alerting notifications config */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-4">
              <Bell className="h-4.5 w-4.5 text-blue-400" />
              <h3 className="text-sm font-bold font-outfit text-white uppercase tracking-wider">Alert Routing</h3>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400">
              <div className="space-y-0.5">
                <span className="font-bold text-slate-300 block">Simulation Completion Toast Alert</span>
                <p className="text-[11px] leading-relaxed">Display desktop alerts immediately upon completion of timeline runs.</p>
              </div>
              <input
                type="checkbox"
                checked={notificationsEnabled}
                onChange={(e) => setNotificationsEnabled(e.target.checked)}
                className="w-4 h-4 bg-slate-900 border-slate-700 rounded text-blue-500 focus:ring-blue-500/30 cursor-pointer"
              />
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
