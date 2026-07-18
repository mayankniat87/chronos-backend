import { create } from 'zustand';

export type ThemePreference = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

export const THEME_STORAGE_KEY = 'chronos_theme';

export function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'dark';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function resolveTheme(preference: ThemePreference): ResolvedTheme {
  return preference === 'system' ? getSystemTheme() : preference;
}

/** Apply the resolved theme to <html>. Single source of DOM mutation. */
export function applyThemeClass(resolved: ResolvedTheme) {
  if (typeof document === 'undefined') return;
  document.documentElement.classList.toggle('dark', resolved === 'dark');
}

function readStoredTheme(): ThemePreference {
  if (typeof window === 'undefined') return 'system';
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  return stored === 'light' || stored === 'dark' || stored === 'system' ? stored : 'system';
}

interface SettingsState {
  apiBaseUrl: string;
  demoMode: boolean;
  theme: ThemePreference;
  resolvedTheme: ResolvedTheme;
  notificationsEnabled: boolean;
  mobileSidebarOpen: boolean;
  setApiBaseUrl: (url: string) => void;
  setDemoMode: (enabled: boolean) => void;
  setTheme: (theme: ThemePreference) => void;
  syncResolvedTheme: () => void;
  setNotificationsEnabled: (enabled: boolean) => void;
  setMobileSidebarOpen: (open: boolean) => void;
}

const DEFAULT_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useSettingsStore = create<SettingsState>((set, get) => ({
  apiBaseUrl: DEFAULT_API_BASE_URL,
  demoMode: true,
  theme: readStoredTheme(),
  resolvedTheme: resolveTheme(readStoredTheme()),
  notificationsEnabled: true,
  mobileSidebarOpen: false,
  setApiBaseUrl: (apiBaseUrl) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chronos_api_url', apiBaseUrl);
    }
    set({ apiBaseUrl });
  },
  setDemoMode: (demoMode) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chronos_demo_mode', String(demoMode));
    }
    set({ demoMode });
  },
  setTheme: (theme) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    }
    const resolvedTheme = resolveTheme(theme);
    applyThemeClass(resolvedTheme);
    set({ theme, resolvedTheme });
  },
  /** Re-resolve when the OS theme changes while preference is 'system'. */
  syncResolvedTheme: () => {
    const resolvedTheme = resolveTheme(get().theme);
    applyThemeClass(resolvedTheme);
    set({ resolvedTheme });
  },
  setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
  setMobileSidebarOpen: (mobileSidebarOpen) => set({ mobileSidebarOpen }),
}));
