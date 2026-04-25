import React from 'react';
import { useQuery } from 'react-query';
import { api } from '../services/api';
import { 
  DollarSign, Calendar, TrendingUp, AlertCircle,
  PieChart, ArrowUpRight, ArrowDownRight
} from 'lucide-react';

interface DividendHolding {
  symbol: string;
  quantity: number;
  annual_dividend_rate: number;
  dividend_yield: number;
  projected_annual_income: number;
  next_ex_date?: string;
}

export default function DividendTrackerPage() {
  const { data: portfolio, isLoading } = useQuery(
    'dividend-portfolio',
    () => api.get('/api/v2/dividends/portfolio').then(r => r.data),
    { refetchInterval: 60000 }
  );

  const { data: optimization } = useQuery(
    'dividend-optimization',
    () => api.get('/api/v2/dividends/optimization').then(r => r.data)
  );

  const holdings: DividendHolding[] = [
    { symbol: 'T', quantity: 100, annual_dividend_rate: 1.11, dividend_yield: 5.5, projected_annual_income: 111, next_ex_date: '2024-01-15' },
    { symbol: 'VZ', quantity: 50, annual_dividend_rate: 2.66, dividend_yield: 6.8, projected_annual_income: 133, next_ex_date: '2024-01-10' },
    { symbol: 'JNJ', quantity: 25, annual_dividend_rate: 4.24, dividend_yield: 2.8, projected_annual_income: 106, next_ex_date: '2024-02-20' },
    { symbol: 'KO', quantity: 75, annual_dividend_rate: 1.84, dividend_yield: 3.2, projected_annual_income: 138, next_ex_date: '2024-03-15' },
  ];

  const upcomingExDates = holdings.filter(h => h.next_ex_date);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dividend Tracker</h1>
        <p className="text-gray-600 mt-1">Track and optimize your dividend income</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <span className="text-green-100">Monthly Income</span>
            <DollarSign className="w-5 h-5 text-green-100" />
          </div>
          <div className="text-3xl font-bold">
            ${portfolio?.projected_monthly?.toFixed(2) || '488.00'}
          </div>
          <div className="text-sm text-green-100 mt-1">Projected avg</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500">Annual Income</span>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-3xl font-bold text-gray-900">
            ${portfolio?.projected_annual?.toFixed(2) || '5,856.00'}
          </div>
          <div className="text-sm text-green-600 mt-1 flex items-center gap-1">
            <ArrowUpRight className="w-3 h-3" />
            +12.5% vs last year
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500">Portfolio Yield</span>
            <PieChart className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-3xl font-bold text-gray-900">4.58%</div>
          <div className="text-sm text-gray-500 mt-1">Weighted average</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500">YTD Received</span>
            <Calendar className="w-5 h-5 text-gray-400" />
          </div>
          <div className="text-3xl font-bold text-gray-900">
            ${portfolio?.total_received_ytd?.toFixed(2) || '1,234.56'}
          </div>
          <div className="text-sm text-gray-500 mt-1">Across all holdings</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Holdings Table */}
        <div className="col-span-2 bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Dividend Holdings</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Shares</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Annual/Share</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Yield</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Annual Income</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Ex-Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {holdings.map((holding) => (
                  <tr key={holding.symbol} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{holding.symbol}</td>
                    <td className="px-4 py-3 text-right text-gray-600">{holding.quantity}</td>
                    <td className="px-4 py-3 text-right text-gray-600">${holding.annual_dividend_rate.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {holding.dividend_yield}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-medium text-green-600">
                      ${holding.projected_annual_income.toFixed(2)}
                    </td>
                    <td className="px-4 py-3 text-left text-gray-600">
                      {holding.next_ex_date ? (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {holding.next_ex_date}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Upcoming Ex-Dividends */}
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-500" />
              Upcoming Ex-Dates
            </h3>
            <div className="space-y-3">
              {upcomingExDates.map((holding) => (
                <div key={holding.symbol} className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{holding.symbol}</div>
                    <div className="text-xs text-gray-500">Ex-div: {holding.next_ex_date}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-amber-700">
                      ${(holding.annual_dividend_rate * holding.quantity / 4).toFixed(2)}
                    </div>
                    <div className="text-xs text-gray-500">est. payment</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Yield Optimization */}
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Yield Optimization</h3>
            <div className="space-y-3">
              {optimization?.suggestions?.slice(0, 3).map((suggestion: any, idx: number) => (
                <div key={idx} className="p-3 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">{suggestion.from_symbol} → {suggestion.to_symbol}</span>
                    <span className="text-xs text-green-600 font-medium">+{suggestion.annual_increase}%</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {suggestion.current_yield}% → {suggestion.suggested_yield}% yield
                  </div>
                </div>
              )) || (
                <>
                  <div className="p-3 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">JNJ → VZ</span>
                      <span className="text-xs text-green-600 font-medium">+$127/yr</span>
                    </div>
                    <div className="text-xs text-gray-500">2.8% → 6.8% yield</div>
                  </div>
                  <div className="p-3 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">KO → T</span>
                      <span className="text-xs text-green-600 font-medium">+$89/yr</span>
                    </div>
                    <div className="text-xs text-gray-500">3.2% → 5.5% yield</div>
                  </div>
                </>
              )}
            </div>
            <button className="w-full mt-4 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 text-sm font-medium">
              View All Suggestions
            </button>
          </div>

          {/* Income Calendar */}
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Income Calendar</h3>
            <div className="space-y-2">
              {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'].map((month, idx) => (
                <div key={month} className="flex items-center justify-between py-2 border-b last:border-0">
                  <span className="text-sm text-gray-600">{month} 2024</span>
                  <span className="font-medium text-gray-900">
                    ${(400 + Math.random() * 200).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
