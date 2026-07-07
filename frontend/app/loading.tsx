'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

export default function RootLoading() {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#05070B] text-slate-400">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <p className="text-sm font-semibold tracking-wide text-blue-400 font-sans">
          Tracing timelines...
        </p>
      </div>
    </div>
  );
}
