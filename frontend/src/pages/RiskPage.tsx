import React from 'react';
import { useQuery } from 'react-query';
import { Shield, AlertTriangle, TrendingDown, Activity } from 'lucide-react';
import { api } from '../services/api';

export const RiskPage: React.FC = () => {
  const { data: riskMetrics, isLoading } = useQuery('risk', () =>
    api.get('/risk/metrics').then((res) => res.data)
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  const metrics = riskMetrics || {
    portfolio_var: 2500,
    portfolio_var_pct: 2.5,
    sharpe_ratio: 1.5,
    max_drawdown: 5.0,
    beta: 1.0,
  };

  return (
    <div className="space-y-6">
      {/* Risk Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <RiskCard
          title="Value at Risk (VaR)"
          value={`$${metrics.portfolio_var.toLocaleString()}`}
          subtitle={`${metrics.portfolio_var_pct}% of portfolio`}
          icon={Shield}
          color="blue"
        />
        <RiskCard
          title="Sharpe Ratio"
          value={metrics.sharpe_ratio.toFixed(2)}
          subtitle="Risk-adjusted return"
          icon={Activity}
          color="green"
        />
        <RiskCard
          title="Max Drawdown"
          value={`${metrics.max_drawdown}%`}
          subtitle="Peak to trough decline"
          icon={TrendingDown}
          color="red"
        />
        <RiskCard
          title="Portfolio Beta"
          value={metrics.beta.toFixed(2)}
          subtitle="Market sensitivity"
          icon={AlertTriangle}
          color="yellow"
        />
      </div>

      {/* Stress Test Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Stress Test Scenarios</h3>
        <div className="space-y-4">
          {[
            { name: 'Market Crash (-20%)', impact: '-$15,000', probability: 'Low' },
            { name: 'Interest Rate Spike', impact: '-$5,000', probability: 'Medium' },
            { name: 'Recession', impact: '-$12,000', probability: 'Low' },
          ].map((scenario) => (
            <div
              key={scenario.name}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div>
                <p className="font-medium">{scenario.name}</p>
                <p className="text-sm text-gray-500">
                  Probability: {scenario.probability}
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-red-600">{scenario.impact}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Factors */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Risk Factor Exposure</h3>
        <div className="space-y-3">
          {[
            { factor: 'Market Risk', exposure: 85, status: 'High' },
            { factor: 'Sector Concentration', exposure: 45, status: 'Medium' },
            { factor: 'Liquidity Risk', exposure: 20, status: 'Low' },
            { factor: 'Currency Risk', exposure: 15, status: 'Low' },
          ].map((item) => (
            <div key={item.factor} className="flex items-center space-x-4">
              <div className="w-32 text-sm">{item.factor}</div>
              <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    item.status === 'High'
                      ? 'bg-red-500'
                      : item.status === 'Medium'
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${item.exposure}%` }}
                />
              </div>
              <div className="w-20 text-right text-sm text-gray-600">
                {item.status}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

interface RiskCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ElementType;
  color: string;
}

const RiskCard: React.FC<RiskCardProps> = ({ title, value, subtitle, icon: Icon, color }) => {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    yellow: 'bg-yellow-100 text-yellow-600',
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          <p className="text-sm text-gray-400 mt-1">{subtitle}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
};
