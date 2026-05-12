import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  BarChart3, 
  Play, 
  Settings, 
  Download, 
  Upload, 
  TrendingUp, 
  Target,
  Brain,
  Zap,
  RefreshCw,
  Plus,
  Trash2,
  Eye,
  Edit,
  Save,
  X,
  Check,
  AlertCircle,
  Clock,
  DollarSign,
  Percent,
  Activity
} from 'lucide-react';

interface Strategy {
  id: string;
  name: string;
  type: string;
  status: 'draft' | 'testing' | 'ready' | 'deployed';
  returns: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  lastTested: string;
  description: string;
  parameters: Record<string, any>;
}

interface BacktestResult {
  strategyId: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalValue: number;
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitFactor: number;
  volatility: number;
}

const QuantResearchPage: React.FC = () => {
  const { t } = useTranslation();
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showBacktestModal, setShowBacktestModal] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'strategies' | 'backtesting' | 'optimization'>('strategies');

  const strategies: Strategy[] = [
    {
      id: '1',
      name: 'Mean Reversion Strategy',
      type: 'Statistical Arbitrage',
      status: 'deployed',
      returns: 18.5,
      sharpeRatio: 1.45,
      maxDrawdown: -8.2,
      winRate: 62.3,
      profitFactor: 1.85,
      lastTested: '2024-01-20',
      description: 'Exploits short-term price reversals using statistical models',
      parameters: {
        lookbackPeriod: 20,
        entryThreshold: 2.0,
        exitThreshold: 0.5,
        positionSize: 0.1
      }
    },
    {
      id: '2',
      name: 'Momentum Factor Model',
      type: 'Factor Investing',
      status: 'testing',
      returns: 15.2,
      sharpeRatio: 1.23,
      maxDrawdown: -12.5,
      winRate: 58.7,
      profitFactor: 1.62,
      lastTested: '2024-01-18',
      description: 'Capitalizes on persistent price trends across multiple assets',
      parameters: {
        momentumPeriod: 12,
        rebalanceFrequency: 'monthly',
        universeSize: 100,
        riskWeighting: 'equal'
      }
    },
    {
      id: '3',
      name: 'Pairs Trading Algorithm',
      type: 'Market Neutral',
      status: 'ready',
      returns: 12.8,
      sharpeRatio: 1.67,
      maxDrawdown: -6.8,
      winRate: 65.4,
      profitFactor: 2.12,
      lastTested: '2024-01-15',
      description: 'Identifies and trades correlated securities pairs',
      parameters: {
        correlationThreshold: 0.8,
        lookbackPeriod: 252,
        zScoreEntry: 2.0,
        zScoreExit: 0.0
      }
    },
    {
      id: '4',
      name: 'Volatility Risk Premium',
      type: 'Options Strategy',
      status: 'draft',
      returns: 0,
      sharpeRatio: 0,
      maxDrawdown: 0,
      winRate: 0,
      profitFactor: 0,
      lastTested: 'Never',
      description: 'Harvests volatility risk premium through options selling',
      parameters: {
        deltaTarget: 0.3,
        daysToExpiry: 30,
        strikeOffset: 0.05,
        positionSize: 0.05
      }
    }
  ];

  const backtestResults: BacktestResult[] = [
    {
      strategyId: '1',
      startDate: '2023-01-01',
      endDate: '2024-01-20',
      initialCapital: 1000000,
      finalValue: 1185000,
      totalReturn: 18.5,
      annualizedReturn: 17.2,
      sharpeRatio: 1.45,
      maxDrawdown: -8.2,
      winRate: 62.3,
      profitFactor: 1.85,
      volatility: 12.8
    },
    {
      strategyId: '2',
      startDate: '2023-01-01',
      endDate: '2024-01-18',
      initialCapital: 1000000,
      finalValue: 1152000,
      totalReturn: 15.2,
      annualizedReturn: 14.3,
      sharpeRatio: 1.23,
      maxDrawdown: -12.5,
      winRate: 58.7,
      profitFactor: 1.62,
      volatility: 15.6
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed': return 'text-green-600 bg-green-100';
      case 'ready': return 'text-blue-600 bg-blue-100';
      case 'testing': return 'text-yellow-600 bg-yellow-100';
      case 'draft': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'deployed': return 'Deployed';
      case 'ready': return 'Ready';
      case 'testing': return 'Testing';
      case 'draft': return 'Draft';
      default: return 'Unknown';
    }
  };

  const handleTestStrategy = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setShowBacktestModal(true);
  };

  const handleDeployStrategy = (strategy: Strategy) => {
    console.log('Deploying strategy:', strategy.name);
    // Handle deployment logic
  };

  const handleDeleteStrategy = (strategy: Strategy) => {
    console.log('Deleting strategy:', strategy.name);
    // Handle deletion logic
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <BarChart3 className="w-8 h-8 mr-3 text-blue-600" />
          {t('quantResearch.title')}
        </h1>
        <p className="text-gray-600">{t('quantResearch.description')}</p>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('strategies')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'strategies'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {t('quantResearch.strategies')}
          </button>
          <button
            onClick={() => setActiveTab('backtesting')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'backtesting'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {t('quantResearch.backtesting')}
          </button>
          <button
            onClick={() => setActiveTab('optimization')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'optimization'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {t('quantResearch.optimization')}
          </button>
        </nav>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Strategies</p>
              <p className="text-2xl font-bold text-gray-900">{strategies.length}</p>
            </div>
            <Brain className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Deployed</p>
              <p className="text-2xl font-bold text-green-600">
                {strategies.filter(s => s.status === 'deployed').length}
              </p>
            </div>
            <Zap className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Returns</p>
              <p className="text-2xl font-bold text-blue-600">
                {(strategies.filter(s => s.returns > 0).reduce((acc, s) => acc + s.returns, 0) / 
                 strategies.filter(s => s.returns > 0).length).toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Sharpe</p>
              <p className="text-2xl font-bold text-purple-600">
                {(strategies.filter(s => s.sharpeRatio > 0).reduce((acc, s) => acc + s.sharpeRatio, 0) / 
                 strategies.filter(s => s.sharpeRatio > 0).length).toFixed(2)}
              </p>
            </div>
            <Target className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mb-8">
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center"
        >
          <Plus className="w-5 h-5 mr-2" />
          {t('quantResearch.createStrategy')}
        </button>
        <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200 flex items-center">
          <Upload className="w-5 h-5 mr-2" />
          Import Strategy
        </button>
        <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200 flex items-center">
          <Download className="w-5 h-5 mr-2" />
          {t('quantResearch.exportResults')}
        </button>
      </div>

      {/* Strategies Tab */}
      {activeTab === 'strategies' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {strategies.map(strategy => (
            <div key={strategy.id} className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{strategy.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{strategy.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center">
                      <Brain className="w-4 h-4 mr-1" />
                      {strategy.type}
                    </span>
                    <span className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      Last tested: {strategy.lastTested}
                    </span>
                  </div>
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(strategy.status)}`}>
                  {getStatusText(strategy.status)}
                </span>
              </div>

              {/* Performance Metrics */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-600">Returns</span>
                    <Percent className="w-3 h-3 text-green-500" />
                  </div>
                  <p className="text-lg font-semibold text-gray-900">{strategy.returns}%</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-600">Sharpe</span>
                    <Activity className="w-3 h-3 text-blue-500" />
                  </div>
                  <p className="text-lg font-semibold text-gray-900">{strategy.sharpeRatio}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-600">Win Rate</span>
                    <Target className="w-3 h-3 text-purple-500" />
                  </div>
                  <p className="text-lg font-semibold text-gray-900">{strategy.winRate}%</p>
                </div>
              </div>

              {/* Additional Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Max Drawdown</span>
                  <span className="text-sm font-medium text-red-600">{strategy.maxDrawdown}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Profit Factor</span>
                  <span className="text-sm font-medium text-green-600">{strategy.profitFactor}</span>
                </div>
              </div>

              {/* Parameters Preview */}
              <div className="bg-blue-50 rounded-lg p-3 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-900">Parameters</span>
                  <button className="text-blue-600 hover:text-blue-700">
                    <Edit className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-blue-800">
                  {Object.entries(strategy.parameters).slice(0, 4).map(([key, value]) => (
                    <div key={key}>
                      <span className="font-medium">{key}:</span> {value}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2">
                {strategy.status === 'draft' && (
                  <>
                    <button
                      onClick={() => handleTestStrategy(strategy)}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      {t('quantResearch.testStrategy')}
                    </button>
                    <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200">
                      <Edit className="w-4 h-4" />
                    </button>
                  </>
                )}
                {strategy.status === 'testing' && (
                  <button className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors duration-200 flex items-center justify-center">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Testing...
                  </button>
                )}
                {strategy.status === 'ready' && (
                  <>
                    <button
                      onClick={() => handleDeployStrategy(strategy)}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 flex items-center justify-center"
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      {t('quantResearch.deployStrategy')}
                    </button>
                    <button
                      onClick={() => handleTestStrategy(strategy)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  </>
                )}
                {strategy.status === 'deployed' && (
                  <>
                    <button className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg cursor-not-allowed">
                      Deployed
                    </button>
                    <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200">
                      <Settings className="w-4 h-4" />
                    </button>
                  </>
                )}
                <button
                  onClick={() => handleDeleteStrategy(strategy)}
                  className="px-4 py-2 bg-red-200 text-red-700 rounded-lg hover:bg-red-300 transition-colors duration-200"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Backtesting Tab */}
      {activeTab === 'backtesting' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Strategy
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Period
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Return
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sharpe Ratio
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Max Drawdown
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Win Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {backtestResults.map(result => {
                  const strategy = strategies.find(s => s.id === result.strategyId);
                  return (
                    <tr key={result.strategyId}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{strategy?.name}</div>
                        <div className="text-sm text-gray-500">{strategy?.type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{result.startDate}</div>
                        <div className="text-sm text-gray-500">to {result.endDate}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-green-600">{result.totalReturn}%</div>
                        <div className="text-sm text-gray-500">{result.annualizedReturn}% annualized</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-blue-600">{result.sharpeRatio}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-red-600">{result.maxDrawdown}%</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-purple-600">{result.winRate}%</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button className="text-blue-600 hover:text-blue-900 mr-3">View</button>
                        <button className="text-blue-600 hover:text-blue-900">Export</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Optimization Tab */}
      {activeTab === 'optimization' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-12">
            <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Portfolio Optimization</h3>
            <p className="text-gray-600 mb-6">
              Advanced optimization tools for portfolio construction and risk management
            </p>
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200">
              Launch Optimizer
            </button>
          </div>
        </div>
      )}

      {/* Create Strategy Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('quantResearch.createStrategy')}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Strategy Name</label>
                <input
                  type="text"
                  placeholder="Enter strategy name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Strategy Type</label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>Statistical Arbitrage</option>
                  <option>Factor Investing</option>
                  <option>Market Neutral</option>
                  <option>Options Strategy</option>
                  <option>Momentum</option>
                  <option>Mean Reversion</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  placeholder="Describe your strategy..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Initial Parameters</label>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Parameter name"
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Parameter value"
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Create Strategy
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Backtest Modal */}
      {showBacktestModal && selectedStrategy && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Backtest: {selectedStrategy.name}
            </h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                  <input
                    type="date"
                    defaultValue="2023-01-01"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <input
                    type="date"
                    defaultValue="2024-01-20"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Initial Capital</label>
                <input
                  type="number"
                  defaultValue="1000000"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Benchmark</label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>S&P 500</option>
                  <option>NASDAQ</option>
                  <option>MSCI World</option>
                  <option>No Benchmark</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => {
                  console.log('Running backtest for:', selectedStrategy.name);
                  setShowBacktestModal(false);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Run Backtest
              </button>
              <button
                onClick={() => {
                  setShowBacktestModal(false);
                  setSelectedStrategy(null);
                }}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuantResearchPage;
