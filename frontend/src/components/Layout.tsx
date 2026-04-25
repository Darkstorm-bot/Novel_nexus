import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  BookOpen,
  Users,
  BrainCircuit,
  FileText,
  Settings,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';
import { useUIStore } from '../store';
import Notifications from './Notifications';

const Layout: React.FC = () => {
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: BookOpen, label: 'Stories', path: '/stories' },
    { icon: Users, label: 'Characters', path: '/characters' },
    { icon: BrainCircuit, label: 'Memory', path: '/memory' },
    { icon: FileText, label: 'Pipeline', path: '/pipeline' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 280 : 0, opacity: sidebarOpen ? 1 : 0 }}
        className="glass border-r border-dark-700/50 flex flex-col overflow-hidden"
      >
        {/* Logo */}
        <div className="p-6 border-b border-dark-700/50">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center glow-primary transition-all group-hover:scale-110">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Narrative Nexus</h1>
              <p className="text-xs text-dark-400">AI Story Platform</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30 glow-primary'
                    : 'text-dark-300 hover:bg-dark-800/50 hover:text-dark-100'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-dark-700/50">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-dark-800/50">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-accent-400" />
            <div className="flex-1">
              <p className="text-sm font-medium text-dark-200">Writer</p>
              <p className="text-xs text-dark-400">Pro Plan</p>
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="glass border-b border-dark-700/50 px-6 py-4 flex items-center justify-between">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-dark-800/50 transition-colors"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <div className="flex items-center gap-4">
            <span className="text-sm text-dark-400">
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>

      {/* Notifications */}
      <Notifications />
    </div>
  );
};

export default Layout;
