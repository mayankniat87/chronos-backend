'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  Brain,
  Network,
  Cpu,
  History,
  Play
} from 'lucide-react';

export default function LandingPage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { type: 'spring' as const, stiffness: 100, damping: 15 },
    },
  };

  const features = [
    {
      title: 'Business Knowledge Graph',
      desc: 'Map multi-dimensional networks of menu pricing, supplier delays, items, customer retention, and operations.',
      icon: Network,
      color: 'text-blue-400',
      border: 'hover:border-blue-500/30'
    },
    {
      title: 'Future Simulation Engine',
      desc: 'Simulate business shifts in pricing, staffing structure, and supply logs over 1 to 12 month horizons.',
      icon: Cpu,
      color: 'text-purple-400',
      border: 'hover:border-purple-500/30'
    },
    {
      title: 'Explainable AI Projections',
      desc: 'Access structured evidence lists, background assumptions, and structural boundaries behind every forecast.',
      icon: Brain,
      color: 'text-cyan-400',
      border: 'hover:border-cyan-500/30'
    },
    {
      title: 'Decision History Logs',
      desc: 'Trace historic simulations and compare model assumptions with real margins to improve predictive accuracy.',
      icon: History,
      color: 'text-emerald-400',
      border: 'hover:border-emerald-500/30'
    },
  ];

  return (
    <div className="relative min-h-screen bg-background overflow-hidden flex flex-col font-sans">
      
      {/* Dynamic Background Light Pools */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-[40%] left-[50%] -translate-x-1/2 w-[400px] h-[400px] bg-cyan-500/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Landing Header */}
      <header className="sticky top-0 z-50 w-full glass-panel border-b border-white/5 py-4 px-6 md:px-12 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-500 shadow-lg shadow-blue-500/20">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-wider font-outfit text-foreground">CHRONOS</span>
        </div>

        <div>
          <Link href="/login">
            <span className="text-sm font-semibold hover:text-blue-400 transition-colors cursor-pointer mr-6 text-muted">
              Sign In
            </span>
          </Link>
          <Link href="/login">
            <button className="px-4 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors shadow-md shadow-blue-500/15 cursor-pointer text-white">
              Launch Console
            </button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 max-w-6xl mx-auto w-full px-6 py-16 md:py-24 flex flex-col items-center justify-center text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="mb-4 inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-blue-500/20 bg-blue-500/5 text-blue-400 text-xs font-medium tracking-wide"
        >
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>Explainable Decision Intelligence for SME Restaurants</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight font-outfit text-foreground max-w-4xl leading-[1.1] mb-6"
        >
          See the Future Before You Make{' '}
          <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent glow-text-blue">
            Business Decisions
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-muted text-base sm:text-xl max-w-2xl leading-relaxed mb-10"
        >
          Chronos maps your operational data into a self-healing knowledge graph, running real-time simulations to project changes in revenue, supply, and staff.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <Link href="/login">
            <button className="group flex items-center gap-2 px-8 py-3.5 text-sm font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-lg shadow-blue-500/10 cursor-pointer">
              <span>Start Simulation</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </Link>
          <Link href="/login">
            <button className="flex items-center gap-2 px-8 py-3.5 text-sm font-semibold rounded-xl border border-edge bg-surface/50 hover:bg-surface-2 text-strong hover:text-foreground transition-all cursor-pointer">
              <Play className="h-4 w-4" />
              <span>Watch Demo</span>
            </button>
          </Link>
        </motion.div>
      </section>

      {/* Features Showcase */}
      <section className="border-t border-edge bg-surface-deep/30 py-24 px-6 md:px-12 relative z-10">
        <div className="max-w-6xl mx-auto w-full">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold font-outfit text-foreground mb-4">Chronos Feature Architecture</h2>
            <p className="text-muted text-sm max-w-lg mx-auto">Enterprise-grade modules designed to replace predictive uncertainty with explainable data models.</p>
          </div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={idx}
                  variants={itemVariants}
                  className={`glass-card p-6 rounded-2xl flex gap-5 border border-white/5 ${feature.border}`}
                >
                  <div className="flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-xl bg-surface/80 border border-edge">
                    <Icon className={`h-6 w-6 ${feature.color}`} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold font-outfit text-strong mb-2">{feature.title}</h3>
                    <p className="text-muted text-sm leading-relaxed">{feature.desc}</p>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6 md:px-12 relative z-10 bg-background">
        <div className="max-w-6xl mx-auto w-full">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold font-outfit text-foreground mb-4 font-semibold">How It Works</h2>
            <p className="text-muted text-sm max-w-lg mx-auto">Four simple steps to forecast operations with explainable confidence.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 relative">
            {/* Connection Line */}
            <div className="hidden lg:block absolute top-1/2 left-4 right-4 h-0.5 bg-gradient-to-r from-blue-500/20 via-cyan-500/20 to-purple-500/20 -translate-y-1/2 z-0" />

            {[
              { num: '01', title: 'Upload Data', desc: 'Drop CSV/Excel inventory and sales records into our encrypted staging zones.' },
              { num: '02', title: 'Ask Question', desc: 'Ask Chronos to evaluate pricing shifts, supply limits, or schedule hours.' },
              { num: '03', title: 'See Future', desc: 'Analyze three timeline variants detailing margins, stock levels, and staff ratios.' },
              { num: '04', title: 'Take Action', desc: 'Lock in simulated actions with confidence and track outcome metrics.' },
            ].map((step, idx) => (
              <div key={idx} className="relative z-10 glass-card p-6 rounded-xl text-left border border-white/5 bg-surface-deep/20 flex flex-col justify-between h-48">
                <span className="text-2xl font-black font-outfit bg-gradient-to-r from-blue-500 to-cyan-400 bg-clip-text text-transparent">{step.num}</span>
                <div>
                  <h4 className="font-bold text-strong mb-1.5 text-base">{step.title}</h4>
                  <p className="text-muted text-xs leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-edge/60 py-8 px-6 text-center text-faint text-xs">
        <p>© {new Date().getFullYear()} Project Chronos. All rights reserved. Built for restaurant decision operations.</p>
      </footer>
    </div>
  );
}
