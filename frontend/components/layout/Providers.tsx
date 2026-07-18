'use client';

import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSettingsStore } from '@/store/settingsStore';

interface ProvidersProps {
  children: React.ReactNode;
}

/**
 * Keeps the resolved theme in sync after hydration:
 * - re-applies the stored preference to <html>
 * - listens for OS prefers-color-scheme changes while preference is 'system'
 * The initial (pre-hydration) theme is applied by the inline script in layout.tsx,
 * so there is no flash and no hydration mismatch.
 */
function ThemeSync() {
  const syncResolvedTheme = useSettingsStore((s) => s.syncResolvedTheme);
  const theme = useSettingsStore((s) => s.theme);

  useEffect(() => {
    syncResolvedTheme();
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => {
      if (useSettingsStore.getState().theme === 'system') {
        syncResolvedTheme();
      }
    };
    media.addEventListener('change', onChange);
    return () => media.removeEventListener('change', onChange);
  }, [theme, syncResolvedTheme]);

  return null;
}

export default function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeSync />
      {children}
    </QueryClientProvider>
  );
}
