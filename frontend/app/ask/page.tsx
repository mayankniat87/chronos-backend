'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { useRestaurantStore } from '@/store/restaurantStore';
import { useSimulationStore } from '@/store/simulationStore';
import { simulationService } from '@/services/simulation';
import { SimulationRequest } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  ChevronDown,
  Info,
  Settings2,
  BrainCircuit,
  MessageSquareCode
} from 'lucide-react';

const loaderMessages = [
  'Parsing decision parameters...',
  'Loading restaurant operational graph...',
  'Querying supplier and inventory node connections...',
  'Calculating price elasticity vectors...',
  'Mapping staff utilization limits...',
  'Projecting 3D confidence scores...',
  'Formatting optimistic, likely, and pessimistic scenarios...',
];

export default function AskPage() {
  const router = useRouter();
  const { selectedRestaurant } = useRestaurantStore();
  const { setCurrentSimulation, setIsSimulating } = useSimulationStore();

  const [question, setQuestion] = useState('');
  const [decisionType, setDecisionType] = useState<SimulationRequest['decisionType']>('pricing');
  const [factorChange, setFactorChange] = useState<number>(10); // Default +10% price
  const [horizonMonths, setHorizonMonths] = useState<number>(3); // Default 3 months
  const [description, setDescription] = useState('');

  const [loaderMessage, setLoaderMessage] = useState('Parsing decision parameters...');
  const loaderIndexRef = useRef(0);

  // React Query simulation mutation
  const simulateMutation = useMutation({
    mutationFn: (request: SimulationRequest) => simulationService.simulateDecision(request),
    onSuccess: (data) => {
      setCurrentSimulation(data);
      setIsSimulating(false);
      router.push(`/timelines/${data.id}`);
    },
    onError: () => {
      setIsSimulating(false);
    }
  });

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (simulateMutation.isPending) {
      interval = setInterval(() => {
        loaderIndexRef.current = (loaderIndexRef.current + 1) % loaderMessages.length;
        setLoaderMessage(loaderMessages[loaderIndexRef.current]);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [simulateMutation.isPending]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question || !selectedRestaurant) return;

    setIsSimulating(true);
    simulateMutation.mutate({
      restaurantId: selectedRestaurant.id,
      decisionType,
      parameters: {
        title: question,
        description: description || `Auto-generated simulation run targeting ${decisionType} adjustments.`,
        factorChange,
      },
      horizonMonths,
    });
  };

  const handleQuickTemplate = (q: string, type: SimulationRequest['decisionType'], change: number, desc: string) => {
    setQuestion(q);
    setDecisionType(type);
    setFactorChange(change);
    setDescription(desc);
  };

  return (
    <div className="space-y-8 font-sans max-w-5xl mx-auto">
      
      {/* Top Banner Header */}
      <div>
        <h1 className="text-3xl font-extrabold font-outfit text-foreground tracking-tight flex items-center gap-2">
          Simulation Laboratory
        </h1>
        <p className="text-muted text-xs mt-1">
          Draft a business question or select a template to project operational paths before committing capital.
        </p>
      </div>

      <AnimatePresence mode="wait">
        {simulateMutation.isPending ? (
          /* High quality simulated loading state */
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className="glass-card p-12 rounded-2xl flex flex-col items-center justify-center min-h-[450px] text-center space-y-6 relative overflow-hidden"
          >
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-[80px] animate-pulse" />
            </div>
            
            <div className="relative">
              <div className="h-16 w-16 animate-spin rounded-full border-4 border-blue-500 border-t-transparent flex items-center justify-center" />
              <BrainCircuit className="h-6 w-6 text-cyan-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
            </div>

            <div className="space-y-2 relative z-10 max-w-md">
              <h3 className="text-lg font-bold font-outfit text-foreground">Chronos Business Time Machine Running</h3>
              <p className="text-xs text-blue-400 font-mono tracking-wide h-6">{loaderMessage}</p>
              <p className="text-[11px] text-faint mt-4 leading-relaxed">
                We are evaluating transaction logs and adjusting supplier delivery vectors. This takes just a moment.
              </p>
            </div>
          </motion.div>
        ) : (
          /* Console Configuration Form */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start"
          >
            {/* Primary Settings Form */}
            <form onSubmit={handleSubmit} className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-6">
              
              {/* Question text box */}
              <div>
                <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2.5">
                  Business Question Prompt
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-faint">
                    <MessageSquareCode className="h-5 w-5" />
                  </span>
                  <input
                    type="text"
                    required
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g. Raise menu prices on premium burgers and domestic beers by 12%?"
                    className="w-full pl-11 pr-4 py-3.5 rounded-xl text-sm glass-input text-strong"
                  />
                </div>
              </div>

              {/* Form Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                
                {/* Decision Type */}
                <div>
                  <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2.5">
                    Decision Category
                  </label>
                  <div className="relative">
                    <select
                      value={decisionType}
                      onChange={(e) => setDecisionType(e.target.value as SimulationRequest['decisionType'])}
                      className="w-full px-4 py-3 rounded-xl text-sm glass-input text-strong appearance-none cursor-pointer"
                    >
                      <option value="pricing">Pricing Adjustments</option>
                      <option value="staffing">Staff Shift Scheduling</option>
                      <option value="inventory">Inventory buffer safety</option>
                      <option value="marketing">Marketing promotions spend</option>
                      <option value="expansion">Facility seat expansions</option>
                      <option value="general">General Operations</option>
                    </select>
                    <ChevronDown className="h-4.5 w-4.5 text-faint absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                  </div>
                </div>

                {/* Horizon Months */}
                <div>
                  <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2.5">
                    Simulation Horizon
                  </label>
                  <div className="relative">
                    <select
                      value={horizonMonths}
                      onChange={(e) => setHorizonMonths(Number(e.target.value))}
                      className="w-full px-4 py-3 rounded-xl text-sm glass-input text-strong appearance-none cursor-pointer"
                    >
                      <option value="1">1 Month Outlook</option>
                      <option value="3">3 Months Standard Outlook</option>
                      <option value="6">6 Months Long-range</option>
                      <option value="12">12 Months Macro Outlook</option>
                    </select>
                    <ChevronDown className="h-4.5 w-4.5 text-faint absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                  </div>
                </div>

                {/* Factor Change (Multiplier Delta) */}
                <div>
                  <label className="flex justify-between text-xs font-semibold text-muted uppercase tracking-wider mb-2.5">
                    <span>Adjustment Factor</span>
                    <span className="text-blue-400 font-bold">{factorChange > 0 ? `+${factorChange}` : factorChange}%</span>
                  </label>
                  <input
                    type="range"
                    min="-50"
                    max="50"
                    step="5"
                    value={factorChange}
                    onChange={(e) => setFactorChange(Number(e.target.value))}
                    className="w-full h-1.5 bg-surface-deep rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />
                  <div className="flex justify-between text-[10px] text-faint mt-1 font-mono">
                    <span>-50% Cut</span>
                    <span>No Shift</span>
                    <span>+50% Growth</span>
                  </div>
                </div>

                {/* Description details */}
                <div>
                  <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2.5">
                    Context / Assumptions
                  </label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe external changes, e.g. local supplier warning"
                    className="w-full px-4 py-3 rounded-xl text-sm glass-input text-strong"
                  />
                </div>

              </div>

              {/* Action Submit */}
              <button
                type="submit"
                className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs shadow-md shadow-blue-500/10 cursor-pointer flex items-center justify-center gap-2 group"
              >
                <Sparkles className="h-4 w-4 text-yellow-300 animate-pulse group-hover:scale-110 transition-transform" />
                <span>Simulate Future Scenarios</span>
              </button>
            </form>

            {/* Templates Sidebar */}
            <div className="space-y-5">
              <div className="glass-card p-6 rounded-2xl">
                <div className="flex items-center gap-2 border-b border-edge/80 pb-4 mb-4">
                  <Settings2 className="h-4.5 w-4.5 text-muted" />
                  <h3 className="text-sm font-bold font-outfit text-foreground uppercase tracking-wider">Quick Templates</h3>
                </div>

                <div className="space-y-3">
                  {[
                    {
                      label: 'Menu Price Adjustment',
                      q: 'Raise wine menu pricing by 12% during dinner service.',
                      type: 'pricing' as const,
                      val: 12,
                      desc: 'Weekday wine menu optimization.'
                    },
                    {
                      label: 'Staff Shifts Reduction',
                      q: 'Reduce prep staff shifts by 15% on quiet Tuesdays.',
                      type: 'staffing' as const,
                      val: -15,
                      desc: 'Labor expense controls for off-peak days.'
                    },
                    {
                      label: 'Seafood Safety Buffer',
                      q: 'Increase salmon and cod inventory buffers by 20%.',
                      type: 'inventory' as const,
                      val: 20,
                      desc: 'Mitigate local supply channel volatility warnings.'
                    },
                  ].map((tpl, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleQuickTemplate(tpl.q, tpl.type, tpl.val, tpl.desc)}
                      className="w-full text-left p-3.5 rounded-xl border border-edge/80 bg-surface/10 hover:border-edge-strong hover:bg-surface/40 transition-all text-xs space-y-1.5"
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-strong">{tpl.label}</span>
                        <span className="text-[10px] text-blue-400 font-semibold">{tpl.val > 0 ? `+${tpl.val}` : tpl.val}%</span>
                      </div>
                      <p className="text-muted leading-normal truncate">{tpl.q}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Explanatory Info Card */}
              <div className="p-5 rounded-2xl border border-edge bg-surface/20 text-xs text-muted leading-normal flex gap-3">
                <Info className="h-4.5 w-4.5 text-blue-400 flex-shrink-0 mt-0.5" />
                <p>
                  Chronos simulations map adjustments across key supply lines. Results detail Optimistic, Likely, and Pessimistic timelines including risk projections.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
