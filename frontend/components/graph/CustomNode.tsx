'use client';

import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import {
  Store,
  Truck,
  PackageOpen,
  Utensils,
  Receipt,
  Users2,
  DollarSign
} from 'lucide-react';

export default function CustomNode({ data, selected }: NodeProps) {
  const type = data.type;
  const status = data.status || 'normal';

  const typeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
    restaurant: Store,
    supplier: Truck,
    inventory: PackageOpen,
    menu_item: Utensils,
    orders: Receipt,
    customers: Users2,
    revenue: DollarSign,
  };

  const Icon = typeIcons[type] || Store;

  const getBorderColor = () => {
    if (selected) return 'border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.4)]';
    if (status === 'critical') return 'border-red-500 shadow-[0_0_12px_rgba(239,68,68,0.3)]';
    if (status === 'warning') return 'border-amber-500 shadow-[0_0_12px_rgba(245,158,11,0.3)]';
    return 'border-edge/80 hover:border-edge-strong';
  };

  const getBadgeColor = () => {
    if (type === 'restaurant') return 'bg-blue-500/15 text-blue-400 border-blue-500/20';
    if (type === 'supplier') return 'bg-orange-500/15 text-orange-400 border-orange-500/20';
    if (type === 'inventory') return 'bg-purple-500/15 text-purple-400 border-purple-500/20';
    if (type === 'menu_item') return 'bg-cyan-500/15 text-cyan-400 border-cyan-500/20';
    if (type === 'orders') return 'bg-yellow-500/15 text-yellow-400 border-yellow-500/20';
    if (type === 'customers') return 'bg-teal-500/15 text-teal-400 border-teal-500/20';
    return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20'; // Revenue
  };

  return (
    <div className={`glass-card p-3.5 rounded-xl border flex items-center gap-3 min-w-[170px] ${getBorderColor()}`}>
      
      {/* Node input Handle */}
      <Handle type="target" position={Position.Top} className="!bg-surface-3 !w-2 !h-2" />
      
      <div className={`p-2 rounded-lg ${getBadgeColor()} border flex items-center justify-center`}>
        <Icon className="h-4.5 w-4.5 flex-shrink-0" />
      </div>

      <div className="flex-1 min-w-0">
        <span className="text-[9px] text-faint uppercase tracking-widest block font-bold">{type}</span>
        <span className="text-xs font-bold text-strong truncate block mt-0.5">{data.label}</span>
      </div>

      {/* Node output Handle */}
      <Handle type="source" position={Position.Bottom} className="!bg-surface-3 !w-2 !h-2" />
    </div>
  );
}
