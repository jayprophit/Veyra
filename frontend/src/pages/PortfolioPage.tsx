import React from 'react';
import { useQuery } from 'react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import { api } from '../services/api';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export const PortfolioPage: React.FC = () => {
  const { data: portfolio, isLoading } = useQuery('portfolio', () =>
    api.get('/portfolio').then((res) => res.data)
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  const portfolioData = portfolio || {
    total_value: 100000,
    day_pnl: 500,
    positions: []
  };

  // Mock chart data
  const performanceData = [
    { date: '2026-01-01', value: 95000 },
    { date: '2026-01-05', value: 96500 },
    { date: '2026-01-10', value: 98000 },
    { date: '2026-01-15', value: 100000 },
  ];

  const allocationData = portfolioData.positions.map((pos: any, idx: number) => ({
    name: pos.symbol,
    value: pos.market_value,
    color: COLORS[idx % COLORS.length]
  })) || [];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <SummaryCard
          title="Total Value"
          value={`$${portfolioData.total_value.toLocaleString()}`}
          icon={DollarSign}
          trend="+2.5%"
          positive
        />
        <SummaryCard
          title="Day P&L"
          value={`$${portfolioData.day_pnl.toLocaleString()}`}
          icon={Activity}
          trend="+1.2%"
          positive={portfolioData.day_pnl >= 0}
        />
        <SummaryCard
          title="Total Return"
          value="+$5,000"
          icon={TrendingUp}
          trend="+5.3%"
          positive
        />
        <SummaryCard
          title="Cash Available"
          value="$25,000"
          icon={TrendingDown}
          trend="Available"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Portfolio Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3B82F6"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Allocation Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Asset Allocation</h3>
          {allocationData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {allocationData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400">
              No positions data available
            </div>
          )}
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Positions</h3>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Cost</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Current</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">P&L</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">P&L %</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {portfolioData.positions.map((position: any) => (
              <tr key={position.symbol} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium">{position.symbol}</td>
                <td className="px-6 py-4 text-right">{position.quantity}</td>
                <td className="px-6 py-4 text-right">${position.avg_cost}</td>
                <td className="px-6 py-4 text-right">${position.current_price}</td>
                <td className={`px-6 py-4 text-right ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ${position.unrealized_pnl}
                </td>
                <td className={`px-6 py-4 text-right ${position.unrealized_pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {position.unrealized_pnl_pct >= 0 ? '+' : ''}{position.unrealized_pnl_pct.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

interface SummaryCardProps {
  title: string;
  value: string;
  icon: React.ElementType;
  trend: string;
  positive?: boolean;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ title, value, icon: Icon, trend, positive }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
      </div>
      <div className={`p-3 rounded-full ${positive ? 'bg-green-100' : 'bg-gray-100'}`}>
        <Icon size={24} className={positive ? 'text-green-600' : 'text-gray-600'} />
      </div>
    </div>
    <p className={`text-sm mt-2 ${positive ? 'text-green-600' : 'text-gray-500'}`}>
      {trend}
    </p>
  </div>
);
