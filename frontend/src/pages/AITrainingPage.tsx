import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Brain, 
  Play, 
  Pause, 
  Settings, 
  Download, 
  Upload, 
  BarChart3, 
  Zap, 
  Database, 
  Target,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Trash2,
  Eye
} from 'lucide-react';

interface Model {
  id: string;
  name: string;
  type: string;
  status: 'training' | 'ready' | 'deployed' | 'error';
  accuracy: number;
  loss: number;
  epochs: number;
  dataset: string;
  lastTrained: string;
  description: string;
}

const AITrainingPage: React.FC = () => {
  const { t } = useTranslation();
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [trainingProgress, setTrainingProgress] = useState<number>(0);

  const models: Model[] = [
    {
      id: '1',
      name: 'Market Predictor v2',
      type: 'Neural Network',
      status: 'deployed',
      accuracy: 0.92,
      loss: 0.08,
      epochs: 100,
      dataset: 'Historical Market Data 2020-2023',
      lastTrained: '2024-01-15',
      description: 'Advanced neural network for market trend prediction'
    },
    {
      id: '2',
      name: 'Risk Assessment Model',
      type: 'Random Forest',
      status: 'training',
      accuracy: 0.87,
      loss: 0.13,
      epochs: 50,
      dataset: 'Risk Factors Dataset',
      lastTrained: '2024-01-20',
      description: 'Machine learning model for portfolio risk assessment'
    },
    {
      id: '3',
      name: 'Sentiment Analyzer',
      type: 'Transformer',
      status: 'ready',
      accuracy: 0.89,
      loss: 0.11,
      epochs: 75,
      dataset: 'News & Social Media Data',
      lastTrained: '2024-01-10',
      description: 'NLP model for market sentiment analysis'
    },
    {
      id: '4',
      name: 'Portfolio Optimizer',
      type: 'Genetic Algorithm',
      status: 'error',
      accuracy: 0.78,
      loss: 0.22,
      epochs: 25,
      dataset: 'Portfolio Performance Data',
      lastTrained: '2024-01-18',
      description: 'Optimization algorithm for portfolio allocation'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed': return 'text-green-600 bg-green-100';
      case 'ready': return 'text-blue-600 bg-blue-100';
      case 'training': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'deployed': return <CheckCircle className="w-4 h-4" />;
      case 'ready': return <Eye className="w-4 h-4" />;
      case 'training': return <Clock className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return null;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'deployed': return 'Deployed';
      case 'ready': return 'Ready';
      case 'training': return 'Training';
      case 'error': return 'Error';
      default: return 'Unknown';
    }
  };

  const handleTrainModel = (model: Model) => {
    setSelectedModel(model);
    setTrainingProgress(0);
    // Simulate training progress
    const interval = setInterval(() => {
      setTrainingProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 5;
      });
    }, 500);
  };

  const handleDeployModel = (model: Model) => {
    console.log('Deploying model:', model.name);
    // Handle deployment logic
  };

  const handleDeleteModel = (model: Model) => {
    console.log('Deleting model:', model.name);
    // Handle deletion logic
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Brain className="w-8 h-8 mr-3 text-blue-600" />
          {t('aiTraining.title')}
        </h1>
        <p className="text-gray-600">{t('aiTraining.description')}</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Models</p>
              <p className="text-2xl font-bold text-gray-900">{models.length}</p>
            </div>
            <Brain className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Deployed</p>
              <p className="text-2xl font-bold text-green-600">
                {models.filter(m => m.status === 'deployed').length}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">In Training</p>
              <p className="text-2xl font-bold text-yellow-600">
                {models.filter(m => m.status === 'training').length}
              </p>
            </div>
            <Clock className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Accuracy</p>
              <p className="text-2xl font-bold text-blue-600">
                {(models.reduce((acc, m) => acc + m.accuracy, 0) / models.length * 100).toFixed(1)}%
              </p>
            </div>
            <Target className="w-8 h-8 text-blue-500" />
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
          {t('aiTraining.createModel')}
        </button>
        <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200 flex items-center">
          <Upload className="w-5 h-5 mr-2" />
          Import Model
        </button>
        <button className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200 flex items-center">
          <Database className="w-5 h-5 mr-2" />
          Manage Datasets
        </button>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {models.map(model => (
          <div key={model.id} className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{model.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{model.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center">
                    <Zap className="w-4 h-4 mr-1" />
                    {model.type}
                  </span>
                  <span className="flex items-center">
                    <Database className="w-4 h-4 mr-1" />
                    {model.epochs} epochs
                  </span>
                </div>
              </div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(model.status)}`}>
                {getStatusIcon(model.status)}
                <span className="ml-1">{getStatusText(model.status)}</span>
              </span>
            </div>

            {/* Progress Bar for Training Models */}
            {model.status === 'training' && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Training Progress</span>
                  <span className="text-sm text-gray-600">{trainingProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${trainingProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Accuracy</span>
                  <TrendingUp className="w-4 h-4 text-green-500" />
                </div>
                <p className="text-lg font-semibold text-gray-900">{(model.accuracy * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Loss</span>
                  <BarChart3 className="w-4 h-4 text-red-500" />
                </div>
                <p className="text-lg font-semibold text-gray-900">{model.loss.toFixed(3)}</p>
              </div>
            </div>

            {/* Dataset Info */}
            <div className="bg-blue-50 rounded-lg p-3 mb-4">
              <div className="flex items-center">
                <Database className="w-4 h-4 text-blue-600 mr-2" />
                <span className="text-sm text-blue-900 font-medium">{model.dataset}</span>
              </div>
              <p className="text-xs text-blue-700 mt-1">Last trained: {model.lastTrained}</p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              {model.status === 'ready' && (
                <>
                  <button
                    onClick={() => handleTrainModel(model)}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    {t('aiTraining.trainModel')}
                  </button>
                  <button
                    onClick={() => handleDeployModel(model)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200"
                  >
                    <Zap className="w-4 h-4" />
                  </button>
                </>
              )}
              {model.status === 'training' && (
                <button
                  className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors duration-200 flex items-center justify-center"
                >
                  <Pause className="w-4 h-4 mr-2" />
                  Pause Training
                </button>
              )}
              {model.status === 'deployed' && (
                <>
                  <button className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg cursor-not-allowed">
                    Deployed
                  </button>
                  <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200">
                    <Settings className="w-4 h-4" />
                  </button>
                </>
              )}
              {model.status === 'error' && (
                <button className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 flex items-center justify-center">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  View Error
                </button>
              )}
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200">
                <Download className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDeleteModel(model)}
                className="px-4 py-2 bg-red-200 text-red-700 rounded-lg hover:bg-red-300 transition-colors duration-200"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Model Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('aiTraining.createModel')}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Model Name</label>
                <input
                  type="text"
                  placeholder="Enter model name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Model Type</label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>Neural Network</option>
                  <option>Random Forest</option>
                  <option>Transformer</option>
                  <option>Genetic Algorithm</option>
                  <option>Support Vector Machine</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Dataset</label>
                <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>Historical Market Data 2020-2023</option>
                  <option>Risk Factors Dataset</option>
                  <option>News & Social Media Data</option>
                  <option>Portfolio Performance Data</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  placeholder="Describe your model..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Create Model
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
    </div>
  );
};

export default AITrainingPage;
