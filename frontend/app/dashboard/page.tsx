'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRestaurantStore } from '@/store/restaurantStore';
import { healthService } from '@/services/health';
import { historyService } from '@/services/history';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  TrendingUp,
  ShoppingBag,
  PackageOpen,
  Users2,
  Percent,
  Play,
  Upload,
  Network,
  History,
  ShieldCheck,
  Calendar,
  AlertCircle
} from 'lucide-react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

export default function DashboardPage() {
  const { selectedRestaurant } = useRestaurantStore();
  const restaurantId = selectedRestaurant?.id || 'rest_01';

  // React Query fetching restaurant health metrics
  const { data: health, isLoading: healthLoading, isError: healthError } = useQuery({
    queryKey: ['restaurant-health', restaurantId],
    queryFn: () => healthService.getRestaurantHealth(restaurantId),
    enabled: !!restaurantId,
  });

  // React Query fetching decision history
  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['restaurant-history', restaurantId],
    queryFn: () => historyService.getDecisionHistory(restaurantId),
    enabled: !!restaurantId,
  });

  if (healthLoading) {
    return (
      <div className="space-y-6">
        {/* Skeleton grid */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="glass-card p-6 rounded-2xl animate-pulse h-28" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-6 rounded-2xl animate-pulse h-96" />
          <div className="glass-card p-6 rounded-2xl animate-pulse h-96" />
        </div>
      </div>
    );
  }

  if (healthError || !health) {
    return (
      <div className="p-6 text-center glass-card rounded-2xl border border-red-500/10 bg-red-500/5 max-w-lg mx-auto">
        <AlertCircle className="h-10 w-10 text-red-400 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-foreground mb-1">Failed to connect to Chronos backend</h3>
        <p className="text-muted text-xs mb-4">
          Please check the backend server health or toggle on Sandbox Demo mode in Settings.
        </p>
        <Link href="/settings">
          <button className="px-4 py-2 text-xs font-semibold rounded-lg bg-surface-2 hover:bg-surface-3 text-strong">
            Open Settings
          </button>
        </Link>
      </div>
    );
  }

  // Format charts telemetry
  const chartData = health.revenueTrend.map((rev, index) => ({
    name: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index] || `Day ${index}`,
    Revenue: rev,
    Orders: health.orderTrend[index] * 40, // Scaled for plotting
  }));

  const cardData = [
    {
      title: 'Estimated Revenue',
      value: `$${health.metrics.monthlyRevenue.toLocaleString()}`,
      change: '+14.2%',
      desc: 'vs last month',
      icon: TrendingUp,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10'
    },
    {
      title: 'Total Volume',
      value: health.metrics.monthlyOrders.toString(),
      change: '+8.6%',
      desc: 'processed tickets',
      icon: ShoppingBag,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10'
    },
    {
      title: 'Inventory Status',
      value: `${health.inventoryTrend[health.inventoryTrend.length - 1]}%`,
      change: `-${health.metrics.inventoryShortages} items`,
      desc: 'below safety limit',
      icon: PackageOpen,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10'
    },
    {
      title: 'Staff Load',
      value: `${health.staffTrend[health.staffTrend.length - 1]}%`,
      change: 'Optimal',
      desc: 'shift utilization',
      icon: Users2,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10'
    },
    {
      title: 'Simulation Score',
      value: `${health.score}%`,
      change: 'High confidence',
      desc: 'accuracy index',
      icon: Percent,
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/10'
    },
  ];

  return (
    <div className="space-y-8 font-sans">
      
      {/* Upper overview header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold font-outfit text-foreground tracking-tight flex items-center gap-2.5">
            Operations Panel
          </h1>
          <p className="text-muted text-xs mt-1">
            Real-time explainable intelligence for <span className="text-blue-400 font-semibold">{selectedRestaurant?.name}</span>.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted bg-surface/60 border border-edge px-3 py-1.5 rounded-lg">
          <Calendar className="h-3.5 w-3.5" />
          <span>Last Synchronized: Just Now</span>
        </div>
      </div>

      {/* KPI Cards row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        {cardData.map((card, idx) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              className="glass-card p-5 rounded-2xl flex flex-col justify-between"
            >
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold text-muted uppercase tracking-wider">{card.title}</span>
                <div className={`p-2 rounded-xl ${card.bg} border border-white/5`}>
                  <Icon className={`h-4.5 w-4.5 ${card.color}`} />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-2xl font-bold font-outfit text-foreground tracking-tight">{card.value}</span>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className={`text-[10px] font-bold ${card.change.startsWith('-') ? 'text-red-400' : 'text-emerald-400'}`}>
                    {card.change}
                  </span>
                  <span className="text-[10px] text-faint">{card.desc}</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Charts & Actions Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Area Chart */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-base font-bold font-outfit text-foreground">Revenue & Orders Weekly Telemetry</h3>
              <p className="text-[11px] text-faint">Comparing active register deposits against order processing metrics</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-blue-400">
                <span className="w-2 h-2 rounded-full bg-blue-500" /> Revenue
              </span>
              <span className="flex items-center gap-1.5 text-cyan-400">
                <span className="w-2 h-2 rounded-full bg-cyan-400" /> Orders
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorOrd" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--edge)" strokeOpacity={0.35} vertical={false} />
                <XAxis dataKey="name" stroke="var(--faint)" fontSize={11} tickLine={false} />
                <YAxis stroke="var(--faint)" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: 'var(--surface)',
                    border: '1px solid var(--edge)',
                    borderRadius: '12px',
                    fontSize: '11px'
                  }}
                  itemStyle={{ color: 'var(--foreground)' }}
                />
                <Area type="monotone" dataKey="Revenue" stroke="#3B82F6" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRev)" />
                <Area type="monotone" dataKey="Orders" stroke="#06B6D4" strokeWidth={2.5} fillOpacity={1} fill="url(#colorOrd)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Actions and Widgets */}
        <div className="flex flex-col gap-6">
          <div className="glass-card p-6 rounded-2xl flex-1 flex flex-col justify-between">
            <div>
              <h3 className="text-base font-bold font-outfit text-foreground mb-2">Simulate Decision</h3>
              <p className="text-xs text-muted leading-relaxed mb-6">
                Project price increases, shift scheduler cuts, or supply logistics delays before committing them.
              </p>
            </div>
            
            <div className="grid grid-cols-2 gap-3.5">
              <Link href="/ask" className="col-span-2">
                <button className="w-full py-3 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-500/10 flex items-center justify-center gap-2 cursor-pointer">
                  <Play className="h-3.5 w-3.5 fill-white" />
                  <span>Start New Run</span>
                </button>
              </Link>
              
              <Link href="/upload">
                <button className="w-full py-2.5 rounded-xl border border-edge bg-surface-deep/40 hover:bg-surface-2 text-strong hover:text-strong text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer">
                  <Upload className="h-3.5 w-3.5" />
                  <span>Ingest Files</span>
                </button>
              </Link>

              <Link href="/graph">
                <button className="w-full py-2.5 rounded-xl border border-edge bg-surface-deep/40 hover:bg-surface-2 text-strong hover:text-strong text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer">
                  <Network className="h-3.5 w-3.5" />
                  <span>Inspect Graph</span>
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Decision Feed segment */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Recent Decisions Feed */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-base font-bold font-outfit text-foreground">Recent Decisions Feed</h3>
              <p className="text-[11px] text-faint">Outcome evaluations from implemented decision models</p>
            </div>
            <Link href="/history">
              <span className="text-xs text-blue-400 hover:underline cursor-pointer flex items-center gap-1">
                <span>View Full Audit</span>
                <History className="h-3 w-3" />
              </span>
            </Link>
          </div>

          <div className="space-y-4">
            {historyLoading ? (
              <p className="text-xs text-faint">Loading history feed...</p>
            ) : history && history.length > 0 ? (
              history.slice(0, 3).map((item) => (
                <div key={item.id} className="p-4 rounded-xl bg-surface-deep/40 border border-edge/80 hover:border-edge-strong transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        item.decisionType === 'pricing' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/10' :
                        item.decisionType === 'staffing' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/10' :
                        'bg-purple-500/10 text-purple-400 border border-purple-500/10'
                      }`}>
                        {item.decisionType}
                      </span>
                      <span className="text-[10px] text-faint">
                        {new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-strong">{item.question}</p>
                    <p className="text-xs text-muted leading-normal">{item.simulatedImpact}</p>
                  </div>
                  
                  {item.status === 'implemented' && (
                    <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/5 px-2.5 py-1.5 rounded-lg border border-emerald-500/10 flex-shrink-0 self-start md:self-auto">
                      <ShieldCheck className="h-4 w-4" />
                      <span>Live Metrics Logged</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-xs text-faint">No decisions simulated yet.</p>
            )}
          </div>
        </div>

        {/* Right Side: Quick Health telemetry metrics */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold font-outfit text-foreground mb-1">Operational Diagnostics</h3>
            <p className="text-[11px] text-faint mb-6">Comparing performance indicators against baseline targets</p>
            
            <div className="space-y-5">
              {[
                { label: 'Weekly Revenue Growth', pct: 94, val: 'Optimal' },
                { label: 'Inventory Level Health', pct: health.inventoryTrend[health.inventoryTrend.length - 1], val: `${health.inventoryTrend[health.inventoryTrend.length - 1]}%` },
                { label: 'Staff Shift Fill Rate', pct: health.staffTrend[health.staffTrend.length - 1], val: `${health.staffTrend[health.staffTrend.length - 1]}%` },
                { label: 'Order Processing Speed', pct: 86, val: `${health.metrics.averageOrderTimeMin} min` },
              ].map((metric, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-muted">{metric.label}</span>
                    <span className="text-strong">{metric.val}</span>
                  </div>
                  <div className="h-1.5 w-full bg-surface-deep rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${
                        metric.pct > 85 ? 'from-blue-500 to-cyan-400' :
                        metric.pct > 70 ? 'from-yellow-500 to-amber-400' :
                        'from-red-500 to-rose-400'
                      }`}
                      style={{ width: `${metric.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
