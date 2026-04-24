import { useState } from 'react';
import toast from 'react-hot-toast';
import {
  User,
  Bell,
  Shield,
  Database,
  Key,
  Webhook,
  Smartphone,
  Globe,
  Save,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Lock,
  Eye,
  EyeOff,
  TestTube,
  Download,
  Upload,
  Trash2,
  Cpu
} from 'lucide-react';

interface ApiConfig {
  name: string;
  key: string;
  status: 'connected' | 'error' | 'not_configured';
  lastTested?: string;
}

const mockApis: ApiConfig[] = [
  { name: 'OpenAI', key: 'sk-•••••••••••••••••••••••••', status: 'connected', lastTested: '2024-01-15 10:30' },
  { name: 'CoinGecko', key: 'CG-•••••••••••••••••••••••••', status: 'connected', lastTested: '2024-01-15 09:15' },
  { name: 'Alpha Vantage', key: 'AV•••••••••••••••••••••••••', status: 'not_configured' },
  { name: 'Telegram Bot', key: '•••••••••••••••••••••••••', status: 'connected', lastTested: '2024-01-15 08:00' },
  { name: 'Plaid', key: '•••••••••••••••••••••••••', status: 'not_configured' },
  { name: 'Twilio', key: '•••••••••••••••••••••••••', status: 'error', lastTested: '2024-01-14 16:45' }
];

const agentStatuses = [
  { id: 1, name: 'Orchestrator Agent', status: 'active', lastRun: '2 min ago', decisions: 1247 },
  { id: 2, name: 'Retirement Planner', status: 'active', lastRun: '5 min ago', decisions: 89 },
  { id: 3, name: 'Tax Optimizer', status: 'active', lastRun: '1 min ago', decisions: 234 },
  { id: 4, name: 'Risk Manager', status: 'active', lastRun: '30 sec ago', decisions: 567 },
  { id: 5, name: 'Portfolio Manager', status: 'active', lastRun: '3 min ago', decisions: 445 },
  { id: 6, name: 'FIRE Calculator', status: 'active', lastRun: '1 hour ago', decisions: 12 },
  { id: 7, name: 'Sentiment Analyzer', status: 'paused', lastRun: '2 hours ago', decisions: 89 },
  { id: 8, name: 'Rebalancing Agent', status: 'active', lastRun: '10 min ago', decisions: 34 }
];

export default function Settings() {
  const [activeTab, setActiveTab] = useState<'profile' | 'apis' | 'agents' | 'notifications' | 'security' | 'advanced'>('profile');
  const [showApiKey, setShowApiKey] = useState<Record<string, boolean>>({});
  const [darkMode, setDarkMode] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [notifications, setNotifications] = useState({
    email: true,
    telegram: true,
    sms: false,
    push: true,
    trades: true,
    alerts: true,
    reports: true,
    errors: true
  });
  const [riskTolerance, setRiskTolerance] = useState(7);
  const [autoExecute, setAutoExecute] = useState(false);
  const [maxTradeSize, setMaxTradeSize] = useState(5000);
  const [requireApproval, setRequireApproval] = useState(true);

  const handleSave = () => {
    toast.success('Settings saved successfully');
  };

  const handleTestApi = (apiName: string) => {
    toast.loading(`Testing ${apiName} connection...`, { duration: 1500 });
    setTimeout(() => {
      toast.success(`${apiName} connection successful`);
    }, 1500);
  };

  const handleBackup = () => {
    toast.success('Backup started - you will receive a download link');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-sm text-gray-500 mt-1">Configure system preferences and integrations</p>
        </div>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          <Save size={18} />
          Save Changes
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex flex-wrap gap-8">
          {[
            { id: 'profile', label: 'Profile', icon: User },
            { id: 'apis', label: 'API Keys', icon: Key },
            { id: 'agents', label: 'AI Agents', icon: Cpu },
            { id: 'notifications', label: 'Notifications', icon: Bell },
            { id: 'security', label: 'Security', icon: Shield },
            { id: 'advanced', label: 'Advanced', icon: Database }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  defaultValue="Financial Master User"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  type="email"
                  defaultValue="user@example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input
                  type="tel"
                  defaultValue="+44 7700 900000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="GBP">GBP (£) - British Pound</option>
                  <option value="USD">USD ($) - US Dollar</option>
                  <option value="EUR">EUR (€) - Euro</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Profile</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Risk Tolerance</label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={riskTolerance}
                    onChange={(e) => setRiskTolerance(parseInt(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium text-gray-900 w-8">{riskTolerance}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {riskTolerance <= 3 ? 'Conservative - Capital preservation priority' :
                   riskTolerance <= 6 ? 'Balanced - Growth with moderate risk' :
                   'Aggressive - Maximum growth potential'}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Investment Horizon</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option>Short Term (&lt; 3 years)</option>
                  <option>Medium Term (3-10 years)</option>
                  <option selected>Long Term (10+ years)</option>
                  <option>Retirement (20+ years)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Annual Income</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option>&lt; £25,000</option>
                  <option>£25,000 - £50,000</option>
                  <option>£50,000 - £100,000</option>
                  <option selected>£100,000+</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tax Status</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option>Basic Rate Taxpayer</option>
                  <option selected>Higher Rate Taxpayer</option>
                  <option>Additional Rate Taxpayer</option>
                  <option>Non-UK Resident</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 lg:col-span-2">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Display Preferences</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label className="flex items-center justify-between p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Globe size={20} className="text-gray-600" />
                  </div>
                  <span className="font-medium text-gray-900">Dark Mode</span>
                </div>
                <input
                  type="checkbox"
                  checked={darkMode}
                  onChange={(e) => setDarkMode(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded"
                />
              </label>
              <label className="flex items-center justify-between p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <RefreshCw size={20} className="text-gray-600" />
                  </div>
                  <div>
                    <span className="font-medium text-gray-900">Auto-refresh</span>
                    <p className="text-xs text-gray-500">Update data every 60s</p>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded"
                />
              </label>
              <label className="flex items-center justify-between p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Database size={20} className="text-gray-600" />
                  </div>
                  <div>
                    <span className="font-medium text-gray-900">Compact Mode</span>
                    <p className="text-xs text-gray-500">Dense data display</p>
                  </div>
                </div>
                <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" />
              </label>
            </div>
          </div>
        </div>
      )}

      {/* API Keys Tab */}
      {activeTab === 'apis' && (
        <div className="space-y-6">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-amber-600 shrink-0 mt-0.5" size={20} />
              <div>
                <h3 className="font-semibold text-amber-900">API Security</h3>
                <p className="text-sm text-amber-700">
                  API keys are encrypted at rest. Never share your keys or commit them to version control.
                  Use environment variables for production deployments.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Connected Services</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {mockApis.map((api) => (
                <div key={api.name} className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${
                        api.status === 'connected' ? 'bg-green-500' :
                        api.status === 'error' ? 'bg-red-500' : 'bg-gray-300'
                      }`} />
                      <span className="font-medium text-gray-900">{api.name}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        api.status === 'connected' ? 'bg-green-100 text-green-800' :
                        api.status === 'error' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {api.status === 'connected' ? 'Connected' :
                         api.status === 'error' ? 'Error' : 'Not Configured'}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleTestApi(api.name)}
                        className="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        <TestTube size={16} className="inline mr-1" />
                        Test
                      </button>
                      <button
                        onClick={() => toast.success(`${api.name} settings saved`)}
                        className="px-3 py-1.5 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50"
                      >
                        <Save size={16} className="inline mr-1" />
                        Save
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 relative">
                      <input
                        type={showApiKey[api.name] ? 'text' : 'password'}
                        defaultValue={api.key}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg text-sm font-mono"
                      />
                      <button
                        onClick={() => setShowApiKey(prev => ({ ...prev, [api.name]: !prev[api.name] }))}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showApiKey[api.name] ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>
                  {api.lastTested && (
                    <p className="text-xs text-gray-500 mt-2">Last tested: {api.lastTested}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Webhook Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Webhook URL</label>
                <div className="flex gap-2">
                  <input
                    type="url"
                    placeholder="https://your-domain.com/webhook"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() => toast.success('Webhook URL saved')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <Webhook size={18} />
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap gap-3">
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked className="rounded text-blue-600" />
                  <span className="text-sm text-gray-700">Trade Executions</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked className="rounded text-blue-600" />
                  <span className="text-sm text-gray-700">Alerts</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="rounded text-blue-600" />
                  <span className="text-sm text-gray-700">Daily Reports</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked className="rounded text-blue-600" />
                  <span className="text-sm text-gray-700">Errors</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agents Tab */}
      {activeTab === 'agents' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center gap-3 mb-2">
                <CheckCircle className="text-green-600" size={24} />
                <span className="text-sm text-gray-500">Active Agents</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {agentStatuses.filter(a => a.status === 'active').length}/8
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center gap-3 mb-2">
                <Cpu className="text-blue-600" size={24} />
                <span className="text-sm text-gray-500">Total Decisions</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {agentStatuses.reduce((s, a) => s + a.decisions, 0).toLocaleString()}
              </div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center gap-3 mb-2">
                <Lock className="text-amber-600" size={24} />
                <span className="text-sm text-gray-500">Pending Approvals</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">2</div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Autonomous Execution Settings</h3>
            </div>
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Enable Autonomous Execution</h4>
                  <p className="text-sm text-gray-500">Allow agents to execute trades without approval</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoExecute}
                    onChange={(e) => setAutoExecute(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              {autoExecute && (
                <div className="space-y-4">
                  <div className="p-4 border border-amber-200 bg-amber-50 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="text-amber-600 shrink-0 mt-0.5" size={20} />
                      <div>
                        <h4 className="font-semibold text-amber-900">Autonomy Guardrails</h4>
                        <p className="text-sm text-amber-700">
                          Even with autonomy enabled, the following limits apply for safety:
                        </p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Maximum Trade Size: £{maxTradeSize.toLocaleString()}
                    </label>
                    <input
                      type="range"
                      min="100"
                      max="50000"
                      step="100"
                      value={maxTradeSize}
                      onChange={(e) => setMaxTradeSize(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Daily Trade Limit
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                      <option>1 trade per day</option>
                      <option>3 trades per day</option>
                      <option selected>5 trades per day</option>
                      <option>10 trades per day</option>
                      <option>Unlimited</option>
                    </select>
                  </div>

                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={requireApproval}
                      onChange={(e) => setRequireApproval(e.target.checked)}
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm text-gray-700">Require approval for trades over £1,000</span>
                  </label>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Agent Status</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {agentStatuses.map((agent) => (
                <div key={agent.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                  <div className="flex items-center gap-4">
                    <div className={`w-2 h-2 rounded-full ${
                      agent.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'
                    }`} />
                    <div>
                      <div className="font-medium text-gray-900">{agent.name}</div>
                      <div className="text-sm text-gray-500">Last run: {agent.lastRun}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">{agent.decisions.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">decisions</div>
                    </div>
                    <button
                      onClick={() => toast.success(`${agent.name} restarted`)}
                      className="p-2 text-gray-400 hover:text-blue-600"
                    >
                      <RefreshCw size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Notification Preferences</h3>
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Channels</h4>
              <div className="space-y-3">
                <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Bell size={18} className="text-blue-600" />
                    </div>
                    <span className="font-medium text-gray-900">Email Notifications</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.email}
                    onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                </label>
                <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Smartphone size={18} className="text-green-600" />
                    </div>
                    <span className="font-medium text-gray-900">Telegram Bot</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.telegram}
                    onChange={(e) => setNotifications({ ...notifications, telegram: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                </label>
                <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <Globe size={18} className="text-purple-600" />
                    </div>
                    <span className="font-medium text-gray-900">Push Notifications</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.push}
                    onChange={(e) => setNotifications({ ...notifications, push: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                </label>
                <label className="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <Bell size={18} className="text-orange-600" />
                    </div>
                    <span className="font-medium text-gray-900">SMS Alerts</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.sms}
                    onChange={(e) => setNotifications({ ...notifications, sms: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                </label>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200">
              <h4 className="font-medium text-gray-900 mb-3">Event Types</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={notifications.trades}
                    onChange={(e) => setNotifications({ ...notifications, trades: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span className="text-gray-900">Trade Executions</span>
                </label>
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={notifications.alerts}
                    onChange={(e) => setNotifications({ ...notifications, alerts: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span className="text-gray-900">Price & Risk Alerts</span>
                </label>
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={notifications.reports}
                    onChange={(e) => setNotifications({ ...notifications, reports: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span className="text-gray-900">Daily/Weekly Reports</span>
                </label>
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={notifications.errors}
                    onChange={(e) => setNotifications({ ...notifications, errors: e.target.checked })}
                    className="w-5 h-5 text-blue-600 rounded"
                  />
                  <span className="text-gray-900">System Errors</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Two-Factor Authentication</h3>
            <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-3">
                <Shield className="text-green-600" size={24} />
                <div>
                  <div className="font-medium text-green-900">2FA Enabled</div>
                  <div className="text-sm text-green-700">Using authenticator app</div>
                </div>
              </div>
              <button
                onClick={() => toast.success('2FA settings opened')}
                className="px-3 py-1.5 text-sm text-green-700 border border-green-300 rounded-lg hover:bg-green-100"
              >
                Configure
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Management</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Current Session</div>
                  <div className="text-xs text-gray-500">Chrome on Windows • IP: 192.168.1.1</div>
                </div>
                <span className="text-xs text-green-600 font-medium">Active</span>
              </div>
              <button
                onClick={() => toast.success('All other sessions terminated')}
                className="w-full px-4 py-2 text-sm text-red-600 border border-red-300 rounded-lg hover:bg-red-50"
              >
                Sign Out All Other Sessions
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Password</h3>
            <div className="space-y-4">
              <input
                type="password"
                placeholder="Current password"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <input
                type="password"
                placeholder="New password"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <input
                type="password"
                placeholder="Confirm new password"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <button
                onClick={() => toast.success('Password updated successfully')}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Change Password
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Login History</h3>
            <div className="space-y-3">
              {[
                { time: 'Today, 09:30', device: 'Chrome on Windows', status: 'Success' },
                { time: 'Yesterday, 18:45', device: 'Safari on iPhone', status: 'Success' },
                { time: 'Jan 13, 14:20', device: 'Firefox on Mac', status: 'Success' }
              ].map((login, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{login.time}</div>
                    <div className="text-xs text-gray-500">{login.device}</div>
                  </div>
                  <span className="text-xs text-green-600 font-medium">{login.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Advanced Tab */}
      {activeTab === 'advanced' && (
        <div className="space-y-6">
          <div className="bg-red-50 border border-red-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-red-600 shrink-0 mt-0.5" size={20} />
              <div>
                <h3 className="font-semibold text-red-900">Advanced Settings</h3>
                <p className="text-sm text-red-700">
                  These settings are for advanced users. Incorrect configuration may affect system performance.
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Management</h3>
              <div className="space-y-3">
                <button
                  onClick={handleBackup}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <Download size={18} />
                  Export All Data
                </button>
                <button
                  onClick={() => toast.success('Import dialog opened')}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <Upload size={18} />
                  Import Data
                </button>
                <button
                  onClick={() => toast.success('Cache cleared successfully')}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  <Trash2 size={18} />
                  Clear Cache
                </button>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Parameters</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Data Retention (days)</label>
                  <input
                    type="number"
                    defaultValue={365}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Log Level</label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    <option>Error</option>
                    <option>Warning</option>
                    <option selected>Info</option>
                    <option>Debug</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price Refresh Interval (seconds)</label>
                  <input
                    type="number"
                    defaultValue={60}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Danger Zone</h3>
            <div className="space-y-3">
              <button
                onClick={() => {
                  if (confirm('Are you sure? This will reset all settings to default.')) {
                    toast.success('Settings reset to default');
                  }
                }}
                className="w-full px-4 py-3 text-amber-600 border border-amber-300 rounded-lg hover:bg-amber-50"
              >
                Reset All Settings to Default
              </button>
              <button
                onClick={() => {
                  if (confirm('WARNING: This will permanently delete all your data. This cannot be undone.')) {
                    toast.success('Data deletion initiated');
                  }
                }}
                className="w-full px-4 py-3 text-red-600 border border-red-300 rounded-lg hover:bg-red-50"
              >
                Delete All Data
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
