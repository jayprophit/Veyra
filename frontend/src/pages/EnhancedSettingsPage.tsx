import React, { useState, useCallback } from 'react';
import { 
  User, 
  Bell, 
  Shield, 
  Key, 
  Database, 
  Globe, 
  Accessibility, 
  Download,
  Upload,
  Monitor,
  Palette,
  Type,
  Maximize
} from 'lucide-react';
import { useLocalStorage, useSettings } from '../hooks/useLocalStorage';
import { Modal } from '../components/UI/Modal';

// Avatar options
const AVATARS = ['🌐', '👤', '🦁', '🐉', '🤖', '👑', '🦊', '🦉', '🐺', '⚡', '🔥', '💎'];

// Currency options
const CURRENCIES = [
  { code: 'GBP', flag: '🇬🇧', name: 'British Pound' },
  { code: 'USD', flag: '🇺🇸', name: 'US Dollar' },
  { code: 'EUR', flag: '🇪🇺', name: 'Euro' },
  { code: 'CAD', flag: '🇨🇦', name: 'Canadian Dollar' },
  { code: 'AUD', flag: '🇦🇺', name: 'Australian Dollar' },
  { code: 'JPY', flag: '🇯🇵', name: 'Japanese Yen' },
  { code: 'INR', flag: '🇮🇳', name: 'Indian Rupee' },
  { code: 'CHF', flag: '🇨🇭', name: 'Swiss Franc' },
];

// Color blindness modes
const COLOR_MODES = [
  { value: 'normal', label: 'Normal' },
  { value: 'deuteranopia', label: 'Deuteranopia (Green-Blind)' },
  { value: 'protanopia', label: 'Protanopia (Red-Blind)' },
  { value: 'tritanopia', label: 'Tritanopia (Blue-Blind)' },
  { value: 'monochromacy', label: 'Monochromacy (B&W)' },
];

// Setting definitions
const SETTING_DEFINITIONS = [
  { group: 'Display', label: 'Dark Theme', description: 'Dark interface (default)' },
  { group: 'Display', label: 'Compact Mode', description: 'Reduce spacing for more data density' },
  { group: 'Data', label: 'Show All Data (Good + Bad)', description: 'Show poor data — reveals gaps & improvement areas' },
  { group: 'Data', label: 'Auto-refresh Data', description: 'Automatically refresh market data' },
  { group: 'Notifications', label: 'Price Alerts', description: 'Get notified when price targets are hit' },
  { group: 'Notifications', label: 'Risk Warnings', description: 'Important risk threshold breaches' },
  { group: 'Notifications', label: 'Daily Summary', description: 'Daily portfolio summary email' },
  { group: 'Notifications', label: 'Order Executions', description: 'Get notified when orders are filled' },
  { group: 'Privacy', label: 'Block Trackers', description: 'Block analytics and tracking scripts' },
  { group: 'Privacy', label: 'Mask Portfolio Values', description: 'Hide actual values in UI' },
];

interface ProfileData {
  name: string;
  email: string;
  avatar: string;
  timezone: string;
  language: string;
}

export const EnhancedSettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const { settings, toggleSetting } = useSettings();
  const [fontSize, setFontSize] = useLocalStorage<number>('fm_fontSize', 100);
  const [currency, setCurrency] = useLocalStorage<string>('fm_currency', 'USD');
  const [colorMode, setColorMode] = useLocalStorage<string>('fm_colorMode', 'normal');
  const [profile, setProfile] = useLocalStorage<ProfileData>('fm_profile', {
    name: 'Admin',
    email: 'admin@financialmaster.com',
    avatar: '👤',
    timezone: 'UTC',
    language: 'English',
  });
  const [showAvatarModal, setShowAvatarModal] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  const handleBackup = useCallback(() => {
    const backup = {
      settings,
      profile,
      currency,
      fontSize,
      colorMode,
      timestamp: new Date().toISOString(),
      version: '2.60.0',
    };
    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `financial-master-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [settings, profile, currency, fontSize, colorMode]);

  const handleRestore = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const data = JSON.parse(event.target?.result as string);
            // Restore data
            if (data.settings) localStorage.setItem('fm_settings', JSON.stringify(data.settings));
            if (data.profile) localStorage.setItem('fm_profile', JSON.stringify(data.profile));
            if (data.currency) localStorage.setItem('fm_currency', data.currency);
            if (data.fontSize) localStorage.setItem('fm_fontSize', String(data.fontSize));
            if (data.colorMode) localStorage.setItem('fm_colorMode', data.colorMode);
            window.location.reload();
          } catch (err) {
            alert('Invalid backup file');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }, []);

  const groupedSettings = SETTING_DEFINITIONS.reduce((acc, setting) => {
    if (!acc[setting.group]) acc[setting.group] = [];
    acc[setting.group].push(setting);
    return acc;
  }, {} as Record<string, typeof SETTING_DEFINITIONS>);

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'data', label: 'Data Sources', icon: Database },
    { id: 'backup', label: 'Backup & Restore', icon: Download },
  ];

  return (
    <div className="flex space-x-6 ds-animate-in">
      {/* Sidebar */}
      <div className="w-64 ds-card" style={{ padding: '16px', height: 'fit-content' }}>
        <nav className="space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-600/30'
                    : 'text-gray-400 hover:bg-white/5'
                }`}
              >
                <Icon size={18} />
                <span className="text-sm">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 ds-card">
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className="ds-card-header">
              <h3 className="ds-card-title">Profile Settings</h3>
            </div>
            
            {/* Avatar Section */}
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
              <div className="ds-card-header">
                <h4 style={{ fontSize: '0.83rem', fontWeight: 600 }}>Avatar</h4>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <div 
                  style={{ 
                    width: 60, 
                    height: 60, 
                    background: 'var(--ds-bg-4)', 
                    borderRadius: '50%', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    fontSize: '1.8rem',
                    cursor: 'pointer',
                    border: '2px solid var(--ds-border-2)',
                  }}
                  onClick={() => setShowAvatarModal(true)}
                >
                  {profile.avatar}
                </div>
                <button className="ds-btn ds-btn-secondary ds-btn-sm" onClick={() => setShowAvatarModal(true)}>
                  Change Avatar
                </button>
              </div>
            </div>

            {/* Profile Fields */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Display Name</label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  className="ds-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  className="ds-input"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Timezone</label>
                  <select
                    value={profile.timezone}
                    onChange={(e) => setProfile({ ...profile, timezone: e.target.value })}
                    className="ds-input"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">America/New_York</option>
                    <option value="Europe/London">Europe/London</option>
                    <option value="Asia/Tokyo">Asia/Tokyo</option>
                    <option value="Australia/Sydney">Australia/Sydney</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Language</label>
                  <select
                    value={profile.language}
                    onChange={(e) => setProfile({ ...profile, language: e.target.value })}
                    className="ds-input"
                  >
                    <option value="English">English</option>
                    <option value="Spanish">Spanish</option>
                    <option value="French">French</option>
                    <option value="German">German</option>
                    <option value="Chinese">Chinese</option>
                    <option value="Japanese">Japanese</option>
                    <option value="Arabic">Arabic</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'appearance' && (
          <div className="space-y-6">
            <div className="ds-card-header">
              <h3 className="ds-card-title">Appearance & Accessibility</h3>
            </div>

            {/* Font Size */}
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '0.83rem', fontWeight: 600 }}>Font Size</div>
                  <div style={{ fontSize: '0.73rem', color: 'var(--ds-text-muted)' }}>Adjust text size</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button 
                    className="ds-btn ds-btn-secondary ds-btn-sm"
                    onClick={() => setFontSize(Math.max(80, fontSize - 10))}
                  >
                    A-
                  </button>
                  <span style={{ fontSize: '0.78rem', minWidth: '45px', textAlign: 'center' }}>
                    {fontSize}%
                  </span>
                  <button 
                    className="ds-btn ds-btn-secondary ds-btn-sm"
                    onClick={() => setFontSize(Math.min(150, fontSize + 10))}
                  >
                    A+
                  </button>
                </div>
              </div>
            </div>

            {/* Color Mode */}
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '0.83rem', fontWeight: 600 }}>Colour Mode</div>
                  <div style={{ fontSize: '0.73rem', color: 'var(--ds-text-muted)' }}>Colour blindness support</div>
                </div>
                <select
                  value={colorMode}
                  onChange={(e) => setColorMode(e.target.value)}
                  className="ds-input"
                  style={{ width: '180px' }}
                >
                  {COLOR_MODES.map(mode => (
                    <option key={mode.value} value={mode.value}>{mode.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Fullscreen */}
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '0.83rem', fontWeight: 600 }}>Fullscreen Mode</div>
                  <div style={{ fontSize: '0.73rem', color: 'var(--ds-text-muted)' }}>Toggle fullscreen</div>
                </div>
                <button className="ds-btn ds-btn-secondary ds-btn-sm" onClick={handleFullscreen}>
                  <Maximize size={14} />
                  {isFullscreen ? 'Exit' : 'Enter'}
                </button>
              </div>
            </div>

            {/* Currency */}
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
              <div className="ds-card-header">
                <h4 style={{ fontSize: '0.83rem', fontWeight: 600 }}>Currency</h4>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {CURRENCIES.map(curr => (
                  <button
                    key={curr.code}
                    onClick={() => setCurrency(curr.code)}
                    className={`ds-btn ds-btn-sm ${currency === curr.code ? 'ds-btn-primary' : 'ds-btn-secondary'}`}
                  >
                    {curr.flag} {curr.code}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="space-y-4">
            <div className="ds-card-header">
              <h3 className="ds-card-title">Notification Preferences</h3>
            </div>
            {groupedSettings['Notifications']?.map((setting) => (
              <div 
                key={setting.label}
                className="ds-card"
                style={{ 
                  background: 'var(--ds-bg-3)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.83rem', fontWeight: 600 }}>{setting.label}</div>
                  <div style={{ fontSize: '0.73rem', color: 'var(--ds-text-muted)' }}>{setting.description}</div>
                </div>
                <div 
                  className={`ds-toggle ${settings[setting.label] ? 'active' : ''}`}
                  onClick={() => toggleSetting(setting.label)}
                />
              </div>
            ))}
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-6">
            <div className="ds-card-header">
              <h3 className="ds-card-title">Security Settings</h3>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Current Password</label>
                <input type="password" className="ds-input" placeholder="••••••••" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">New Password</label>
                <input type="password" className="ds-input" placeholder="••••••••" />
              </div>
              <div className="ds-card" style={{ background: 'var(--ds-bg-3)', padding: '12px 16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: '0.83rem', fontWeight: 600 }}>Two-Factor Authentication</div>
                    <div style={{ fontSize: '0.73rem', color: 'var(--ds-text-muted)' }}>Secure your account with 2FA</div>
                  </div>
                  <div className="ds-toggle" />
                </div>
              </div>
              {groupedSettings['Privacy']?.map((setting) => (
                <div 
                  key={setting.label}
                  className="ds-card"
                  style={{ 
                    background: 'var(--ds-bg-3)', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '0.83rem', fontWeight: 600 }}>{setting.label}</div>
                    <div style={{ fontSize: '0.73rem', color: 'var(--ds-text-muted)' }}>{setting.description}</div>
                  </div>
                  <div 
                    className={`ds-toggle ${settings[setting.label] ? 'active' : ''}`}
                    onClick={() => toggleSetting(setting.label)}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'api' && (
          <div className="space-y-4">
            <div className="ds-card-header">
              <h3 className="ds-card-title">API Configuration</h3>
            </div>
            {[
              { name: 'Polygon.io', key: 'POLYGON_API_KEY', masked: 'pk_...7f9a' },
              { name: 'Alpaca', key: 'ALPACA_API_KEY', masked: 'PK...3d2f' },
              { name: 'OpenAI', key: 'OPENAI_API_KEY', masked: 'sk-...x7y2' },
            ].map((api) => (
              <div key={api.name} className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <p style={{ fontWeight: 600, fontSize: '0.85rem' }}>{api.name}</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--ds-text-muted)', fontFamily: 'var(--ds-font-mono)' }}>
                      {api.masked}
                    </p>
                  </div>
                  <button className="ds-btn ds-btn-primary ds-btn-sm">Update</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'data' && (
          <div className="space-y-4">
            <div className="ds-card-header">
              <h3 className="ds-card-title">Data Source Configuration</h3>
            </div>
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
              <p style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '8px' }}>Primary Data Source</p>
              <select className="ds-input">
                <option>Polygon.io (Live)</option>
                <option>Alpaca (Paper Trading)</option>
                <option>Mock Data (Development)</option>
              </select>
            </div>
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)' }}>
              <p style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '8px' }}>Update Frequency</p>
              <select className="ds-input">
                <option>Real-time (WebSocket)</option>
                <option>1 second</option>
                <option>5 seconds</option>
                <option>1 minute</option>
              </select>
            </div>
            {groupedSettings['Data']?.map((setting) => (
              <div 
                key={setting.label}
                className="ds-card"
                style={{ 
                  background: 'var(--ds-bg-3)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.83rem', fontWeight: 600 }}>{setting.label}</div>
                  <div style={{ fontSize: '0.73rem', color: 'var(--ds-text-muted)' }}>{setting.description}</div>
                </div>
                <div 
                  className={`ds-toggle ${settings[setting.label] ? 'active' : ''}`}
                  onClick={() => toggleSetting(setting.label)}
                />
              </div>
            ))}
          </div>
        )}

        {activeTab === 'backup' && (
          <div className="space-y-6">
            <div className="ds-card-header">
              <h3 className="ds-card-title">Backup & Restore</h3>
            </div>
            <p style={{ fontSize: '0.79rem', color: 'var(--ds-text-muted)', marginBottom: '16px' }}>
              Export all your data, settings and preferences as a portable backup file.
            </p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button className="ds-btn ds-btn-primary" onClick={handleBackup}>
                <Download size={16} />
                Download Backup
              </button>
              <button className="ds-btn ds-btn-secondary" onClick={handleRestore}>
                <Upload size={16} />
                Restore Backup
              </button>
            </div>
            
            <div className="ds-card" style={{ background: 'var(--ds-bg-3)', marginTop: '20px' }}>
              <h4 style={{ fontSize: '0.83rem', fontWeight: 600, marginBottom: '10px' }}>Storage Usage</h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ flex: 1, height: '8px', background: 'var(--ds-bg-4)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: '15%', height: '100%', background: 'var(--ds-primary)' }} />
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--ds-text-muted)' }}>~150 KB used</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Avatar Selection Modal */}
      <Modal
        isOpen={showAvatarModal}
        onClose={() => setShowAvatarModal(false)}
        title="Select Avatar"
        footer={
          <>
            <button 
              className="ds-btn ds-btn-secondary ds-btn-sm" 
              onClick={() => setProfile({ ...profile, avatar: '👤' })}
            >
              Reset
            </button>
            <button 
              className="ds-btn ds-btn-primary ds-btn-sm" 
              onClick={() => setShowAvatarModal(false)}
            >
              Done
            </button>
          </>
        }
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '10px' }}>
          {AVATARS.map(avatar => (
            <div
              key={avatar}
              onClick={() => setProfile({ ...profile, avatar })}
              style={{
                width: '50px',
                height: '50px',
                background: profile.avatar === avatar ? 'var(--ds-primary)' : 'var(--ds-bg-3)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.6rem',
                cursor: 'pointer',
                border: `2px solid ${profile.avatar === avatar ? 'var(--ds-primary)' : 'transparent'}`,
                transition: 'all 0.12s',
              }}
            >
              {avatar}
            </div>
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default EnhancedSettingsPage;
