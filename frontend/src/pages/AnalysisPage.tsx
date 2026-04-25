import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Brain, TrendingUp, AlertTriangle, Activity } from 'lucide-react';
import { api } from '../services/api';

export const AnalysisPage: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [analysisType, setAnalysisType] = useState('sentiment');

  const { data: analysis, isLoading } = useQuery(
    ['analysis', symbol, analysisType],
    () =>
      api
        .post('/analysis', { symbol, analysis_type: analysisType })
        .then((res) => res.data),
    { enabled: !!symbol }
  );

  const analysisTypes = [
    { id: 'sentiment', label: 'Sentiment Analysis', icon: Brain },
    { id: 'pattern', label: 'Pattern Recognition', icon: TrendingUp },
    { id: 'prediction', label: 'Price Prediction', icon: Activity },
    { id: 'risk', label: 'Risk Analysis', icon: AlertTriangle },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="Enter symbol (e.g., AAPL)"
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={analysisType}
          onChange={(e) => setAnalysisType(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          {analysisTypes.map((type) => (
            <option key={type.id} value={type.id}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      {/* Analysis Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {analysisTypes.map((type) => {
          const Icon = type.icon;
          const isActive = analysisType === type.id;
          return (
            <button
              key={type.id}
              onClick={() => setAnalysisType(type.id)}
              className={`p-4 rounded-lg border text-left transition-colors ${
                isActive
                  ? 'bg-blue-50 border-blue-500'
                  : 'bg-white hover:bg-gray-50'
              }`}
            >
              <Icon className={`w-6 h-6 ${isActive ? 'text-blue-600' : 'text-gray-600'}`} />
              <p className={`mt-2 font-medium ${isActive ? 'text-blue-900' : 'text-gray-900'}`}>
                {type.label}
              </p>
            </button>
          );
        })}
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        </div>
      ) : analysis ? (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">
            {symbol} - {analysisTypes.find(t => t.id === analysisType)?.label} Results
          </h3>
          <pre className="bg-gray-50 p-4 rounded overflow-auto">
            {JSON.stringify(analysis, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="bg-gray-50 p-8 rounded-lg text-center text-gray-500">
          Enter a symbol and select an analysis type to see results
        </div>
      )}
    </div>
  );
};
