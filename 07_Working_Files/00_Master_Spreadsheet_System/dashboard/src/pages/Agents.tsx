import React, { useState } from 'react';
import { 
  Bot, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Play, 
  Pause, 
  Settings,
  FileText,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'paused' | 'error';
  lastRun: string;
  totalDecisions: number;
  pendingDecisions: number;
  description: string;
  responsibilities: string[];
}

const agents: Agent[] = [
  {
    id: 'accountant',
    name: 'AI Accountant',
    type: 'Tax & Compliance',
    status: 'active',
    lastRun: '2 minutes ago',
    totalDecisions: 47,
    pendingDecisions: 2,
    description: 'Tax optimization, CGT tracking, ISA allowance monitoring',
    responsibilities: [
      'Monitor CGT allowance utilization',
      'Track ISA contribution limits',
      'Identify tax-loss harvesting opportunities',
      'Project dividend tax liability',
      'Self Assessment deadline monitoring'
    ]
  },
  {
    id: 'lawyer',
    name: 'AI Lawyer',
    type: 'Legal & Regulatory',
    status: 'active',
    lastRun: '6 minutes ago',
    totalDecisions: 12,
    pendingDecisions: 0,
    description: 'FCA compliance, regulatory monitoring, platform verification',
    responsibilities: [
      'Verify platform FCA registrations',
      'Monitor regulatory changes (CARF, MiCA)',
      'Check platform Terms of Service changes',
      'Assess jurisdiction exposure risks',
      'Compliance documentation tracking'
    ]
  },
  {
    id: 'governance',
    name: 'AI Governance',
    type: 'Policy Enforcement',
    status: 'active',
    lastRun: '15 minutes ago',
    totalDecisions: 89,
    pendingDecisions: 1,
    description: 'Policy enforcement, audit trails, quorum decisions',
    responsibilities: [
      'Check policy violations',
      'Verify audit trail integrity',
      'Review quorum-based decisions',
      'Enforce max trade size limits',
      'Monitor daily trade limits'
    ]
  },
  {
    id: 'regulations',
    name: 'AI Regulations',
    type: 'HMRC & Global',
    status: 'active',
    lastRun: '1 hour ago',
    totalDecisions: 23,
    pendingDecisions: 0,
    description: 'HMRC compliance, CARF readiness, global tax monitoring',
    responsibilities: [
      'Monitor HMRC guidance updates',
      'Track CARF implementation timeline',
      'Assess MiCA impact on holdings',
      'Verify tax reporting readiness',
      'Cross-border tax optimization'
    ]
  },
  {
    id: 'protocols',
    name: 'AI Protocols',
    type: 'DeFi Risk',
    status: 'active',
    lastRun: '4 hours ago',
    totalDecisions: 8,
    pendingDecisions: 0,
    description: 'DeFi protocol risk assessment, yield optimization',
    responsibilities: [
      'Assess DeFi protocol risks',
      'Monitor audit reports',
      'Track yield opportunities',
      'Analyze TVL changes',
      'Detect protocol exploits'
    ]
  },
  {
    id: 'security',
    name: 'AI Cyber Security',
    type: 'Security',
    status: 'warning',
    lastRun: '23 minutes ago',
    totalDecisions: 156,
    pendingDecisions: 1,
    description: 'API security, wallet monitoring, fraud detection',
    responsibilities: [
      'Check API key permissions',
      'Detect suspicious transactions',
      'Monitor wallet security',
      'Recommend multi-sig wallets',
      'Fraud pattern detection'
    ]
  },
  {
    id: 'blockchain',
    name: 'AI Blockchain',
    type: 'On-Chain',
    status: 'active',
    lastRun: '45 minutes ago',
    totalDecisions: 34,
    pendingDecisions: 0,
    description: 'Gas optimization, network monitoring, MEV protection',
    responsibilities: [
      'Monitor gas prices',
      'Check network congestion',
      'Analyze MEV exposure',
      'Recommend transaction timing',
      'Cross-chain bridge monitoring'
    ]
  },
  {
    id: 'analyst',
    name: 'AI Analyst',
    type: 'Market Intelligence',
    status: 'active',
    lastRun: '1.5 hours ago',
    totalDecisions: 67,
    pendingDecisions: 1,
    description: 'Market research, portfolio correlation, sentiment analysis',
    responsibilities: [
      'Identify market opportunities',
      'Check portfolio correlations',
      'Analyze market sentiment',
      'Monitor macro conditions',
      'Rebalancing recommendations'
    ]
  }
];

const pendingDecisions = [
  {
    id: '7a3f9b2c',
    agent: 'AI Cyber Security',
    title: 'API Security Check',
    priority: 'critical',
    description: 'Binance API has withdrawal permissions enabled. This is a security risk. Recommend disabling.',
    recommendedAction: 'Revoke withdrawal permissions for Binance API key',
    confidence: 0.95,
    autoExecutable: false,
    createdAt: '2 hours ago'
  },
  {
    id: 'b8c2d4e6',
    agent: 'AI Accountant',
    title: 'CGT Optimization',
    priority: 'high',
    description: '£2,100 CGT allowance remaining with 45 days to year-end. Consider crystallizing gains.',
    recommendedAction: 'Sell £1,200 BTC, buy back immediately (bed & breakfast)',
    confidence: 0.87,
    autoExecutable: false,
    createdAt: '4 hours ago'
  },
  {
    id: 'a1d5f7e9',
    agent: 'AI Analyst',
    title: 'Portfolio Rebalance',
    priority: 'medium',
    description: 'BTC allocation at 40% (target 35%). ETH at 7% (target 10%). Drift exceeds 5% threshold.',
    recommendedAction: 'Sell £262 BTC, buy £157 ETH + £105 VWRP',
    confidence: 0.78,
    autoExecutable: true,
    createdAt: '6 hours ago'
  }
];

const Agents: React.FC = () => {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'decisions' | 'logs'>('overview');

  const toggleAgent = (id: string) => {
    setExpandedAgent(expandedAgent === id ? null : id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400';
      case 'paused': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'error': return 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400';
      default: return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-700 border-red-300 dark:bg-red-900/20 dark:text-red-400';
      case 'high': return 'bg-orange-100 text-orange-700 border-orange-300 dark:bg-orange-900/20 dark:text-orange-400';
      case 'medium': return 'bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-900/20 dark:text-blue-400';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">AI Agents</h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Multi-agent system orchestrating your financial operations
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center text-sm text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-3 py-1.5 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
            8/8 Agents Online
          </div>
          <button className="flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700">
            <Play className="w-4 h-4 mr-1.5" />
            Run Cycle
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Decisions</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">436</p>
          <p className="mt-1 text-xs text-green-600">+12 today</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pending Approval</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">4</p>
          <p className="mt-1 text-xs text-orange-600">3 require manual</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Auto-Executed</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">89%</p>
          <p className="mt-1 text-xs text-gray-500">391 decisions</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">System Uptime</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">99.7%</p>
          <p className="mt-1 text-xs text-gray-500">Last 30 days</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8">
          {['overview', 'decisions', 'logs'].map((tab) => (
            <button
              key={tab}
              onClick={() => setSelectedTab(tab as any)}
              className={`py-4 px-1 text-sm font-medium border-b-2 transition-colors ${
                selectedTab === tab
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {selectedTab === 'overview' && (
        <div className="space-y-4">
          {agents.map((agent) => (
            <div 
              key={agent.id} 
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div 
                className="p-6 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                onClick={() => toggleAgent(agent.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`p-3 rounded-lg ${
                      agent.status === 'active' ? 'bg-green-50 dark:bg-green-900/20' :
                      agent.status === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20' :
                      'bg-gray-50 dark:bg-gray-700'
                    }`}>
                      <Bot className={`w-6 h-6 ${
                        agent.status === 'active' ? 'text-green-600 dark:text-green-400' :
                        agent.status === 'warning' ? 'text-yellow-600 dark:text-yellow-400' :
                        'text-gray-600'
                      }`} />
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
                        <span className={`ml-3 px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                          {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{agent.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{agent.totalDecisions}</p>
                      <p className="text-xs text-gray-500">decisions</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{agent.pendingDecisions}</p>
                      <p className="text-xs text-gray-500">pending</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{agent.lastRun}</p>
                      <p className="text-xs text-gray-500">last run</p>
                    </div>
                    {expandedAgent === agent.id ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                </div>
              </div>
              
              {expandedAgent === agent.id && (
                <div className="px-6 pb-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/30">
                  <div className="pt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Responsibilities</h4>
                      <ul className="space-y-2">
                        {agent.responsibilities.map((resp, idx) => (
                          <li key={idx} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                            <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                            {resp}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Configuration</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Check Interval:</span>
                            <span className="text-gray-900 dark:text-white">15 minutes</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Auto-execute:</span>
                            <span className="text-green-600">Enabled (Low risk)</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Confidence Threshold:</span>
                            <span className="text-gray-900 dark:text-white">75%</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-3">
                        <button className="flex-1 flex items-center justify-center px-3 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50">
                          <Settings className="w-4 h-4 mr-2" />
                          Configure
                        </button>
                        <button className="flex-1 flex items-center justify-center px-3 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50">
                          <FileText className="w-4 h-4 mr-2" />
                          View Logs
                        </button>
                        {agent.status === 'active' ? (
                          <button className="flex-1 flex items-center justify-center px-3 py-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 rounded-lg text-sm font-medium text-yellow-700 hover:bg-yellow-100">
                            <Pause className="w-4 h-4 mr-2" />
                            Pause
                          </button>
                        ) : (
                          <button className="flex-1 flex items-center justify-center px-3 py-2 bg-green-50 dark:bg-green-900/20 border border-green-300 rounded-lg text-sm font-medium text-green-700 hover:bg-green-100">
                            <Play className="w-4 h-4 mr-2" />
                            Resume
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedTab === 'decisions' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Pending Decisions</h3>
            <button className="text-sm text-blue-600 hover:underline">View History</button>
          </div>
          
          {pendingDecisions.map((decision) => (
            <div 
              key={decision.id} 
              className={`bg-white dark:bg-gray-800 rounded-xl p-6 border-2 ${getPriorityColor(decision.priority)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                      decision.priority === 'critical' ? 'bg-red-600 text-white' :
                      decision.priority === 'high' ? 'bg-orange-500 text-white' :
                      'bg-blue-500 text-white'
                    }`}>
                      {decision.priority}
                    </span>
                    <span className="ml-3 text-sm text-gray-500">{decision.agent}</span>
                    <span className="ml-3 text-sm text-gray-500">{decision.createdAt}</span>
                  </div>
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{decision.title}</h4>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">{decision.description}</p>
                  
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4">
                    <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">Recommended Action:</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{decision.recommendedAction}</p>
                  </div>
                  
                  <div className="flex items-center space-x-6 text-sm">
                    <div>
                      <span className="text-gray-500">Confidence:</span>
                      <span className="ml-1 font-medium text-gray-900 dark:text-white">{(decision.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Auto-executable:</span>
                      <span className={`ml-1 font-medium ${decision.autoExecutable ? 'text-green-600' : 'text-yellow-600'}`}>
                        {decision.autoExecutable ? 'Yes' : 'No (requires approval)'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="ml-6 flex flex-col space-y-2">
                  <button className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700">
                    Approve
                  </button>
                  <button className="px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-500 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg hover:bg-gray-50">
                    Reject
                  </button>
                  <button className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">
                    Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedTab === 'logs' && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Agent Activity Logs</h3>
            <div className="flex items-center space-x-2">
              <select className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700">
                <option>All Agents</option>
                <option>AI Accountant</option>
                <option>AI Analyst</option>
                <option>AI Security</option>
              </select>
              <button className="text-sm text-blue-600 hover:underline">Export</button>
            </div>
          </div>
          
          <div className="space-y-2 font-mono text-sm">
            <div className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
              <span className="text-gray-400">[09:15:23]</span>
              <span className="text-green-600">AI Accountant</span>
              <span className="text-gray-600 dark:text-gray-400">CGT analysis complete. 0 opportunities found.</span>
            </div>
            <div className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
              <span className="text-gray-400">[09:15:45]</span>
              <span className="text-blue-600">AI Analyst</span>
              <span className="text-gray-600 dark:text-gray-400">Portfolio drift check: BTC +5%, ETH -3%</span>
            </div>
            <div className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
              <span className="text-gray-400">[09:16:12]</span>
              <span className="text-yellow-600">AI Security</span>
              <span className="text-gray-600 dark:text-gray-400">⚠️ API permission check: Binance withdrawal enabled</span>
            </div>
            <div className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
              <span className="text-gray-400">[09:17:00]</span>
              <span className="text-green-600">AI Governance</span>
              <span className="text-gray-600 dark:text-gray-400">Policy check: All limits within bounds</span>
            </div>
            <div className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
              <span className="text-gray-400">[09:18:34]</span>
              <span className="text-purple-600">AI Regulations</span>
              <span className="text-gray-600 dark:text-gray-400">CARF monitoring: 255 days until implementation</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Agents;
