'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, login } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isPublicPage = pathname === '/' || pathname === '/login';

  useEffect(() => {
    // Restore authentication state from localStorage
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('chronos_token');
      const storedUser = localStorage.getItem('chronos_user');

      if (storedToken && storedUser) {
        try {
          login(storedToken, storedToken, JSON.parse(storedUser));
        } catch {
          // Stale or corrupted token
          localStorage.removeItem('chronos_token');
          localStorage.removeItem('chronos_user');
        }
      }
    }
    setTimeout(() => {
      setLoading(false);
    }, 0);
  }, [login]);

  useEffect(() => {
    if (!loading && !isAuthenticated && !isPublicPage) {
      router.push('/login');
    }
  }, [isAuthenticated, isPublicPage, loading, router]);

  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background text-muted">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <p className="text-sm font-semibold tracking-wide text-blue-400">Restoring Chronos Session...</p>
        </div>
      </div>
    );
  }

  // Pure page view for Landing and Login pages
  if (isPublicPage) {
    return <main className="flex-1 w-full bg-background min-h-screen">{children}</main>;
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Sidebar Navigation */}
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

      {/* Main Panel Content Container */}
      <div
        className="flex-1 flex flex-col min-w-0 transition-all duration-300"
        style={{ paddingLeft: isMobile ? 0 : (collapsed ? 80 : 260) }}
      >
        {/* Navbar */}
        <Navbar />

        {/* Dynamic Route Panel */}
        <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
