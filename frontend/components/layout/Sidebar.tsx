'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/store/authStore';
import { useSettingsStore } from '@/store/settingsStore';
import {
  LayoutDashboard,
  UploadCloud,
  MessageSquare,
  Network,
  History,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  TrendingUp
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

export default function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuthStore();
  const { mobileSidebarOpen, setMobileSidebarOpen } = useSettingsStore();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Upload Data', path: '/upload', icon: UploadCloud },
    { name: 'Ask AI', path: '/ask', icon: MessageSquare },
    { name: 'Knowledge Graph', path: '/graph', icon: Network },
    { name: 'Decision History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleNavClick = () => {
    if (isMobile) {
      setMobileSidebarOpen(false);
    }
  };

  return (
    <>
      {/* Mobile Drawer Overlay Backdrop */}
      {isMobile && mobileSidebarOpen && (
        <div
          onClick={() => setMobileSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm transition-opacity duration-300 md:hidden"
        />
      )}

      <motion.aside
        animate={{
          width: isMobile ? 260 : (collapsed ? 80 : 260),
          x: isMobile ? (mobileSidebarOpen ? 0 : -260) : 0,
        }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="fixed left-0 top-0 bottom-0 z-40 flex flex-col glass-panel border-r border-slate-800 text-slate-200"
      >
        {/* Sidebar Header Brand */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800/80">
          <Link href="/dashboard" className="flex items-center gap-3" onClick={handleNavClick}>
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-500 shadow-md shadow-blue-500/20">
              <TrendingUp className="h-5 w-5 text-white animate-pulse" />
            </div>
            {(!collapsed || isMobile) && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent tracking-wide font-outfit"
              >
                CHRONOS
              </motion.span>
            )}
          </Link>
          {!collapsed && !isMobile && (
            <button
              onClick={() => setCollapsed(true)}
              className="rounded-lg p-1.5 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              aria-label="Collapse sidebar menu"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Nav Links */}
        <nav className="flex-1 space-y-1.5 px-3 py-6 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.path;
            const Icon = item.icon;

            return (
              <Link key={item.path} href={item.path} className="block" onClick={handleNavClick}>
                <div
                  className={`relative flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-205 group focus-within:ring-1 focus-within:ring-blue-500/30 ${
                    isActive
                      ? 'bg-blue-600/10 border border-blue-500/30 text-blue-400 glow-bg-blue'
                      : 'border border-transparent hover:bg-slate-800/50 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {/* Active Indicator Bar */}
                  {isActive && (
                    <motion.div
                      layoutId="active-indicator"
                      className="absolute left-0 top-2 bottom-2 w-1 rounded-r-md bg-cyan-400"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                  <Icon className={`h-5 w-5 flex-shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  {(!collapsed || isMobile) && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-sm font-medium tracking-wide"
                    >
                      {item.name}
                    </motion.span>
                  )}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Expand button when collapsed */}
        {collapsed && !isMobile && (
          <div className="flex justify-center py-4 border-t border-slate-800/60">
            <button
              onClick={() => setCollapsed(false)}
              className="rounded-lg p-1.5 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              aria-label="Expand sidebar menu"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        )}

        {/* User profile / Logout segment */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/20">
          {(!collapsed || isMobile) && (
            <div className="mb-3 px-2">
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase">Active Operator</p>
              <p className="text-sm font-medium text-slate-300 truncate">{user?.name || 'Chronos Guest'}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email || 'guest@chronos.ai'}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl border border-transparent hover:bg-red-500/10 hover:border-red-500/20 text-slate-400 hover:text-red-400 transition-all duration-200 group focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500/40"
            aria-label="Logout session"
          >
            <LogOut className="h-5 w-5 flex-shrink-0 group-hover:rotate-12 transition-transform duration-200" />
            {(!collapsed || isMobile) && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-sm font-medium"
              >
                Sign Out
              </motion.span>
            )}
          </button>
        </div>
      </motion.aside>
    </>
  );
}
