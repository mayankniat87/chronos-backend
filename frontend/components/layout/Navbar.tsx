'use client';

import React, { useState, useEffect } from 'react';
import { useRestaurantStore } from '@/store/restaurantStore';
import { useSettingsStore } from '@/store/settingsStore';
import { useAuthStore } from '@/store/authStore';
import {
  Bell,
  ChevronDown,
  User,
  AlertTriangle,
  Moon,
  Sun,
  Monitor,
  CheckCircle2,
  Menu
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
  const { restaurants, selectedRestaurant, setSelectedRestaurant } = useRestaurantStore();
  const { demoMode, theme, resolvedTheme, setTheme, mobileSidebarOpen, setMobileSidebarOpen } = useSettingsStore();
  const { user } = useAuthStore();
  
  const [restaurantDropdownOpen, setRestaurantDropdownOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  // Theme preference comes from localStorage, which the server can't see.
  // Render the theme icon only after mount to avoid a hydration mismatch.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const mockNotifications = [
    { id: 'not_1', type: 'success', text: 'Simulation "Wine Pricing Optimization" completed successfully.' },
    { id: 'not_2', type: 'warning', text: 'Supply Chain: Organic greens inventory levels falling below safety threshold.' },
    { id: 'not_3', type: 'info', text: 'Bistro Downtown: Monthly reports compiled and ready for audit.' },
  ];

  return (
    <header className="sticky top-0 right-0 left-0 z-30 h-16 glass-panel border-b border-edge/80 px-6 flex items-center justify-between text-strong">
      
      {/* Left section: Restaurant Selector */}
      <div className="flex items-center gap-4">
        {/* Hamburger Menu on Mobile */}
        <button
          onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
          className="md:hidden p-1.5 rounded-lg hover:bg-surface-2 text-muted hover:text-strong transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          aria-label="Toggle sidebar menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="relative">
          <button
            onClick={() => setRestaurantDropdownOpen(!restaurantDropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-edge-strong bg-surface/60 hover:bg-surface-2/70 hover:border-edge-strong transition-all text-sm font-medium focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="truncate max-w-[180px]">{selectedRestaurant?.name || 'Select Restaurant'}</span>
            <ChevronDown className="h-4 w-4 text-muted" />
          </button>
          
          <AnimatePresence>
            {restaurantDropdownOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setRestaurantDropdownOpen(false)} />
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.15 }}
                  className="absolute left-0 mt-2 w-64 rounded-xl border border-edge bg-surface p-1.5 shadow-2xl z-20"
                >
                  <p className="text-xs text-faint font-semibold px-2.5 py-1.5 tracking-wider uppercase">Active Restaurant Nodes</p>
                  {restaurants.map((rest) => (
                    <button
                      key={rest.id}
                      onClick={() => {
                        setSelectedRestaurant(rest);
                        setRestaurantDropdownOpen(false);
                      }}
                      className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-sm transition-colors ${
                        selectedRestaurant?.id === rest.id
                          ? 'bg-blue-600/10 text-blue-400 border border-blue-500/10'
                          : 'hover:bg-surface-2/80 text-strong'
                      }`}
                    >
                      <span className="font-medium truncate">{rest.name}</span>
                      <span className="text-xs text-faint">{rest.location}</span>
                    </button>
                  ))}
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        {demoMode && (
          <div className="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-full border border-amber-500/20 bg-amber-500/10 text-amber-400 text-xs font-semibold glow-bg-purple/20">
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>Sandbox Demo Active</span>
          </div>
        )}
      </div>

      {/* Right section: Global search, notifications, theme, profile */}
      <div className="flex items-center gap-4">
        
        {/* Theme toggle: cycles Light -> Dark -> System */}
        <button
          onClick={() => setTheme(theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light')}
          className="rounded-lg p-2 text-muted hover:bg-surface-2/60 hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          aria-label={mounted ? `Theme: ${theme}. Click to switch.` : 'Toggle theme'}
          title={mounted ? `Theme: ${theme}` : undefined}
        >
          {!mounted || theme === 'system' ? (
            <Monitor className="h-5 w-5" />
          ) : resolvedTheme === 'dark' ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </button>

        {/* Notifications dropdown */}
        <div className="relative">
          <button
            onClick={() => setNotificationOpen(!notificationOpen)}
            className="relative rounded-lg p-2 text-muted hover:bg-surface-2/60 hover:text-foreground transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-blue-500 ring-2 ring-surface" />
          </button>

          <AnimatePresence>
            {notificationOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setNotificationOpen(false)} />
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 mt-2 w-80 rounded-xl border border-edge bg-surface p-2 shadow-2xl z-20"
                >
                  <div className="flex justify-between items-center px-2 py-1.5 border-b border-edge mb-1">
                    <span className="text-xs font-bold text-muted">Simulation Feed</span>
                    <button className="text-[10px] text-blue-400 hover:underline">Clear all</button>
                  </div>
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {mockNotifications.map((not) => (
                      <div key={not.id} className="p-2 rounded-lg hover:bg-surface-2/50 flex gap-2.5 items-start text-xs border border-transparent hover:border-edge/30">
                        {not.type === 'success' && <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />}
                        {not.type === 'warning' && <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0 mt-0.5" />}
                        {not.type === 'info' && <Bell className="h-4 w-4 text-blue-400 flex-shrink-0 mt-0.5" />}
                        <p className="text-strong leading-relaxed">{not.text}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        {/* User profile dropdown */}
        <div className="relative">
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex items-center gap-2 rounded-lg p-1.5 border border-edge/50 hover:bg-surface-2/60 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="User profile details"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600/10 text-blue-400 font-semibold border border-blue-500/20">
              <User className="h-4 w-4" />
            </div>
            <span className="hidden md:inline text-xs font-medium text-strong truncate max-w-[100px]">{user?.name || 'Administrator'}</span>
            <ChevronDown className="h-3.5 w-3.5 text-faint" />
          </button>

          <AnimatePresence>
            {profileOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setProfileOpen(false)} />
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 mt-2 w-48 rounded-xl border border-edge bg-surface p-1.5 shadow-2xl z-20 text-sm"
                >
                  <div className="px-3 py-2 border-b border-edge text-xs">
                    <p className="font-semibold text-strong">{user?.name || 'Operator'}</p>
                    <p className="text-faint truncate">{user?.email || 'operator@chronos.ai'}</p>
                  </div>
                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      // Route to settings
                    }}
                    className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-muted hover:bg-surface-2/60 hover:text-strong transition-colors"
                  >
                    <User className="h-4 w-4" />
                    <span>My Account</span>
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

      </div>
    </header>
  );
}
