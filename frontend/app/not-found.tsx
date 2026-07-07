'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="relative min-h-screen bg-[#05070B] overflow-hidden flex flex-col items-center justify-center font-sans text-center p-4">
      {/* Background gradients */}
      <div className="absolute top-[30%] left-[30%] w-[350px] h-[350px] bg-red-500/5 rounded-full blur-[80px] pointer-events-none" />
      
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        className="space-y-6 relative z-10 max-w-md"
      >
        <div className="inline-flex h-14 w-14 items-center justify-center rounded-xl bg-red-500/10 text-red-400 border border-red-500/15 mb-2">
          <ShieldAlert className="h-7 w-7" />
        </div>
        
        <div className="space-y-2">
          <h1 className="text-4xl font-extrabold font-outfit text-white tracking-tight">404 - Node Out of Bounds</h1>
          <p className="text-slate-400 text-xs leading-relaxed">
            The timeline index or dashboard route you are attempting to trace is unmapped in this branch.
          </p>
        </div>

        <Link href="/dashboard">
          <button className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold transition-all cursor-pointer">
            <ArrowLeft className="h-4 w-4" />
            <span>Return to Operations Console</span>
          </button>
        </Link>
      </motion.div>
    </div>
  );
}
