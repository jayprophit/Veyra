import React, { useState, useEffect } from 'react';
import { AlertCircle, Clock, CheckCircle, RefreshCw, Mail, Bell, Zap, Shield } from 'lucide-react';

interface MaintenanceStatus {
  status: 'scheduled' | 'in_progress' | 'completed';
  title: string;
  description: string;
  startTime: string;
  endTime: string;
  affectedServices: string[];
  progress: number;
  updates: Array<{
    time: string;
    message: string;
    type: 'info' | 'warning' | 'success';
  }>;
}

const MaintenancePage: React.FC = () => {
  const [maintenanceStatus, setMaintenanceStatus] = useState<MaintenanceStatus>({
    status: 'in_progress',
    title: 'System Maintenance',
    description: 'We\'re performing scheduled maintenance to improve our services.',
    startTime: '2024-01-15T02:00:00Z',
    endTime: '2024-01-15T06:00:00Z',
    affectedServices: ['Trading Platform', 'Portfolio Analysis', 'Market Data', 'API Services'],
    progress: 65,
    updates: [
      {
        time: '2024-01-15T05:30:00Z',
        message: 'Database optimization completed successfully',
        type: 'success'
      },
      {
        time: '2024-01-15T04:45:00Z',
        message: 'API services are being updated',
        type: 'info'
      },
      {
        time: '2024-01-15T03:30:00Z',
        message: 'Trading platform maintenance in progress',
        type: 'warning'
      },
      {
        time: '2024-01-15T02:00:00Z',
        message: 'Maintenance started - System temporarily unavailable',
        type: 'info'
      }
    ]
  });

  const [currentTime, setCurrentTime] = useState<Date>(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date): string => {
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const calculateTimeRemaining = (endTime: string): string => {
    const end = new Date(endTime);
    const now = currentTime;
    const diff = end.getTime() - now.getTime();
    
    if (diff <= 0) return 'Completed';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    return `${hours}h ${minutes}m ${seconds}s`;
  };

  const getStatusIcon = (status: string): JSX.Element => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'in_progress':
        return <RefreshCw className="w-6 h-6 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-6 h-6 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };

  const getUpdateIcon = (type: string): JSX.Element => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      default:
        return <Bell className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 rounded-lg p-2">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Veyra Platform</h1>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Shield className="w-4 h-4" />
              <span>Maintenance Mode</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Status Card */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
          <div className={`px-6 py-4 border-b ${getStatusColor(maintenanceStatus.status)}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getStatusIcon(maintenanceStatus.status)}
                <div>
                  <h2 className="text-xl font-semibold">{maintenanceStatus.title}</h2>
                  <p className="text-sm opacity-75">{maintenanceStatus.description}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(maintenanceStatus.status)}`}>
                {maintenanceStatus.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>

          <div className="p-6">
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Progress</span>
                <span className="text-sm text-gray-500">{maintenanceStatus.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${maintenanceStatus.progress}%` }}
                />
              </div>
            </div>

            {/* Time Information */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-1">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Started</span>
                </div>
                <p className="text-sm text-gray-600">{formatTime(new Date(maintenanceStatus.startTime))}</p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-1">
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Time Remaining</span>
                </div>
                <p className="text-sm text-gray-600">{calculateTimeRemaining(maintenanceStatus.endTime)}</p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Expected End</span>
                </div>
                <p className="text-sm text-gray-600">{formatTime(new Date(maintenanceStatus.endTime))}</p>
              </div>
            </div>

            {/* Affected Services */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Affected Services</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {maintenanceStatus.affectedServices.map((service: string, index: number) => (
                  <div key={index} className="flex items-center space-x-2 bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2">
                    <AlertCircle className="w-4 h-4 text-yellow-600" />
                    <span className="text-sm text-yellow-800">{service}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Updates Timeline */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Maintenance Updates</h3>
          <div className="space-y-4">
            {maintenanceStatus.updates.map((update, index: number) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  {getUpdateIcon(update.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-900">{update.message}</p>
                    <span className="text-xs text-gray-500">
                      {formatTime(new Date(update.time))}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* What to Expect */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What to Expect</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">During Maintenance</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  Limited access to trading features
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  Real-time data may be unavailable
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  Portfolio updates may be delayed
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  API services temporarily limited
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">After Maintenance</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  Improved system performance
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  Enhanced security features
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  New features and improvements
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  Better data accuracy
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Contact Support */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">Need Assistance?</h3>
              <p className="text-blue-700">
                Our support team is available to help with any questions during this maintenance period.
              </p>
            </div>
            <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              <Mail className="w-4 h-4" />
              <span>Contact Support</span>
            </button>
          </div>
        </div>

        {/* Auto Refresh Notice */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>This page will automatically update when maintenance is complete.</p>
          <p className="mt-1">Last updated: {formatTime(currentTime)}</p>
        </div>
      </div>
    </div>
  );
};

export default MaintenancePage;
