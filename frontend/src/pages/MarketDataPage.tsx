import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Candlestick,
} from 'recharts';
import { Search, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const MarketDataPage: React.FC = () => {
  const [searchSymbol, setSearchSymbol] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');

  const { data: quote, refetch } = useQuery(
    ['quote', selectedSymbol],
    () => api.get(`/market/quote/${selectedSymbol}`).then((res) => res.data),
    { refetchInterval: 5000 }
  );

  const { data: historical } = useQuery(
    ['historical', selectedSymbol],
    () =>
      api
        .get(`/market/historical/${selectedSymbol}?timeframe=1d&days=30`)
        .then((res) => res.data)
  );

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchSymbol) {
      setSelectedSymbol(searchSymbol.toUpperCase());
    }
  };

  // Mock chart data if no historical data
  const chartData = historical || [
    { date: '2026-01-01', price: 145 },
    { date: '2026-01-05', price: 148 },
    { date: '2026-01-10', price: 146 },
    { date: '2026-01-15', price: 150 },
    { date: '2026-01-20', price: 152 },
  ];

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex space-x-2">
        <input
          type="text"
          value={searchSymbol}
          onChange={(e) => setSearchSymbol(e.target.value)}
          placeholder="Search symbol (e.g., AAPL)"
          className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Search className="w-5 h-5" />
        </button>
        <button
          type="button"
          onClick={() => refetch()}
          className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </form>

      {/* Quote Display */}
      {quote && (
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold">{quote.symbol}</h2>
              <div className="mt-2 flex items-baseline space-x-4">
                <span className="text-4xl font-bold">${quote.price.toFixed(2)}</span>
                <span
                  className={`text-xl ${
                    quote.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {quote.change >= 0 ? '+' : ''}
                  {quote.change.toFixed(2)} ({quote.change_pct.toFixed(2)}%)
                </span>
              </div>
            </div>
            <div className="text-right space-y-1">
              <p className="text-sm text-gray-500">
                Volume: <span className="font-semibold text-gray-900">{quote.volume?.toLocaleString()}</span>
              </p>
              <p className="text-sm text-gray-500">
                Updated: <span className="font-semibold text-gray-900">{new Date(quote.timestamp).toLocaleTimeString()}</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Price Chart</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {['SPY', 'QQQ', 'IWM'].map((etf) => (
          <div key={etf} className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <span className="font-semibold">{etf}</span>
              <span className="text-green-600">+1.2%</span>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {etf === 'SPY' && 'S&P 500 ETF'}
              {etf === 'QQQ' && 'Nasdaq 100 ETF'}
              {etf === 'IWM' && 'Russell 2000 ETF'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
