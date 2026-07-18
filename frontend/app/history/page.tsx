'use client';

import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRestaurantStore } from '@/store/restaurantStore';
import { historyService } from '@/services/history';
import { DecisionHistory } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Calendar,
  ChevronRight,
  FileCheck,
  X,
  ShieldAlert,
  ClipboardList
} from 'lucide-react';

export default function HistoryPage() {
  const { selectedRestaurant } = useRestaurantStore();
  const restaurantId = selectedRestaurant?.id || 'rest_01';

  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [selectedItem, setSelectedItem] = useState<DecisionHistory | null>(null);

  // React Query fetching decision history ledger
  const { data: history, isLoading } = useQuery({
    queryKey: ['restaurant-history', restaurantId],
    queryFn: () => historyService.getDecisionHistory(restaurantId),
    enabled: !!restaurantId,
  });

  const categories = ['all', 'pricing', 'staffing', 'inventory', 'marketing'];

  const filteredHistory = useMemo(() => {
    if (!history) return [];
    return history.filter((item) => {
      const matchesSearch = item.question.toLowerCase().includes(search.toLowerCase()) || item.simulatedImpact.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = activeCategory === 'all' || item.decisionType === activeCategory;
      return matchesSearch && matchesCategory;
    });
  }, [history, search, activeCategory]);

  return (
    <div className="space-y-8 font-sans">
      
      {/* Top Banner Header */}
      <div>
        <h1 className="text-3xl font-extrabold font-outfit text-foreground tracking-tight">Decision Audit Ledger</h1>
        <p className="text-muted text-xs mt-1">
          Historical log of simulated questions and retrospective actual outcomes for <span className="text-blue-400 font-semibold">{selectedRestaurant?.name}</span>.
        </p>
      </div>

      {/* Filter toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-surface-deep/40 p-4 rounded-2xl border border-edge/80">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-faint">
              <Search className="h-4 w-4" />
            </span>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search audit trail..."
              className="pl-9 pr-4 py-2 w-56 text-xs rounded-xl glass-input text-strong"
            />
          </div>

          <div className="flex gap-1.5">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3 py-1.5 rounded-lg border text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer ${
                  activeCategory === cat
                    ? 'bg-surface-2 border-edge-strong text-strong'
                    : 'border-transparent text-faint hover:text-muted'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main timeline listing */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass-card p-6 rounded-2xl animate-pulse h-24" />
            ))}
          </div>
        ) : filteredHistory.length > 0 ? (
          filteredHistory.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => setSelectedItem(item)}
              className="glass-card p-5 rounded-2xl border border-white/5 hover:border-edge-strong hover:bg-surface/10 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer group"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                    item.decisionType === 'pricing' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/10' :
                    item.decisionType === 'staffing' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/10' :
                    'bg-purple-500/10 text-purple-400 border border-purple-500/10'
                  }`}>
                    {item.decisionType}
                  </span>
                  <span className="text-[10px] text-faint flex items-center gap-1 font-mono">
                    <Calendar className="h-3.5 w-3.5" />
                    {new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-strong leading-snug">{item.question}</h3>
                <p className="text-xs text-muted leading-normal">{item.simulatedImpact}</p>
              </div>

              <div className="flex items-center gap-4 flex-shrink-0">
                {item.status === 'implemented' ? (
                  <span className="px-2.5 py-1 text-[10px] font-bold uppercase rounded-lg border border-emerald-500/20 bg-emerald-500/10 text-emerald-400 flex items-center gap-1">
                    <FileCheck className="h-3.5 w-3.5" /> Implemented
                  </span>
                ) : (
                  <span className="px-2.5 py-1 text-[10px] font-bold uppercase rounded-lg border border-edge bg-surface/60 text-faint flex items-center gap-1">
                    <ClipboardList className="h-3.5 w-3.5" /> Simulation Run
                  </span>
                )}
                <ChevronRight className="h-5 w-5 text-faint group-hover:text-muted transition-colors group-hover:translate-x-1 duration-200" />
              </div>
            </motion.div>
          ))
        ) : (
          <div className="text-center p-12 glass-card rounded-2xl">
            <p className="text-sm text-faint">No decisions simulated matching these filters.</p>
          </div>
        )}
      </div>

      {/* Modal Inspector Detail Drawer */}
      <AnimatePresence>
        {selectedItem && (
          <>
            <div className="fixed inset-0 z-50 bg-background/70 backdrop-blur-sm" onClick={() => setSelectedItem(null)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="fixed inset-y-12 right-12 w-[550px] max-w-full glass-panel border border-edge bg-surface-deep/95 p-6 rounded-2xl z-55 flex flex-col justify-between shadow-2xl font-sans"
            >
              <div className="space-y-6 overflow-y-auto pr-1">
                {/* Header title */}
                <div className="flex justify-between items-start border-b border-edge/80 pb-4">
                  <div className="space-y-1">
                    <span className="text-[10px] text-faint font-bold uppercase tracking-widest">ledger audit #{selectedItem.id}</span>
                    <h2 className="text-lg font-bold font-outfit text-foreground leading-tight">{selectedItem.question}</h2>
                  </div>
                  <button
                    onClick={() => setSelectedItem(null)}
                    className="p-1 rounded hover:bg-surface-2 text-faint hover:text-foreground transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3.5 rounded-xl border border-edge bg-surface/30">
                    <span className="text-[10px] text-faint font-bold uppercase tracking-wider block">Decision Type</span>
                    <span className="text-sm font-semibold text-strong capitalize">{selectedItem.decisionType}</span>
                  </div>
                  <div className="p-3.5 rounded-xl border border-edge bg-surface/30">
                    <span className="text-[10px] text-faint font-bold uppercase tracking-wider block">Chosen Timeline</span>
                    <span className="text-sm font-semibold text-blue-400">{selectedItem.scenarioChosen} Scenario</span>
                  </div>
                </div>

                {/* Simulated detail section */}
                <div className="space-y-2">
                  <h4 className="text-[10px] font-bold text-faint uppercase tracking-widest">Simulated Projection</h4>
                  <p className="p-3 rounded-lg border border-edge bg-surface-deep/60 text-xs leading-relaxed text-strong">
                    {selectedItem.simulatedImpact}
                  </p>
                </div>

                {/* Actual Outcomes log */}
                <div className="space-y-2">
                  <h4 className="text-[10px] font-bold text-faint uppercase tracking-widest">Retrospective Actual Outcomes</h4>
                  <p className="p-3 rounded-lg border border-blue-500/10 bg-blue-500/5 text-xs leading-relaxed text-blue-300">
                    {selectedItem.outcomeMetric}
                  </p>
                </div>

                {/* Audit notes detail text */}
                <div className="space-y-2">
                  <h4 className="text-[10px] font-bold text-faint uppercase tracking-widest">Operations Log Details</h4>
                  <p className="text-xs leading-relaxed text-muted">
                    {selectedItem.details}
                  </p>
                </div>
              </div>

              {/* Drawer footer details */}
              <div className="pt-6 border-t border-edge mt-6 text-[10px] text-faint font-semibold flex items-center justify-between">
                <span className="flex items-center gap-1"><ShieldAlert className="h-3.5 w-3.5" /> Ledger audit records are cryptographically stored.</span>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
