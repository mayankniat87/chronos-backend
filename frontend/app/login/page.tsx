'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  Mail,
  Lock,
  ArrowRight,
  Sparkles,
  Database
} from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { setDemoUser } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDemoLogin = () => {
    setLoading(true);
    setTimeout(() => {
      setDemoUser();
      router.push('/dashboard');
    }, 800);
  };

  const handleStandardSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please provide email and password credentials.');
      return;
    }
    setError('');
    setLoading(true);
    // Simulate real auth validation with mock response
    setTimeout(() => {
      setDemoUser(); // Log in as demo user
      router.push('/dashboard');
    }, 1200);
  };

  return (
    <div className="relative min-h-screen bg-[#05070B] overflow-hidden flex items-center justify-center font-sans p-4">
      {/* Background radial effects */}
      <div className="absolute top-[20%] left-[20%] w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[20%] right-[20%] w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Main login card container */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        className="w-full max-w-md relative z-10"
      >
        <div className="text-center mb-8">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 shadow-lg shadow-blue-500/20 mb-4">
            <TrendingUp className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold font-outfit text-white mb-2 tracking-tight">Project Chronos</h1>
          <p className="text-slate-400 text-xs leading-relaxed max-w-xs mx-auto">
            Access the restaurant explainable decision intelligence console.
          </p>
        </div>

        {/* Form container */}
        <div className="glass-card p-8 rounded-2xl border border-white/5 shadow-2xl relative">
          
          {/* Subtle glowing bar on top */}
          <div className="absolute top-0 left-10 right-10 h-[2px] bg-gradient-to-r from-blue-500 via-cyan-400 to-purple-500" />

          {error && (
            <div className="mb-4 p-3 rounded-lg border border-red-500/20 bg-red-500/10 text-red-400 text-xs">
              {error}
            </div>
          )}

          <form onSubmit={handleStandardSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Email Address</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <Mail className="h-4.5 w-4.5" />
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@restaurant.com"
                  className="w-full pl-11 pr-4 py-3 rounded-xl text-sm glass-input text-slate-200"
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Secure Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <Lock className="h-4.5 w-4.5" />
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-11 pr-4 py-3 rounded-xl text-sm glass-input text-slate-200"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center gap-2 cursor-pointer text-slate-400 hover:text-slate-300">
                <input type="checkbox" className="rounded bg-slate-900 border-slate-700 text-blue-500 focus:ring-blue-500/30" />
                <span>Remember me</span>
              </label>
              <button type="button" className="text-blue-400 hover:underline">Forgot password?</button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-all shadow-lg shadow-blue-500/10 flex items-center justify-center gap-2 cursor-pointer"
            >
              {loading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="h-4.5 w-4.5" />
                </>
              )}
            </button>
          </form>

          {/* Spacer */}
          <div className="relative my-6 text-center">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-800" /></div>
            <span className="relative z-10 px-3 bg-[#0d1423] text-slate-500 text-[10px] uppercase font-bold tracking-widest">or evaluation bypass</span>
          </div>

          {/* Quick Demo Bypass */}
          <button
            onClick={handleDemoLogin}
            disabled={loading}
            className="w-full py-3.5 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-800 text-slate-300 hover:text-white font-semibold text-sm transition-all flex items-center justify-center gap-2.5 cursor-pointer group"
          >
            <Sparkles className="h-4.5 w-4.5 text-yellow-500 animate-pulse group-hover:scale-110 transition-transform" />
            <span>Launch Sandbox Demo</span>
          </button>
        </div>

        <div className="mt-8 text-center text-slate-500 text-xs">
          <p className="flex items-center justify-center gap-1.5">
            <Database className="h-3.5 w-3.5 text-slate-600" />
            <span>FastAPI service detection: auto-configured.</span>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
