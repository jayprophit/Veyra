import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

export const TradingPage: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [quantity, setQuantity] = useState('100');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [orderType, setOrderType] = useState('market');

  const { data: quote, isLoading } = useQuery(
    ['quote', symbol],
    () => api.get(`/market/quote/${symbol}`).then((res) => res.data),
    { refetchInterval: 5000 }
  );

  const orderMutation = useMutation(
    (orderData: any) => api.post('/orders', orderData),
    {
      onSuccess: () => {
        toast.success('Order submitted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Order failed');
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    orderMutation.mutate({
      symbol,
      side,
      quantity,
      order_type: orderType,
    });
  };

  return (
    <div className="space-y-6">
      {/* Quote Card */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{symbol.toUpperCase()}</h2>
            {quote && (
              <div className="mt-2">
                <span className="text-3xl font-bold">${quote.price}</span>
                <span
                  className={`ml-2 text-lg ${
                    quote.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {quote.change >= 0 ? '+' : ''}
                  {quote.change} ({quote.change_pct}%)
                </span>
              </div>
            )}
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Volume</p>
            <p className="font-semibold">{quote?.volume?.toLocaleString() || '-'}</p>
          </div>
        </div>
      </div>

      {/* Order Form */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Place Order</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Symbol
              </label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="AAPL"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Side
                </label>
                <select
                  value={side}
                  onChange={(e) => setSide(e.target.value as 'buy' | 'sell')}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                >
                  <option value="buy">Buy</option>
                  <option value="sell">Sell</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Quantity
                </label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Order Type
              </label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              >
                <option value="market">Market</option>
                <option value="limit">Limit</option>
                <option value="stop">Stop</option>
              </select>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={orderMutation.isLoading}
                className={`w-full py-3 px-4 rounded-lg font-semibold text-white ${
                  side === 'buy'
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-red-600 hover:bg-red-700'
                } disabled:opacity-50`}
              >
                {orderMutation.isLoading
                  ? 'Submitting...'
                  : `${side === 'buy' ? 'Buy' : 'Sell'} ${symbol.toUpperCase()}`}
              </button>
            </div>
          </form>
        </div>

        {/* Quick Stats */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Account Summary</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
              <div className="flex items-center">
                <DollarSign className="w-5 h-5 text-gray-600 mr-2" />
                <span>Buying Power</span>
              </div>
              <span className="font-semibold">$25,000.00</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
              <div className="flex items-center">
                <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
                <span>Day Trades</span>
              </div>
              <span className="font-semibold">0 / 3</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
              <div className="flex items-center">
                <TrendingDown className="w-5 h-5 text-red-600 mr-2" />
                <span>Unsettled Funds</span>
              </div>
              <span className="font-semibold">$0.00</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
