import { useState, useEffect } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';
import toast from 'react-hot-toast';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  RefreshCw,
  Plus,
  Edit3,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Building2,
  Bitcoin,
  Coins,
  Landmark
} from 'lucide-react';

interface Asset {
  id: string;
  symbol: string;
  name: string;
  type: 'stock' | 'crypto' | 'bond' | 'cash' | 'etf' | 'reit';
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  value: number;
  pl: number;
  plPercent: number;
  allocation: number;
  targetAllocation: number;
  drift: number;
  lastUpdated: string;
}

interface SectorAllocation {
  name: string;
  value: number;
  target: number;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#6366F1'];

const TYPE_ICONS = {
  stock: Building2,
  crypto: Bitcoin,
  bond: Landmark,
  cash: DollarSign,
  etf: Coins,
  reit: Building2
};

const TYPE_COLORS = {
  stock: 'bg-blue-100 text-blue-800',
  crypto: 'bg-orange-100 text-orange-800',
  bond: 'bg-green-100 text-green-800',
  cash: 'bg-gray-100 text-gray-800',
  etf: 'bg-purple-100 text-purple-800',
  reit: 'bg-pink-100 text-pink-800'
};

const mockAssets: Asset[] = [
  { id: '1', symbol: 'VWRL', name: 'Vanguard FTSE All-World', type: 'etf', quantity: 450, avgPrice: 95.5, currentPrice: 102.3, value: 46035, pl: 3060, plPercent: 7.12, allocation: 35, targetAllocation: 40, drift: -5, lastUpdated: '2024-01-15 14:30' },
  { id: '2', symbol: 'VUKE', name: 'Vanguard FTSE 100', type: 'etf', quantity: 800, avgPrice: 32.4, currentPrice: 35.1, value: 28080, pl: 2160, plPercent: 8.33, allocation: 21, targetAllocation: 20, drift: 1, lastUpdated: '2024-01-15 14:30' },
  { id: '3', symbol: 'BTC', name: 'Bitcoin', type: 'crypto', quantity: 0.5, avgPrice: 38000, currentPrice: 42500, value: 21250, pl: 2250, plPercent: 11.84, allocation: 16, targetAllocation: 10, drift: 6, lastUpdated: '2024-01-15 14:30' },
  { id: '4', symbol: 'ETH', name: 'Ethereum', type: 'crypto', quantity: 4, avgPrice: 2100, currentPrice: 2550, value: 10200, pl: 1800, plPercent: 21.43, allocation: 8, targetAllocation: 5, drift: 3, lastUpdated: '2024-01-15 14:30' },
  { id: '5', symbol: 'VUKG', name: 'Vanguard UK Gilt', type: 'bond', quantity: 500, avgPrice: 21.5, currentPrice: 20.8, value: 10400, pl: -350, plPercent: -3.26, allocation: 8, targetAllocation: 15, drift: -7, lastUpdated: '2024-01-15 14:30' },
  { id: '6', symbol: 'CASH', name: 'Cash Reserves', type: 'cash', quantity: 1, avgPrice: 8000, currentPrice: 8000, value: 8000, pl: 0, plPercent: 0, allocation: 6, targetAllocation: 5, drift: 1, lastUpdated: '2024-01-15 14:30' },
  { id: '7', symbol: 'VAPX', name: 'Vanguard Property', type: 'reit', quantity: 100, avgPrice: 42.3, currentPrice: 44.5, value: 4450, pl: 220, plPercent: 5.20, allocation: 3, targetAllocation: 3, drift: 0, lastUpdated: '2024-01-15 14:30' },
  { id: '8', symbol: 'AAPL', name: 'Apple Inc', type: 'stock', quantity: 15, avgPrice: 175, currentPrice: 185.5, value: 2782, pl: 157.5, plPercent: 6.00, allocation: 2, targetAllocation: 2, drift: 0, lastUpdated: '2024-01-15 14:30' }
];

const mockSectorData: SectorAllocation[] = [
  { name: 'Global Equities', value: 35, target: 40 },
  { name: 'UK Equities', value: 21, target: 20 },
  { name: 'Cryptocurrency', value: 24, target: 15 },
  { name: 'Fixed Income', value: 8, target: 15 },
  { name: 'Cash', value: 6, target: 5 },
  { name: 'Real Estate', value: 3, target: 3 },
  { name: 'US Tech', value: 2, target: 2 }
];

const mockPerformanceData = [
  { month: 'Jul', portfolio: 100000, benchmark: 100000 },
  { month: 'Aug', portfolio: 102500, benchmark: 101200 },
  { month: 'Sep', portfolio: 104200, benchmark: 102100 },
  { month: 'Oct', portfolio: 108500, benchmark: 103500 },
  { month: 'Nov', portfolio: 112000, benchmark: 104800 },
  { month: 'Dec', portfolio: 115000, benchmark: 105200 },
  { month: 'Jan', portfolio: 130965, benchmark: 106500 }
];

export default function Portfolio() {
  const [assets, setAssets] = useState<Asset[]>(mockAssets);
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('value');
  const [showRebalanceModal, setShowRebalanceModal] = useState(false);

  const totalValue = assets.reduce((sum, a) => sum + a.value, 0);
  const totalPL = assets.reduce((sum, a) => sum + a.pl, 0);
  const totalPLPercent = (totalPL / (totalValue - totalPL)) * 100;
  const needsRebalance = assets.filter(a => Math.abs(a.drift) > 5).length;

  const filteredAssets = filter === 'all'
    ? assets
    : assets.filter(a => a.type === filter);

  const sortedAssets = [...filteredAssets].sort((a, b) => {
    switch (sortBy) {
      case 'value': return b.value - a.value;
      case 'pl': return b.pl - a.pl;
      case 'plPercent': return b.plPercent - a.plPercent;
      case 'drift': return Math.abs(b.drift) - Math.abs(a.drift);
      default: return 0;
    }
  });

  const handleRefresh = () => {
    toast.loading('Refreshing prices...', { duration: 1500 });
    setTimeout(() => {
      setAssets(prev => prev.map(a => ({
        ...a,
        currentPrice: a.currentPrice * (1 + (Math.random() - 0.5) * 0.02),
        lastUpdated: new Date().toLocaleString()
      })));
      toast.success('Prices updated');
    }, 1500);
  };

  const pieData = assets.map(a => ({ name: a.symbol, value: a.value }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
          <p className="text-sm text-gray-500 mt-1">Real-time holdings & allocation analysis</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw size={18} />
            Refresh
          </button>
          <button
            onClick={() => setShowRebalanceModal(true)}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100"
          >
            <RefreshCw size={18} />
            Rebalance
          </button>
          <button
            onClick={() => toast.success('Add asset feature - integrate with Agent 5')}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} />
            Add Asset
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Wallet className="text-blue-600" size={24} />
            <span className="text-sm text-gray-500">Total Value</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            £{totalValue.toLocaleString()}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-green-600" size={24} />
            <span className="text-sm text-gray-500">Total P&L</span>
          </div>
          <div className={`text-2xl font-bold ${totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {totalPL >= 0 ? '+' : ''}£{totalPL.toLocaleString()}
          </div>
          <div className={`text-sm ${totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {totalPLPercent >= 0 ? '+' : ''}{totalPLPercent.toFixed(2)}%
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="text-amber-600" size={24} />
            <span className="text-sm text-gray-500">Rebalance Needed</span>
          </div>
          <div className={`text-2xl font-bold ${needsRebalance > 0 ? 'text-amber-600' : 'text-green-600'}`}>
            {needsRebalance}
          </div>
          <div className="text-sm text-gray-500">assets out of target</div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="text-purple-600" size={24} />
            <span className="text-sm text-gray-500">Holdings</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {assets.length}
          </div>
          <div className="text-sm text-gray-500">across {new Set(assets.map(a => a.type)).size} asset types</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Allocation Pie */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Allocation</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `£${value.toLocaleString()}`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Sector vs Target */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sector vs Target</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={mockSectorData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 50]} tickFormatter={(v) => `${v}%`} />
              <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value: number) => `${value}%`} />
              <Legend />
              <Bar dataKey="value" name="Current %" fill="#3B82F6" />
              <Bar dataKey="target" name="Target %" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Performance vs Benchmark */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance vs Benchmark</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={mockPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis tickFormatter={(v) => `£${v / 1000}k`} />
              <Tooltip formatter={(value: number) => `£${value.toLocaleString()}`} />
              <Legend />
              <Line type="monotone" dataKey="portfolio" name="Portfolio" stroke="#3B82F6" strokeWidth={2} />
              <Line type="monotone" dataKey="benchmark" name="FTSE All-Share" stroke="#9CA3AF" strokeWidth={2} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex flex-wrap gap-4 justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Holdings</h3>
          <div className="flex gap-3">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="all">All Types</option>
              <option value="stock">Stocks</option>
              <option value="crypto">Crypto</option>
              <option value="bond">Bonds</option>
              <option value="cash">Cash</option>
              <option value="etf">ETFs</option>
              <option value="reit">REITs</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="value">Sort by Value</option>
              <option value="pl">Sort by P&L</option>
              <option value="plPercent">Sort by P&L %</option>
              <option value="drift">Sort by Drift</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Price</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Current</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Value</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">P&L</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Alloc %</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Drift</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sortedAssets.map((asset) => {
                const Icon = TYPE_ICONS[asset.type];
                return (
                  <tr key={asset.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${TYPE_COLORS[asset.type]}`}>
                          <Icon size={16} />
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{asset.symbol}</div>
                          <div className="text-xs text-gray-500">{asset.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${TYPE_COLORS[asset.type]}`}>
                        {asset.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">
                      {asset.quantity.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-500">
                      £{asset.avgPrice.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">
                      £{asset.currentPrice.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-sm font-medium text-gray-900">
                      £{asset.value.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className={`text-sm font-medium ${asset.pl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {asset.pl >= 0 ? '+' : ''}£{asset.pl.toLocaleString()}
                      </div>
                      <div className={`text-xs ${asset.pl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {asset.pl >= 0 ? <ArrowUpRight size={12} className="inline" /> : <ArrowDownRight size={12} className="inline" />}
                        {Math.abs(asset.plPercent).toFixed(2)}%
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-gray-900">
                      {asset.allocation}%
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className={`text-sm font-medium ${Math.abs(asset.drift) > 5 ? 'text-red-600' : 'text-green-600'}`}>
                        {asset.drift > 0 ? '+' : ''}{asset.drift}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => toast.success(`Edit ${asset.symbol} - integrate with Agent 5`)}
                        className="p-1 text-gray-400 hover:text-blue-600"
                      >
                        <Edit3 size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Rebalance Modal */}
      {showRebalanceModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Rebalance Recommendations</h2>
            <p className="text-gray-600 mb-4">
              The following rebalancing trades are recommended to align with your target allocations:
            </p>
            <div className="space-y-3 mb-6">
              {assets.filter(a => Math.abs(a.drift) > 2).map(asset => (
                <div key={asset.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{asset.symbol}</span>
                    <span className={`text-sm ${asset.drift > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {asset.drift > 0 ? 'Overweight' : 'Underweight'} by {Math.abs(asset.drift)}%
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {asset.drift > 0 ? 'SELL' : 'BUY'} ~£{Math.abs(asset.value * (asset.drift / 100)).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowRebalanceModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  toast.success('Rebalancing request sent to Agent 5 (Portfolio Manager)');
                  setShowRebalanceModal(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Execute Rebalance
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
