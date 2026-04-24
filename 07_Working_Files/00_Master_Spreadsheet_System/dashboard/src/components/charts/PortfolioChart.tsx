import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface PortfolioData {
  date: string;
  value: number;
  benchmark: number;
}

interface PortfolioChartProps {
  data: PortfolioData[];
  height?: number;
}

export const PortfolioChart: React.FC<PortfolioChartProps> = ({ data, height = 400 }) => {
  return (
    <div className="w-full bg-[#0d0d0d] border border-white/10 rounded-2xl p-6">
      <h3 className="text-lg font-semibold mb-4 text-white">Portfolio Performance</h3>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff0a" />
          <XAxis 
            dataKey="date" 
            axisLine={false} 
            tickLine={false} 
            tick={{fill: '#4b5563', fontSize: 12}} 
            dy={10} 
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tick={{fill: '#4b5563', fontSize: 12}}
            tickFormatter={(val) => val.toLocaleString()}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#111', borderColor: '#333', borderRadius: '12px' }}
            itemStyle={{ color: '#10b981' }}
            formatter={(value: number) => [`$${value.toLocaleString()}`, 'Value']}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#10b981"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#colorValue)"
            name="Portfolio"
          />
          <Area
            type="monotone"
            dataKey="benchmark"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="transparent"
            strokeDasharray="5 5"
            name="S&P 500"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
