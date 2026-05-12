import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Database, 
  Satellite, 
  CreditCard, 
  MapPin, 
  MessageSquare, 
  Newspaper, 
  Cloud, 
  Truck, 
  Briefcase,
  Link,
  Check,
  X,
  Settings,
  Search,
  Filter,
  TrendingUp,
  AlertCircle,
  Clock,
  BarChart3
} from 'lucide-react';

interface DataSource {
  id: string;
  name: string;
  category: string;
  description: string;
  status: 'connected' | 'available' | 'unavailable';
  quality: 'high' | 'medium' | 'low';
  freshness: 'real-time' | 'hourly' | 'daily' | 'weekly';
  coverage: string;
  price: string;
  icon: React.ReactNode;
  features: string[];
  lastUpdated?: string;
  apiKey?: string;
}

const AlternativeDataPage: React.FC = () => {
  const { t } = useTranslation();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [showConnectModal, setShowConnectModal] = useState<boolean>(false);
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);

  const dataSources: DataSource[] = [
    {
      id: '1',
      name: 'Satellite Imaging Analytics',
      category: 'satellite',
      description: 'Real-time satellite imagery analysis for economic activity tracking',
      status: 'connected',
      quality: 'high',
      freshness: 'daily',
      coverage: 'Global',
      price: '$5,000/month',
      icon: <Satellite className="w-6 h-6" />,
      features: ['Oil tank monitoring', 'Agricultural yield prediction', 'Construction activity'],
      lastUpdated: '2024-01-20 14:30:00',
      apiKey: 'sat_***masked***'
    },
    {
      id: '2',
      name: 'Consumer Credit Analytics',
      category: 'creditCard',
      description: 'Aggregated credit card transaction data for retail insights',
      status: 'available',
      quality: 'high',
      freshness: 'daily',
      coverage: 'US, EU, UK',
      price: '$3,500/month',
      icon: <CreditCard className="w-6 h-6" />,
      features: ['Spending patterns', 'Category analysis', 'Geographic breakdown']
    },
    {
      id: '3',
      name: 'Mobile Location Intelligence',
      category: 'mobileLocation',
      description: 'Anonymized mobile location data for foot traffic analysis',
      status: 'connected',
      quality: 'medium',
      freshness: 'hourly',
      coverage: 'North America',
      price: '$2,800/month',
      icon: <MapPin className="w-6 h-6" />,
      features: ['Foot traffic patterns', 'Store visitation', 'Demographic insights'],
      lastUpdated: '2024-01-20 15:45:00',
      apiKey: 'loc_***masked***'
    },
    {
      id: '4',
      name: 'Social Media Sentiment',
      category: 'socialMedia',
      description: 'Real-time social media sentiment analysis and trend detection',
      status: 'available',
      quality: 'medium',
      freshness: 'real-time',
      coverage: 'Global',
      price: '$1,200/month',
      icon: <MessageSquare className="w-6 h-6" />,
      features: ['Brand sentiment', 'Trend detection', 'Influencer tracking']
    },
    {
      id: '5',
      name: 'News Analytics Engine',
      category: 'news',
      description: 'AI-powered news analysis for market impact assessment',
      status: 'connected',
      quality: 'high',
      freshness: 'real-time',
      coverage: 'Global (multilingual)',
      price: '$4,200/month',
      icon: <Newspaper className="w-6 h-6" />,
      features: ['Sentiment analysis', 'Entity recognition', 'Impact scoring'],
      lastUpdated: '2024-01-20 16:00:00',
      apiKey: 'news_***masked***'
    },
    {
      id: '6',
      name: 'Weather Intelligence',
      category: 'weather',
      description: 'Historical and predictive weather data for commodity trading',
      status: 'available',
      quality: 'high',
      freshness: 'hourly',
      coverage: 'Global',
      price: '$800/month',
      icon: <Cloud className="w-6 h-6" />,
      features: ['Historical data', 'Forecasts', 'Extreme weather alerts']
    },
    {
      id: '7',
      name: 'Supply Chain Tracking',
      category: 'shipping',
      description: 'Global shipping and logistics data for trade flow analysis',
      status: 'unavailable',
      quality: 'medium',
      freshness: 'daily',
      coverage: 'Major trade routes',
      price: '$6,500/month',
      icon: <Truck className="w-6 h-6" />,
      features: ['Port activity', 'Shipping volumes', 'Route optimization']
    },
    {
      id: '8',
      name: 'Job Market Intelligence',
      category: 'jobPostings',
      description: 'Real-time job posting data for economic health indicators',
      status: 'available',
      quality: 'high',
      freshness: 'daily',
      coverage: 'US, Europe',
      price: '$2,200/month',
      icon: <Briefcase className="w-6 h-6" />,
      features: ['Hiring trends', 'Salary analysis', 'Skill demand']
    }
  ];

  const categories = [
    { id: 'all', name: 'All Sources', icon: <Database className="w-4 h-4" /> },
    { id: 'satellite', name: t('alternativeData.satellite'), icon: <Satellite className="w-4 h-4" /> },
    { id: 'creditCard', name: t('alternativeData.creditCard'), icon: <CreditCard className="w-4 h-4" /> },
    { id: 'mobileLocation', name: t('alternativeData.mobileLocation'), icon: <MapPin className="w-4 h-4" /> },
    { id: 'socialMedia', name: t('alternativeData.socialMedia'), icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'news', name: t('alternativeData.news'), icon: <Newspaper className="w-4 h-4" /> },
    { id: 'weather', name: t('alternativeData.weather'), icon: <Cloud className="w-4 h-4" /> },
    { id: 'shipping', name: t('alternativeData.shipping'), icon: <Truck className="w-4 h-4" /> },
    { id: 'jobPostings', name: t('alternativeData.jobPostings'), icon: <Briefcase className="w-4 h-4" /> }
  ];

  const filteredSources = dataSources.filter(source => {
    const matchesCategory = selectedCategory === 'all' || source.category === selectedCategory;
    const matchesSearch = source.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         source.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-100';
      case 'available': return 'text-blue-600 bg-blue-100';
      case 'unavailable': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getFreshnessIcon = (freshness: string) => {
    switch (freshness) {
      case 'real-time': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'hourly': return <Clock className="w-4 h-4 text-blue-500" />;
      case 'daily': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'weekly': return <Clock className="w-4 h-4 text-gray-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const handleConnect = (source: DataSource) => {
    if (source.status === 'available') {
      setSelectedSource(source);
      setShowConnectModal(true);
    }
  };

  const handleDisconnect = (source: DataSource) => {
    console.log('Disconnecting source:', source.name);
    // Handle disconnection logic
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Database className="w-8 h-8 mr-3 text-blue-600" />
          {t('alternativeData.title')}
        </h1>
        <p className="text-gray-600">{t('alternativeData.description')}</p>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col lg:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search data sources..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Sources</p>
              <p className="text-2xl font-bold text-gray-900">{dataSources.length}</p>
            </div>
            <Database className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Connected</p>
              <p className="text-2xl font-bold text-green-600">
                {dataSources.filter(s => s.status === 'connected').length}
              </p>
            </div>
            <Check className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High Quality</p>
              <p className="text-2xl font-bold text-green-600">
                {dataSources.filter(s => s.quality === 'high').length}
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Real-time</p>
              <p className="text-2xl font-bold text-blue-600">
                {dataSources.filter(s => s.freshness === 'real-time').length}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Data Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSources.map(source => (
          <div key={source.id} className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mr-3">
                  {source.icon}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{source.name}</h3>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(source.status)}`}>
                    {source.status}
                  </span>
                </div>
              </div>
            </div>

            <p className="text-gray-600 mb-4 text-sm">{source.description}</p>

            {/* Metadata */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="flex items-center">
                <span className="text-sm text-gray-600 mr-2">Quality:</span>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getQualityColor(source.quality)}`}>
                  {source.quality}
                </span>
              </div>
              <div className="flex items-center">
                <span className="text-sm text-gray-600 mr-2">Freshness:</span>
                <div className="flex items-center">
                  {getFreshnessIcon(source.freshness)}
                  <span className="text-xs text-gray-700 ml-1">{source.freshness}</span>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Coverage</span>
                <span className="text-sm font-medium text-gray-900">{source.coverage}</span>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Price</span>
                <span className="text-sm font-medium text-gray-900">{source.price}</span>
              </div>
              {source.lastUpdated && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Last Updated</span>
                  <span className="text-xs text-gray-500">{source.lastUpdated}</span>
                </div>
              )}
            </div>

            {/* Features */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Features:</h4>
              <ul className="space-y-1">
                {source.features.slice(0, 3).map((feature, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-center">
                    <Check className="w-3 h-3 text-green-500 mr-2" />
                    {feature}
                  </li>
                ))}
                {source.features.length > 3 && (
                  <li className="text-sm text-blue-600">+{source.features.length - 3} more</li>
                )}
              </ul>
            </div>

            {/* API Key */}
            {source.apiKey && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900">API Key</span>
                  <button className="text-blue-600 hover:text-blue-700">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded block">{source.apiKey}</code>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              {source.status === 'connected' ? (
                <>
                  <button
                    onClick={() => handleDisconnect(source)}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 flex items-center justify-center"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Disconnect
                  </button>
                  <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200">
                    <Settings className="w-4 h-4" />
                  </button>
                </>
              ) : source.status === 'available' ? (
                <button
                  onClick={() => handleConnect(source)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
                >
                  <Link className="w-4 h-4 mr-2" />
                  {t('alternativeData.connectSource')}
                </button>
              ) : (
                <button
                  disabled
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
                >
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Unavailable
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Connect Modal */}
      {showConnectModal && selectedSource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Connect to {selectedSource.name}
            </h3>
            <p className="text-gray-600 mb-4">
              To connect to {selectedSource.name}, please enter your API credentials:
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                <input
                  type="password"
                  placeholder="Enter API key"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">API Secret (if required)</label>
                <input
                  type="password"
                  placeholder="Enter API secret"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-blue-600 mr-2" />
                <span className="text-sm text-blue-900">
                  Monthly subscription: {selectedSource.price}
                </span>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  console.log('Connecting to source:', selectedSource.name);
                  setShowConnectModal(false);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Connect
              </button>
              <button
                onClick={() => {
                  setShowConnectModal(false);
                  setSelectedSource(null);
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

export default AlternativeDataPage;
