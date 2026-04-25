import React, { useState } from 'react';
import { Bell, Shield, User, Key, Database } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile');

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'data', label: 'Data Sources', icon: Database },
  ];

  return (
    <div className="flex space-x-6">
      {/* Sidebar */}
      <div className="w-64 bg-white rounded-lg shadow p-4">
        <nav className="space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon size={20} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 bg-white rounded-lg shadow p-6">
        {activeTab === 'profile' && <ProfileSettings />}
        {activeTab === 'notifications' && <NotificationSettings />}
        {activeTab === 'security' && <SecuritySettings />}
        {activeTab === 'api' && <APISettings />}
        {activeTab === 'data' && <DataSettings />}
      </div>
    </div>
  );
};

const ProfileSettings: React.FC = () => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold">Profile Settings</h3>
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Display Name</label>
        <input
          type="text"
          defaultValue="Admin"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Email</label>
        <input
          type="email"
          defaultValue="admin@financialmaster.com"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Timezone</label>
        <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
          <option>UTC</option>
          <option>America/New_York</option>
          <option>Europe/London</option>
        </select>
      </div>
    </div>
  </div>
);

const NotificationSettings: React.FC = () => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold">Notification Preferences</h3>
    <div className="space-y-4">
      {[
        { label: 'Order Executions', description: 'Get notified when orders are filled' },
        { label: 'Price Alerts', description: 'Alerts when price targets are hit' },
        { label: 'Risk Warnings', description: 'Important risk threshold breaches' },
        { label: 'Daily Summary', description: 'Daily portfolio summary email' },
      ].map((item) => (
        <div key={item.label} className="flex items-center justify-between py-3 border-b">
          <div>
            <p className="font-medium">{item.label}</p>
            <p className="text-sm text-gray-500">{item.description}</p>
          </div>
          <input type="checkbox" defaultChecked className="h-5 w-5" />
        </div>
      ))}
    </div>
  </div>
);

const SecuritySettings: React.FC = () => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold">Security Settings</h3>
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Current Password</label>
        <input type="password" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">New Password</label>
        <input type="password" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Two-Factor Authentication</label>
        <div className="mt-2 flex items-center">
          <input type="checkbox" className="h-5 w-5 mr-2" />
          <span className="text-sm text-gray-600">Enable 2FA</span>
        </div>
      </div>
    </div>
  </div>
);

const APISettings: React.FC = () => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold">API Configuration</h3>
    <div className="space-y-4">
      {[
        { name: 'Polygon.io', key: 'POLYGON_API_KEY', masked: 'pk_...7f9a' },
        { name: 'Alpaca', key: 'ALPACA_API_KEY', masked: 'PK...3d2f' },
        { name: 'OpenAI', key: 'OPENAI_API_KEY', masked: 'sk-...x7y2' },
      ].map((api) => (
        <div key={api.name} className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{api.name}</p>
              <p className="text-sm text-gray-500 font-mono">{api.masked}</p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
              Update
            </button>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const DataSettings: React.FC = () => (
  <div className="space-y-6">
    <h3 className="text-lg font-semibold">Data Source Configuration</h3>
    <div className="space-y-4">
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="font-medium">Primary Data Source</p>
        <select className="mt-2 block w-full rounded-md border-gray-300 shadow-sm">
          <option>Polygon.io (Live)</option>
          <option>Alpaca (Paper Trading)</option>
          <option>Mock Data (Development)</option>
        </select>
      </div>
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="font-medium">Update Frequency</p>
        <select className="mt-2 block w-full rounded-md border-gray-300 shadow-sm">
          <option>Real-time (WebSocket)</option>
          <option>1 second</option>
          <option>5 seconds</option>
          <option>1 minute</option>
        </select>
      </div>
    </div>
  </div>
);
