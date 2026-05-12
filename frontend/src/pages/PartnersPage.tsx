import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Users, 
  Globe, 
  Database, 
  BarChart3, 
  Code, 
  Building2, 
  Link, 
  Check, 
  X,
  Settings,
  ExternalLink,
  Search,
  Filter
} from 'lucide-react';

interface Partner {
  id: string;
  name: string;
  category: string;
  description: string;
  status: 'connected' | 'available' | 'unavailable';
  icon: React.ReactNode;
  features: string[];
  website?: string;
  apiKey?: string;
}

const PartnersPage: React.FC = () => {
  const { t } = useTranslation();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [showApiKeyModal, setShowApiKeyModal] = useState<boolean>(false);
  const [selectedPartner, setSelectedPartner] = useState<Partner | null>(null);

  const partners: Partner[] = [
    {
      id: '1',
      name: 'Alpha Markets',
      category: 'brokers',
      description: 'Premium brokerage services with advanced trading tools',
      status: 'connected',
      icon: <Users className="w-6 h-6" />,
      features: ['Real-time data', 'Advanced order types', 'API access'],
      website: 'https://alphamarkets.com',
      apiKey: 'am_***masked***'
    },
    {
      id: '2',
      name: 'DataFlow Analytics',
      category: 'dataProviders',
      description: 'Comprehensive market data and analytics platform',
      status: 'available',
      icon: <Database className="w-6 h-6" />,
      features: ['Historical data', 'Real-time feeds', 'Custom indicators'],
      website: 'https://dataflow.com'
    },
    {
      id: '3',
      name: 'QuantLab',
      category: 'analytics',
      description: 'Professional quantitative analysis and backtesting tools',
      status: 'connected',
      icon: <BarChart3 className="w-6 h-6" />,
      features: ['Backtesting engine', 'Risk metrics', 'Portfolio optimization'],
      website: 'https://quantlab.io',
      apiKey: 'ql_***masked***'
    },
    {
      id: '4',
      name: 'TradeAPI Pro',
      category: 'apiPartners',
      description: 'RESTful API for automated trading and portfolio management',
      status: 'available',
      icon: <Code className="w-6 h-6" />,
      features: ['REST API', 'WebSocket support', 'Documentation'],
      website: 'https://tradeapi.pro'
    },
    {
      id: '5',
      name: 'FinTech Solutions',
      category: 'fintech',
      description: 'Innovative financial technology solutions for institutions',
      status: 'unavailable',
      icon: <Globe className="w-6 h-6" />,
      features: ['Institutional tools', 'White-label solutions', 'Compliance'],
      website: 'https://fintechsolutions.com'
    },
    {
      id: '6',
      name: 'Capital Partners',
      category: 'institutional',
      description: 'Institutional-grade trading and investment services',
      status: 'available',
      icon: <Building2 className="w-6 h-6" />,
      features: ['Institutional access', 'Bulk trading', 'Dedicated support'],
      website: 'https://capitalpartners.com'
    }
  ];

  const categories = [
    { id: 'all', name: 'All Partners', icon: <Users className="w-4 h-4" /> },
    { id: 'brokers', name: t('partners.categories.brokers'), icon: <Users className="w-4 h-4" /> },
    { id: 'dataProviders', name: t('partners.categories.dataProviders'), icon: <Database className="w-4 h-4" /> },
    { id: 'analytics', name: t('partners.categories.analytics'), icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'apiPartners', name: t('partners.categories.apiPartners'), icon: <Code className="w-4 h-4" /> },
    { id: 'fintech', name: t('partners.categories.fintech'), icon: <Globe className="w-4 h-4" /> },
    { id: 'institutional', name: t('partners.categories.institutional'), icon: <Building2 className="w-4 h-4" /> }
  ];

  const filteredPartners = partners.filter(partner => {
    const matchesCategory = selectedCategory === 'all' || partner.category === selectedCategory;
    const matchesSearch = partner.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         partner.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleConnect = (partner: Partner) => {
    if (partner.status === 'available') {
      setSelectedPartner(partner);
      setShowApiKeyModal(true);
    }
  };

  const handleDisconnect = (partner: Partner) => {
    console.log('Disconnecting:', partner.name);
    // Handle disconnection logic
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-100';
      case 'available': return 'text-blue-600 bg-blue-100';
      case 'unavailable': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'connected': return 'Connected';
      case 'available': return 'Available';
      case 'unavailable': return 'Unavailable';
      default: return 'Unknown';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('partners.title')}</h1>
        <p className="text-gray-600">{t('partners.description')}</p>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col lg:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search partners..."
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

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Partners</p>
              <p className="text-2xl font-bold text-gray-900">{partners.length}</p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Connected</p>
              <p className="text-2xl font-bold text-green-600">
                {partners.filter(p => p.status === 'connected').length}
              </p>
            </div>
            <Check className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Available</p>
              <p className="text-2xl font-bold text-blue-600">
                {partners.filter(p => p.status === 'available').length}
              </p>
            </div>
            <Link className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Partners Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPartners.map(partner => (
          <div key={partner.id} className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mr-3">
                  {partner.icon}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{partner.name}</h3>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(partner.status)}`}>
                    {getStatusText(partner.status)}
                  </span>
                </div>
              </div>
            </div>

            <p className="text-gray-600 mb-4">{partner.description}</p>

            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Features:</h4>
              <ul className="space-y-1">
                {partner.features.map((feature, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-center">
                    <Check className="w-3 h-3 text-green-500 mr-2" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            {partner.apiKey && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-1">API Key:</h4>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">{partner.apiKey}</code>
              </div>
            )}

            <div className="flex gap-2">
              {partner.status === 'connected' ? (
                <>
                  <button
                    onClick={() => handleDisconnect(partner)}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 flex items-center justify-center"
                  >
                    <X className="w-4 h-4 mr-2" />
                    {t('partners.disconnect')}
                  </button>
                  <button
                    onClick={() => console.log('Configure:', partner.name)}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                </>
              ) : partner.status === 'available' ? (
                <>
                  <button
                    onClick={() => handleConnect(partner)}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
                  >
                    <Link className="w-4 h-4 mr-2" />
                    {t('partners.connect')}
                  </button>
                  {partner.website && (
                    <a
                      href={partner.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </>
              ) : (
                <button
                  disabled
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
                >
                  {t('partners.connect')}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* API Key Modal */}
      {showApiKeyModal && selectedPartner && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Connect to {selectedPartner.name}
            </h3>
            <p className="text-gray-600 mb-4">
              To connect to {selectedPartner.name}, please enter your API key:
            </p>
            <input
              type="password"
              placeholder="Enter API key"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
            />
            <div className="flex gap-2">
              <button
                onClick={() => {
                  console.log('Connecting with API key');
                  setShowApiKeyModal(false);
                  setSelectedPartner(null);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Connect
              </button>
              <button
                onClick={() => {
                  setShowApiKeyModal(false);
                  setSelectedPartner(null);
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

export default PartnersPage;
