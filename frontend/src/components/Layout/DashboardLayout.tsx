import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  Brain,
  Shield,
  Settings,
  Bell,
  User
} from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { ConnectionStatus } from './ConnectionStatus';

const navItems = [
  { path: '/portfolio', icon: LayoutDashboard, label: 'Portfolio' },
  { path: '/trading', icon: TrendingUp, label: 'Trading' },
  { path: '/market', icon: BarChart3, label: 'Market Data' },
  { path: '/analysis', icon: Brain, label: 'AI Analysis' },
  { path: '/risk', icon: Shield, label: 'Risk' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const DashboardLayout: React.FC = () => {
  const location = useLocation();
  const { connected, alerts } = useWebSocket();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold">Financial Master</h1>
          <p className="text-xs text-slate-400 mt-1">v2.50.0</p>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <ConnectionStatus connected={connected} />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">
              {navItems.find((item) => item.path === location.pathname)?.label || 'Dashboard'}
            </h2>
          </div>

          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
              <Bell size={20} />
              {alerts.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>

            {/* User */}
            <button className="flex items-center space-x-2 p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
              <User size={20} />
              <span className="text-sm font-medium">Admin</span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
