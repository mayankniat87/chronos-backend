'use client';

import React, { useEffect } from 'react';
import { ShieldAlert, RotateCcw } from 'lucide-react';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function RootError({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log exception to logging systems if available
  }, [error]);

  return (
    <div className="flex h-screen w-full items-center justify-center bg-background p-4 text-center font-sans">
      <div className="glass-card p-8 rounded-2xl border border-red-500/10 bg-red-500/5 max-w-md w-full space-y-6">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/10 text-red-400 border border-red-500/15">
          <ShieldAlert className="h-6 w-6" />
        </div>

        <div className="space-y-2">
          <h2 className="text-xl font-bold text-foreground tracking-tight">Timeline Index Error</h2>
          <p className="text-xs text-muted leading-relaxed">
            An anomaly was detected while calculating node projections. The runtime logs report:
          </p>
          <div className="p-3 rounded-lg bg-surface-deep/60 border border-edge text-left font-mono text-[10px] text-red-400 overflow-x-auto select-text">
            {error.message || 'Unknown runtime error.'}
          </div>
        </div>

        <button
          onClick={reset}
          className="w-full py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-semibold shadow-md shadow-red-500/10 transition-all cursor-pointer flex items-center justify-center gap-2"
        >
          <RotateCcw className="h-4.5 w-4.5" />
          <span>Reset Simulation Boundary</span>
        </button>
      </div>
    </div>
  );
}
