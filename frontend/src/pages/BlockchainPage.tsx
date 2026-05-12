import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Wallet, 
  Link, 
  TrendingUp, 
  Shield, 
  Coins, 
  Network, 
  FileText, 
  ArrowRight,
  Copy,
  ExternalLink,
  Check,
  AlertCircle,
  RefreshCw,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react';

interface WalletInfo {
  id: string;
  name: string;
  address: string;
  balance: string;
  network: string;
  connected: boolean;
  type: 'metamask' | 'walletconnect' | 'coinbase' | 'custom';
}

interface DeFiProtocol {
  id: string;
  name: string;
  apy: string;
  tvl: string;
  risk: 'low' | 'medium' | 'high';
  category: string;
  connected: boolean;
}

interface Transaction {
  id: string;
  hash: string;
  type: 'send' | 'receive' | 'swap' | 'stake';
  amount: string;
  token: string;
  timestamp: string;
  status: 'pending' | 'confirmed' | 'failed';
  from: string;
  to: string;
}

const BlockchainPage: React.FC = () => {
  const { t } = useTranslation();
  const [showPrivateKey, setShowPrivateKey] = useState<boolean>(false);
  const [selectedWallet, setSelectedWallet] = useState<WalletInfo | null>(null);
  const [showConnectModal, setShowConnectModal] = useState<boolean>(false);

  const wallets: WalletInfo[] = [
    {
      id: '1',
      name: 'MetaMask',
      address: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db45',
      balance: '2.456 ETH',
      network: 'Ethereum Mainnet',
      connected: true,
      type: 'metamask'
    },
    {
      id: '2',
      name: 'WalletConnect',
      address: '0x8ba1f109551bD432803012645Hac136c',
      balance: '1.234 ETH',
      network: 'Polygon',
      connected: false,
      type: 'walletconnect'
    },
    {
      id: '3',
      name: 'Coinbase Wallet',
      address: '0x3f5CE5FBFe3F6b32B3b8C4d4b4b8C4d4b4b8C4d4',
      balance: '0.789 ETH',
      network: 'Arbitrum',
      connected: false,
      type: 'coinbase'
    }
  ];

  const defiProtocols: DeFiProtocol[] = [
    {
      id: '1',
      name: 'Uniswap V3',
      apy: '12.5%',
      tvl: '$4.2B',
      risk: 'medium',
      category: 'DEX',
      connected: true
    },
    {
      id: '2',
      name: 'Aave',
      apy: '8.3%',
      tvl: '$12.1B',
      risk: 'low',
      category: 'Lending',
      connected: false
    },
    {
      id: '3',
      name: 'Compound',
      apy: '6.7%',
      tvl: '$8.9B',
      risk: 'low',
      category: 'Lending',
      connected: false
    },
    {
      id: '4',
      name: 'Curve Finance',
      apy: '15.2%',
      tvl: '$3.8B',
      risk: 'medium',
      category: 'DEX',
      connected: true
    }
  ];

  const transactions: Transaction[] = [
    {
      id: '1',
      hash: '0x1234...5678',
      type: 'swap',
      amount: '0.5',
      token: 'ETH',
      timestamp: '2024-01-20 14:30:00',
      status: 'confirmed',
      from: '0x742d...4Db45',
      to: '0x8ba1...136c'
    },
    {
      id: '2',
      hash: '0x5678...9abc',
      type: 'stake',
      amount: '1.0',
      token: 'USDC',
      timestamp: '2024-01-20 12:15:00',
      status: 'pending',
      from: '0x742d...4Db45',
      to: '0xdefi...protocol'
    },
    {
      id: '3',
      hash: '0x9abc...def0',
      type: 'receive',
      amount: '0.25',
      token: 'ETH',
      timestamp: '2024-01-19 18:45:00',
      status: 'confirmed',
      from: '0x3f5c...8C4d4',
      to: '0x742d...4Db45'
    }
  ];

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'text-green-600 bg-green-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'send': return <ArrowRight className="w-4 h-4 text-red-500" />;
      case 'receive': return <ArrowRight className="w-4 h-4 text-green-500 rotate-180" />;
      case 'swap': return <RefreshCw className="w-4 h-4 text-blue-500" />;
      case 'stake': return <TrendingUp className="w-4 h-4 text-purple-500" />;
      default: return <Coins className="w-4 h-4 text-gray-500" />;
    }
  };

  const handleConnectWallet = (wallet: WalletInfo) => {
    setSelectedWallet(wallet);
    setShowConnectModal(true);
  };

  const handleDisconnectWallet = (wallet: WalletInfo) => {
    console.log('Disconnecting wallet:', wallet.name);
    // Handle disconnection logic
  };

  const handleCopyAddress = (address: string) => {
    navigator.clipboard.writeText(address);
    // Show toast notification
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Network className="w-8 h-8 mr-3 text-blue-600" />
          {t('blockchain.title')}
        </h1>
        <p className="text-gray-600">{t('blockchain.description')}</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Connected Wallets</p>
              <p className="text-2xl font-bold text-gray-900">
                {wallets.filter(w => w.connected).length}
              </p>
            </div>
            <Wallet className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Balance</p>
              <p className="text-2xl font-bold text-gray-900">4.479 ETH</p>
            </div>
            <Coins className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">DeFi Positions</p>
              <p className="text-2xl font-bold text-gray-900">
                {defiProtocols.filter(p => p.connected).length}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending Transactions</p>
              <p className="text-2xl font-bold text-gray-900">
                {transactions.filter(t => t.status === 'pending').length}
              </p>
            </div>
            <RefreshCw className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Wallets Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <Wallet className="w-6 h-6 mr-2" />
          {t('blockchain.wallets')}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {wallets.map(wallet => (
            <div key={wallet.id} className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{wallet.name}</h3>
                  <p className="text-sm text-gray-600">{wallet.network}</p>
                </div>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  wallet.connected ? 'text-green-600 bg-green-100' : 'text-gray-600 bg-gray-100'
                }`}>
                  {wallet.connected ? <Check className="w-3 h-3 mr-1" /> : <AlertCircle className="w-3 h-3 mr-1" />}
                  {wallet.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Address</span>
                  <button
                    onClick={() => handleCopyAddress(wallet.address)}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded block break-all">
                  {wallet.address}
                </code>
              </div>

              <div className="mb-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{t('blockchain.balance')}</span>
                  <span className="text-lg font-semibold text-gray-900">{wallet.balance}</span>
                </div>
              </div>

              <div className="flex gap-2">
                {wallet.connected ? (
                  <>
                    <button
                      onClick={() => console.log('Manage wallet:', wallet.name)}
                      className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDisconnectWallet(wallet)}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
                    >
                      Disconnect
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleConnectWallet(wallet)}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                  >
                    {t('blockchain.connectWallet')}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* DeFi Protocols Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <TrendingUp className="w-6 h-6 mr-2" />
          {t('blockchain.defi')}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {defiProtocols.map(protocol => (
            <div key={protocol.id} className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{protocol.name}</h3>
                  <p className="text-sm text-gray-600">{protocol.category}</p>
                </div>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(protocol.risk)}`}>
                  {protocol.risk.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600">APY</p>
                  <p className="text-lg font-semibold text-green-600">{protocol.apy}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">TVL</p>
                  <p className="text-lg font-semibold text-gray-900">{protocol.tvl}</p>
                </div>
              </div>

              <button
                className={`w-full px-4 py-2 rounded-lg transition-colors duration-200 ${
                  protocol.connected 
                    ? 'bg-gray-300 text-gray-700 cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
                disabled={protocol.connected}
              >
                {protocol.connected ? 'Connected' : 'Connect'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Transactions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <FileText className="w-6 h-6 mr-2" />
          {t('blockchain.transactionHistory')}
        </h2>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hash
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.map(transaction => (
                  <tr key={transaction.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getTransactionIcon(transaction.type)}
                        <span className="ml-2 text-sm text-gray-900 capitalize">{transaction.type}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {transaction.amount} {transaction.token}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <code className="text-sm text-gray-600">{transaction.hash}</code>
                        <button className="ml-2 text-blue-600 hover:text-blue-700">
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(transaction.status)}`}>
                        {transaction.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button className="text-blue-600 hover:text-blue-900">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Connect Wallet Modal */}
      {showConnectModal && selectedWallet && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Connect to {selectedWallet.name}
            </h3>
            <p className="text-gray-600 mb-4">
              Please approve the connection request in your {selectedWallet.name} wallet.
            </p>
            <div className="bg-blue-50 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <Shield className="w-5 h-5 text-blue-600 mr-2" />
                <span className="text-sm text-blue-900">
                  This connection is secure and encrypted
                </span>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  console.log('Connecting to wallet:', selectedWallet.name);
                  setShowConnectModal(false);
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Connect
              </button>
              <button
                onClick={() => {
                  setShowConnectModal(false);
                  setSelectedWallet(null);
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

export default BlockchainPage;
