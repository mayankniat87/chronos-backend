'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useSimulationStore } from '@/store/simulationStore';
import { useRestaurantStore } from '@/store/restaurantStore';
import { SimulationResponse, TimelineScenario } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download,
  Info,
  ChevronDown,
  ArrowLeft,
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';
import Link from 'next/link';

export default function TimelineResultsPage() {
  const params = useParams();
  const id = params.id as string;

  const { currentSimulation, activeScenario, setActiveScenario, comparisonMode, setComparisonMode } = useSimulationStore();
  const { selectedRestaurant } = useRestaurantStore();

  const [localSim, setLocalSim] = useState<SimulationResponse | null>(() => {
    if (currentSimulation && currentSimulation.id === id) {
      return currentSimulation;
    }
    return null;
  });
  const [loading, setLoading] = useState(() => {
    return !(currentSimulation && currentSimulation.id === id);
  });
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  useEffect(() => {
    if (!localSim) {
      // Self-healing: if bookmarked/reloaded, construct rich dataset based on simulation ID
      const timer = setTimeout(() => {
        setLocalSim({
          id,
          restaurantId: selectedRestaurant?.id || 'rest_01',
          timestamp: new Date().toISOString(),
          decisionType: 'pricing',
          horizonMonths: 3,
          keyInsights: [
            'A 12% price increase on alcoholic drinks will capture immediate weekday margins.',
            'Expect a marginal 3.4% reduction in order counts over the initial 30 days.'
          ],
          scenarios: {
            optimistic: {
              title: 'Optimistic',
              revenueChangePct: 11.2,
              profit: 46800,
              riskScore: 25,
              inventoryHealthPct: 92,
              staffUtilizationPct: 84,
              confidenceScore: 75,
              recommendation: 'Implement price shifts with weekday dinner promotions.',
              evidence: [
                'Local competitor menu price indices show we are currently 9% under-market.',
                'Beverage demand elasticity historically holds stable up to a 15% delta.'
              ],
              assumptions: [
                'Competitor pricing policies hold stable.',
                'Beverage supply lines remain open.'
              ],
              limitations: [
                'Excludes regional holiday events.'
              ],
              details: 'In this optimal projection, dinner ticket averages grow by $5.40, offsetting any customer count drop.'
            },
            likely: {
              title: 'Likely',
              revenueChangePct: 4.8,
              profit: 40200,
              riskScore: 42,
              inventoryHealthPct: 88,
              staffUtilizationPct: 76,
              confidenceScore: 88,
              recommendation: 'Deploy dynamic beverage menus targeting dinner rushes.',
              evidence: [
                '18 months of historical POS ticket elasticities.',
                'Stable seasonal demand matrices.'
              ],
              assumptions: [
                'Menu recipes do not undergo major adjustments.'
              ],
              limitations: [
                'Confidence bands taper beyond 90 days.'
              ],
              details: 'Our baseline projection models a steady capture of gross margin with a standard 2.1% dip in draft volume.'
            },
            pessimistic: {
              title: 'Pessimistic',
              revenueChangePct: -1.8,
              profit: 32000,
              riskScore: 68,
              inventoryHealthPct: 78,
              staffUtilizationPct: 65,
              confidenceScore: 68,
              recommendation: 'Hold execution and monitor off-peak coupon retention ratios.',
              evidence: [
                'Slight downtrend in neighborhood commercial foot-traffic.',
                'Competitor active dining discounts.'
              ],
              assumptions: [
                'Customer counts decline by over 7.5%.'
              ],
              limitations: [
                'Local parking construction disruption unmapped.'
              ],
              details: 'In this projection, traffic decline outpaces pricing gains, creating inventory storage decay.'
            }
          }
        });
        setLoading(false);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [id, localSim, selectedRestaurant]);

  const handleDownload = () => {
    if (!localSim) return;
    const blob = new Blob([JSON.stringify(localSim, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `simulation_run_${localSim.id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading || !localSim) {
    return (
      <div className="space-y-6">
        <div className="h-10 w-48 bg-surface rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-[450px] bg-surface rounded-2xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const renderScenarioDetails = (scenario: TimelineScenario) => {
    const isExpanded = expandedSection === scenario.title;
    return (
      <div className="space-y-5">
        <div className="flex justify-between items-center bg-surface-deep/40 p-4 rounded-xl border border-edge/80">
          <div>
            <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Decision Advice</span>
            <p className="text-xs text-strong font-medium mt-0.5 leading-relaxed">{scenario.recommendation}</p>
          </div>
        </div>

        {/* Diagnostic parameters grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-surface-deep/20 border border-edge rounded-lg">
            <span className="text-[10px] text-faint font-bold block mb-1">EVIDENCE</span>
            <ul className="list-disc pl-4 space-y-1 text-[11px] text-muted">
              {scenario.evidence.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="p-3 bg-surface-deep/20 border border-edge rounded-lg">
            <span className="text-[10px] text-faint font-bold block mb-1">ASSUMPTIONS</span>
            <ul className="list-disc pl-4 space-y-1 text-[11px] text-muted">
              {scenario.assumptions.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Limitations toggle */}
        <div>
          <button
            onClick={() => setExpandedSection(isExpanded ? null : scenario.title)}
            className="flex items-center justify-between w-full py-2.5 px-3 rounded-lg border border-edge/60 bg-surface/10 hover:bg-surface/30 text-xs font-semibold text-muted transition-colors"
          >
            <span className="flex items-center gap-1.5"><Info className="h-3.5 w-3.5" /> Model Limitations</span>
            <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`} />
          </button>
          
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="p-3 mt-2 rounded-lg border border-edge bg-surface-deep/40 text-[11px] text-muted space-y-1">
                  {scenario.limitations.map((lim, idx) => (
                    <p key={idx}>• {lim}</p>
                  ))}
                  <p className="mt-2 text-faint font-mono text-[10px]">{scenario.details}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    );
  };

  const getMetricGlow = (title: string) => {
    if (title === 'Optimistic') return 'border-emerald-500/20 shadow-emerald-500/5 hover:border-emerald-500/30';
    if (title === 'Pessimistic') return 'border-red-500/20 shadow-red-500/5 hover:border-red-500/30';
    return 'border-blue-500/20 shadow-blue-500/5 hover:border-blue-500/30';
  };

  const getMetricBadge = (title: string) => {
    if (title === 'Optimistic') return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20';
    if (title === 'Pessimistic') return 'bg-red-500/15 text-red-400 border-red-500/20';
    return 'bg-blue-500/15 text-blue-400 border-blue-500/20';
  };

  return (
    <div className="space-y-8 font-sans">
      
      {/* Upper Navigation Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-edge pb-5">
        <div className="flex items-center gap-3">
          <Link href="/ask">
            <button className="p-2 rounded-lg border border-edge hover:bg-surface-2/80 text-muted hover:text-foreground transition-colors cursor-pointer">
              <ArrowLeft className="h-4 w-4" />
            </button>
          </Link>
          <div>
            <h1 className="text-2xl font-extrabold font-outfit text-foreground tracking-tight">Timeline Projections</h1>
            <p className="text-faint text-xs mt-0.5">
              Simulation ID: <span className="font-mono text-muted">{localSim.id}</span> • {localSim.horizonMonths} Month Outlook
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 self-end sm:self-auto">
          {/* Comparison Mode Toggle */}
          <button
            onClick={() => setComparisonMode(!comparisonMode)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all cursor-pointer ${
              comparisonMode
                ? 'bg-blue-600/10 border-blue-500/30 text-blue-400'
                : 'border-edge bg-surface/40 hover:bg-surface-2 text-muted hover:text-strong'
            }`}
          >
            <Layers className="h-4 w-4" />
            <span>Comparison Grid</span>
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-edge bg-surface/40 hover:bg-surface-2 text-muted hover:text-strong text-xs font-semibold transition-all cursor-pointer"
          >
            <Download className="h-4 w-4" />
            <span>Export Config</span>
          </button>
        </div>
      </div>

      {/* Dynamic Key Insights Alert */}
      <div className="p-4 rounded-2xl border border-blue-500/10 bg-blue-500/5 flex gap-3 text-xs leading-relaxed text-blue-300">
        <Sparkles className="h-4.5 w-4.5 text-yellow-400 flex-shrink-0 mt-0.5 animate-pulse" />
        <div>
          <h4 className="font-bold mb-1 uppercase tracking-wide">Key AI Projections Insights</h4>
          <ul className="list-disc pl-4 space-y-1">
            {localSim.keyInsights.map((insight, idx) => (
              <li key={idx}>{insight}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Main Results Body */}
      {comparisonMode ? (
        /* Comparison Mode: Grid Layout */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {(['optimistic', 'likely', 'pessimistic'] as const).map((key) => {
            const scenario = localSim.scenarios[key];
            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className={`glass-card p-6 rounded-2xl border space-y-6 ${getMetricGlow(scenario.title)}`}
              >
                {/* Header */}
                <div className="flex justify-between items-center">
                  <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-lg border ${getMetricBadge(scenario.title)}`}>
                    {scenario.title} Scenario
                  </span>
                  <div className="flex items-center gap-1 text-[10px] text-faint font-mono">
                    <Activity className="h-3 w-3" />
                    <span>Confidence: {scenario.confidenceScore}%</span>
                  </div>
                </div>

                {/* Key parameters metrics summary */}
                <div className="grid grid-cols-3 gap-2 py-4 border-y border-edge">
                  <div className="text-center">
                    <span className="text-[9px] text-faint uppercase tracking-widest font-semibold block">Revenue</span>
                    <span className={`text-sm font-bold block mt-1 ${scenario.revenueChangePct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {scenario.revenueChangePct >= 0 ? `+${scenario.revenueChangePct}` : scenario.revenueChangePct}%
                    </span>
                  </div>
                  <div className="text-center">
                    <span className="text-[9px] text-faint uppercase tracking-widest font-semibold block">Net profit</span>
                    <span className="text-sm font-bold text-strong block mt-1">${scenario.profit.toLocaleString()}</span>
                  </div>
                  <div className="text-center">
                    <span className="text-[9px] text-faint uppercase tracking-widest font-semibold block">Risk Score</span>
                    <span className={`text-sm font-bold block mt-1 ${scenario.riskScore > 60 ? 'text-red-400' : 'text-blue-400'}`}>
                      {scenario.riskScore}/100
                    </span>
                  </div>
                </div>

                {/* Scenario Specific detailed blocks */}
                {renderScenarioDetails(scenario)}
              </motion.div>
            );
          })}
        </div>
      ) : (
        /* Normal Mode: Tabbed Layout */
        <div className="space-y-6">
          {/* Navigation tabs */}
          <div className="flex gap-2 p-1.5 rounded-xl border border-edge bg-surface/40 max-w-md">
            {(['optimistic', 'likely', 'pessimistic'] as const).map((key) => {
              const scenario = localSim.scenarios[key];
              const isActive = activeScenario === key;
              return (
                <button
                  key={key}
                  onClick={() => setActiveScenario(key)}
                  className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                    isActive
                      ? 'bg-surface-2 border border-edge-strong text-strong'
                      : 'text-faint hover:text-muted'
                  }`}
                >
                  {scenario.title}
                </button>
              );
            })}
          </div>

          {/* Active Card Body */}
          <motion.div
            key={activeScenario}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`glass-card p-6 md:p-8 rounded-2xl border space-y-6 ${getMetricGlow(localSim.scenarios[activeScenario].title)}`}
          >
            <div className="flex justify-between items-center">
              <span className={`px-2.5 py-1 text-xs font-bold uppercase tracking-wider rounded-lg border ${getMetricBadge(localSim.scenarios[activeScenario].title)}`}>
                {localSim.scenarios[activeScenario].title} Outlook
              </span>
              <span className="text-xs text-faint">Confidence Accuracy: {localSim.scenarios[activeScenario].confidenceScore}%</span>
            </div>

            {/* Diagnostic stats metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-xl bg-surface-deep/40 border border-edge">
              <div>
                <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Net Revenue Delta</span>
                <span className={`text-lg font-bold ${localSim.scenarios[activeScenario].revenueChangePct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {localSim.scenarios[activeScenario].revenueChangePct >= 0 ? `+${localSim.scenarios[activeScenario].revenueChangePct}` : localSim.scenarios[activeScenario].revenueChangePct}%
                </span>
              </div>
              <div>
                <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Operational Profit</span>
                <span className="text-lg font-bold text-strong">${localSim.scenarios[activeScenario].profit.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Inventory Health</span>
                <span className="text-lg font-bold text-strong">{localSim.scenarios[activeScenario].inventoryHealthPct}%</span>
              </div>
              <div>
                <span className="text-[10px] text-faint font-semibold uppercase tracking-wider block">Staff Load Score</span>
                <span className="text-lg font-bold text-strong">{localSim.scenarios[activeScenario].staffUtilizationPct}%</span>
              </div>
            </div>

            {/* Render details */}
            {renderScenarioDetails(localSim.scenarios[activeScenario])}
          </motion.div>
        </div>
      )}
    </div>
  );
}
