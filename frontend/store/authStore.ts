import { create } from 'zustand';

interface User {
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, token: string, user: User) => void;
  logout: () => void;
  setDemoUser: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  login: (email, token, user) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chronos_token', token);
      localStorage.setItem('chronos_user', JSON.stringify(user));
    }
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('chronos_token');
      localStorage.removeItem('chronos_user');
    }
    set({ user: null, token: null, isAuthenticated: false });
  },
  setDemoUser: () => {
    const demoUser = {
      email: 'demo@chronos.ai',
      name: 'Chronos Demo Admin',
      role: 'Restaurant Manager',
    };
    if (typeof window !== 'undefined') {
      localStorage.setItem('chronos_token', 'demo-secret-jwt-token-chronos');
      localStorage.setItem('chronos_user', JSON.stringify(demoUser));
    }
    set({
      user: demoUser,
      token: 'demo-secret-jwt-token-chronos',
      isAuthenticated: true,
    });
  },
}));
