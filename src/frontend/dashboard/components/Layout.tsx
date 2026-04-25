import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  PieChart, 
  Bot, 
  Calculator, 
  Settings, 
  Menu,
  Bell,
  User,
  LogOut,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/portfolio', label: 'Portfolio', icon: PieChart },
    { path: '/agents', label: 'AI Agents', icon: Bot },
    { path: '/tax', label: 'Tax & Compliance', icon: Calculator },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b border-gray-200 dark:border-gray-700">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          {sidebarOpen && (
            <div className="ml-3 flex items-center">
              <TrendingUp className="w-6 h-6 text-blue-600" />
              <span className="ml-2 font-bold text-gray-900 dark:text-white">FinMaster</span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2.5 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`
                }
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && <span className="ml-3 font-medium">{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>

        {/* Status */}
        {sidebarOpen && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-gray-600 dark:text-gray-400">8 Agents Active</span>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              System v1.0.5 • 4.2★ → 5.0★
            </div>
          </div>
        )}

        {/* User */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button className="flex items-center w-full hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2">
            <User className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            {sidebarOpen && (
              <div className="ml-3 text-left">
                <p className="text-sm font-medium text-gray-900 dark:text-white">Admin</p>
                <p className="text-xs text-gray-500">View Profile</p>
              </div>
            )}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            Financial Master Dashboard
          </h1>
          
          <div className="flex items-center space-x-4">
            {/* Alerts */}
            <button className="relative p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {/* Emergency Kill Switch */}
            <button 
              className="flex items-center px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
              onClick={() => {
                if (window.confirm('🛑 EMERGENCY STOP: This will halt all trading. Are you sure?')) {
                  alert('Emergency stop activated. All trading halted.');
                }
              }}
            >
              <AlertTriangle className="w-4 h-4 mr-1.5" />
              KILL SWITCH
            </button>

            {/* Logout */}
            <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
