import { create } from 'zustand';

interface SettingsState {
  apiBaseUrl: string;
  demoMode: boolean;
  theme: 'dark' | 'light';
  notificationsEnabled: boolean;
  mobileSidebarOpen: boolean;
  setApiBaseUrl: (url: string) => void;
  setDemoMode: (enabled: boolean) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setNotificationsEnabled: (enabled: boolean) => void;
  setMobileSidebarOpen: (open: boolean) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  apiBaseUrl: 'http://localhost:8000',
  demoMode: true,
  theme: 'dark',
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
  setTheme: (theme) => set({ theme }),
  setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
  setMobileSidebarOpen: (mobileSidebarOpen) => set({ mobileSidebarOpen }),
}));
