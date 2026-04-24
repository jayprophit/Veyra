import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  PieChart, 
  Bot, 
  AlertTriangle,
  Clock,
  CheckCircle,
  DollarSign,
  Percent
} from 'lucide-react';
import { 
  PieChart as RePieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area
} from 'recharts';

// Mock data - In production, this comes from your Python backend API
const portfolioData = [
  { name: 'BTC', value: 1836, percentage: 35, color: '#F7931A' },
  { name: 'VWRP', value: 1312, percentage: 25, color: '#3B82F6' },
  { name: 'LISA', value: 1050, percentage: 20, color: '#10B981' },
  { name: 'ETH', value: 525, percentage: 10, color: '#627EEA' },
  { name: 'GOLD', value: 525, percentage: 10, color: '#F59E0B' },
];

const netWorthHistory = [
  { date: 'Jan', value: 4200 },
  { date: 'Feb', value: 4450 },
  { date: 'Mar', value: 4300 },
  { date: 'Apr', value: 4890 },
  { date: 'May', value: 5120 },
  { date: 'Jun', value: 5248 },
];

const recentAlerts = [
  { 
    id: 1, 
    type: 'warning', 
    title: 'CGT Allowance', 
    message: '£2,100 remaining. 45 days to year-end.',
    time: '2 hours ago',
    agent: 'AI Accountant'
  },
  { 
    id: 2, 
    type: 'info', 
    title: 'ISA Opportunity', 
    message: '£18,500 allowance remaining. Need £1,542/month.',
    time: '4 hours ago',
    agent: 'AI Accountant'
  },
  { 
    id: 3, 
    type: 'success', 
    title: 'Rebalance Complete', 
    message: 'Sold £50 BTC, bought £30 ETH + £20 VWRP',
    time: '1 day ago',
    agent: 'AI Analyst'
  },
];

const agentStatus = [
  { name: 'AI Accountant', status: 'active', lastRun: '2 min ago', decisions: 47 },
  { name: 'AI Lawyer', status: 'active', lastRun: '6 min ago', decisions: 12 },
  { name: 'AI Governance', status: 'active', lastRun: '15 min ago', decisions: 89 },
  { name: 'AI Regulations', status: 'active', lastRun: '1 hour ago', decisions: 23 },
  { name: 'AI Cyber Security', status: 'warning', lastRun: '23 min ago', decisions: 156 },
  { name: 'AI Analyst', status: 'active', lastRun: '45 min ago', decisions: 67 },
];

const Dashboard: React.FC = () => {
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isLive, setIsLive] = useState(true);

  // Simulate real-time updates
  useEffect(() => {
    if (!isLive) return;
    
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 15000); // Update every 15 seconds

    return () => clearInterval(interval);
  }, [isLive]);

  const StatCard = ({ 
    title, 
    value, 
    change, 
    changeType, 
    icon: Icon,
    subtext 
  }: { 
    title: string; 
    value: string; 
    change: string; 
    changeType: 'positive' | 'negative' | 'neutral';
    icon: any;
    subtext?: string;
  }) => (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
          <div className="mt-2 flex items-center">
            {changeType === 'positive' ? (
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
            ) : changeType === 'negative' ? (
              <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
            ) : null}
            <span className={`text-sm font-medium ${
              changeType === 'positive' ? 'text-green-600' : 
              changeType === 'negative' ? 'text-red-600' : 
              'text-gray-600'
            }`}>
              {change}
            </span>
          </div>
          {subtext && (
            <p className="mt-1 text-xs text-gray-500">{subtext}</p>
          )}
        </div>
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <Icon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Real-time overview of your financial master system
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center text-sm text-gray-500">
            <div className={`w-2 h-2 rounded-full mr-2 ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
            Last update: {lastUpdate.toLocaleTimeString()}
          </div>
          <button 
            onClick={() => setIsLive(!isLive)}
            className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              isLive 
                ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400' 
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
            }`}
          >
            {isLive ? '● Live' : '○ Paused'}
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Net Worth"
          value="£5,247.83"
          change="+£127.42 (+2.49%)"
          changeType="positive"
          icon={Wallet}
          subtext="vs last month"
        />
        <StatCard
          title="24h Change"
          value="+£127.42"
          change="+2.49%"
          changeType="positive"
          icon={TrendingUp}
          subtext="£4,200 → £5,247"
        />
        <StatCard
          title="Active Agents"
          value="8/8"
          change="All systems operational"
          changeType="neutral"
          icon={Bot}
          subtext="23 decisions today"
        />
        <StatCard
          title="CGT Allowance"
          value="£3,000"
          change="100% remaining"
          changeType="positive"
          icon={Percent}
          subtext="45 days to year-end"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio Allocation */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Portfolio Allocation
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie
                  data={portfolioData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {portfolioData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => `£${value.toLocaleString()}`}
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                />
              </RePieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {portfolioData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 rounded-full mr-2" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-gray-700 dark:text-gray-300">{item.name}</span>
                </div>
                <div className="text-gray-900 dark:text-white font-medium">
                  {item.percentage}% (£{item.value.toLocaleString()})
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Net Worth History */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Net Worth History
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={netWorthHistory}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                  formatter={(value: number) => `£${value.toLocaleString()}`}
                />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3B82F6" 
                  fillOpacity={1} 
                  fill="url(#colorValue)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>6-month trend: +24.9%</span>
            <span>Projected year-end: £6,200</span>
          </div>
        </div>
      </div>

      {/* Bottom Row: Alerts & Agents */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Recent Alerts
            </h3>
            <span className="text-sm text-blue-600 dark:text-blue-400 cursor-pointer hover:underline">
              View all
            </span>
          </div>
          <div className="space-y-4">
            {recentAlerts.map((alert) => (
              <div 
                key={alert.id} 
                className={`p-4 rounded-lg border-l-4 ${
                  alert.type === 'warning' ? 'bg-yellow-50 border-yellow-400 dark:bg-yellow-900/10' :
                  alert.type === 'success' ? 'bg-green-50 border-green-400 dark:bg-green-900/10' :
                  'bg-blue-50 border-blue-400 dark:bg-blue-900/10'
                }`}
              >
                <div className="flex items-start">
                  {alert.type === 'warning' ? (
                    <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-3 flex-shrink-0" />
                  ) : alert.type === 'success' ? (
                    <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-3 flex-shrink-0" />
                  ) : (
                    <DollarSign className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-gray-900 dark:text-white">{alert.title}</p>
                      <span className="text-xs text-gray-500">{alert.time}</span>
                    </div>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{alert.message}</p>
                    <p className="mt-2 text-xs text-gray-500">via {alert.agent}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Agent Status */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Agent Status
            </h3>
            <div className="flex items-center text-sm text-green-600 dark:text-green-400">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
              8/8 Online
            </div>
          </div>
          <div className="space-y-3">
            {agentStatus.map((agent) => (
              <div 
                key={agent.name} 
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
              >
                <div className="flex items-center">
                  <Bot className={`w-5 h-5 mr-3 ${
                    agent.status === 'active' ? 'text-green-500' : 
                    agent.status === 'warning' ? 'text-yellow-500' : 
                    'text-red-500'
                  }`} />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white text-sm">{agent.name}</p>
                    <p className="text-xs text-gray-500">{agent.lastRun} • {agent.decisions} decisions</p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  agent.status === 'active' ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400' :
                  agent.status === 'warning' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400' :
                  'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
                }`}>
                  {agent.status === 'active' ? 'Active' : agent.status === 'warning' ? 'Warning' : 'Error'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Phase Progress */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Phase Progress: 3 → 4
          </h3>
          <span className="text-sm text-gray-600 dark:text-gray-400">67% Complete</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mb-4">
          <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '67%' }}></div>
        </div>
        <div className="grid grid-cols-5 gap-4 text-center text-sm">
          {['Phase 1\nFoundation', 'Phase 2\nLaunch', 'Phase 3\nExpansion ✓', 'Phase 4\nScaling', 'Phase 5\nEmpire'].map((phase, idx) => (
            <div key={idx} className={`p-2 rounded-lg ${
              idx < 2 ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400' :
              idx === 2 ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 border-2 border-blue-500' :
              'bg-gray-50 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
            }`}>
              {phase.split('\n').map((line, i) => (
                <div key={i} className={i === 0 ? 'font-medium' : 'text-xs'}>{line}</div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
