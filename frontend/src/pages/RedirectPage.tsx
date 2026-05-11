import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ExternalLink, Clock, CheckCircle, AlertCircle, Home, ArrowRight } from 'lucide-react';

interface RedirectConfig {
  destination: string;
  delay: number;
  message?: string;
  autoRedirect: boolean;
}

const RedirectPage: React.FC = () => {
  const { target } = useParams<{ target: string }>();
  const navigate = useNavigate();
  
  const [countdown, setCountdown] = useState(5);
  const [redirectStatus, setRedirectStatus] = useState<'pending' | 'success' | 'error'>('pending');
  const [redirectConfig, setRedirectConfig] = useState<RedirectConfig | null>(null);

  // predefined redirects
  const redirectMappings: Record<string, RedirectConfig> = {
    'portfolio': {
      destination: '/portfolio',
      delay: 3,
      message: 'Taking you to your portfolio dashboard...',
      autoRedirect: true
    },
    'trading': {
      destination: '/trading',
      delay: 3,
      message: 'Redirecting to trading platform...',
      autoRedirect: true
    },
    'analysis': {
      destination: '/analysis',
      delay: 3,
      message: 'Loading market analysis tools...',
      autoRedirect: true
    },
    'settings': {
      destination: '/settings',
      delay: 3,
      message: 'Opening settings panel...',
      autoRedirect: true
    },
    'support': {
      destination: '/support',
      delay: 3,
      message: 'Connecting to support center...',
      autoRedirect: true
    },
    'help': {
      destination: 'https://docs.veyra.dev',
      delay: 5,
      message: 'Opening documentation in a new tab...',
      autoRedirect: true
    },
    'github': {
      destination: 'https://github.com/veyra/veyra',
      delay: 3,
      message: 'Redirecting to GitHub repository...',
      autoRedirect: true
    },
    'discord': {
      destination: 'https://discord.gg/veyra',
      delay: 3,
      message: 'Joining our Discord community...',
      autoRedirect: true
    },
    'blog': {
      destination: 'https://blog.veyra.dev',
      delay: 3,
      message: 'Opening Veyra blog...',
      autoRedirect: true
    },
    'status': {
      destination: 'https://status.veyra.dev',
      delay: 3,
      message: 'Checking system status...',
      autoRedirect: true
    }
  };

  useEffect(() => {
    if (target && redirectMappings[target]) {
      const config = redirectMappings[target];
      setRedirectConfig(config);
      setCountdown(config.delay);

      if (config.autoRedirect) {
        const timer = setInterval(() => {
          setCountdown((prev) => {
            if (prev <= 1) {
              clearInterval(timer);
              performRedirect(config);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);

        return () => clearInterval(timer);
      } else {
        setRedirectStatus('error');
      }
    } else {
      setRedirectStatus('error');
    }
  }, [target]);

  const performRedirect = (config: RedirectConfig) => {
    try {
      if (config.destination.startsWith('http')) {
        // External URL - open in new tab
        window.open(config.destination, '_blank', 'noopener,noreferrer');
        setRedirectStatus('success');
      } else {
        // Internal route - navigate within app
        navigate(config.destination);
        setRedirectStatus('success');
      }
    } catch (error) {
      console.error('Redirect failed:', error);
      setRedirectStatus('error');
    }
  };

  const handleManualRedirect = (): void => {
    if (redirectConfig) {
      performRedirect(redirectConfig);
    }
  };

  const getStatusIcon = (): JSX.Element => {
    switch (redirectStatus) {
      case 'success':
        return <CheckCircle className="w-8 h-8 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-8 h-8 text-red-500" />;
      default:
        return <Clock className="w-8 h-8 text-blue-500 animate-pulse" />;
    }
  };

  const getStatusMessage = (): string => {
    if (redirectStatus === 'error') {
      return 'Invalid redirect target';
    }
    if (redirectStatus === 'success') {
      return 'Redirect completed';
    }
    return redirectConfig?.message || 'Preparing redirect...';
  };

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
    return 'Preparing redirect...';
  };

  const isExternal = redirectConfig?.destination.startsWith('http');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-lg w-full">
        {/* Main Card */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-8 text-center">
            <div className="mb-4 flex justify-center">
              {getStatusIcon()}
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">
              {redirectStatus === 'pending' ? 'Redirecting...' : 
               redirectStatus === 'success' ? 'Redirect Successful' : 
               'Redirect Failed'}
            </h1>
            <p className="text-blue-100">
              {getStatusMessage()}
            </p>
          </div>

          {/* Content */}
          <div className="p-6">
            {redirectStatus === 'pending' && redirectConfig && (
              <div className="text-center">
                {/* Countdown Timer */}
                <div className="mb-6">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full">
                    <span className="text-2xl font-bold text-blue-600">{countdown}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">seconds remaining</p>
                </div>

                {/* Progress Bar */}
                <div className="mb-6">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-1000"
                      style={{ 
                        width: `${((redirectConfig.delay - countdown) / redirectConfig.delay) * 100}%` 
                      }}
                    />
                  </div>
                </div>

                {/* Destination Info */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
                    <ExternalLink className="w-4 h-4" />
                    <span>Destination:</span>
                    <span className="font-medium text-gray-900">
                      {isExternal ? 
                        new URL(redirectConfig.destination).hostname : 
                        redirectConfig.destination
                      }
                    </span>
                  </div>
                </div>

                {/* Manual Redirect Button */}
                <button
                  onClick={handleManualRedirect}
                  className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
                >
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Redirect Now
                </button>
              </div>
            )}

            {redirectStatus === 'success' && (
              <div className="text-center">
                <div className="mb-6">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                </div>
                <p className="text-gray-600 mb-6">
                  {isExternal ? 
                    'The external link has been opened in a new tab.' :
                    'You have been successfully redirected.'}
                </p>
                
                {!isExternal && (
                  <button
                    onClick={() => navigate('/')}
                    className="inline-flex items-center px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors duration-200"
                  >
                    <Home className="w-4 h-4 mr-2" />
                    Go Home
                  </button>
                )}
              </div>
            )}

            {redirectStatus === 'error' && (
              <div className="text-center">
                <div className="mb-6">
                  <AlertCircle className="w-16 h-16 text-red-500 mx-auto" />
                </div>
                <p className="text-gray-600 mb-2">
                  The redirect target "{target}" is not valid.
                </p>
                <p className="text-sm text-gray-500 mb-6">
                  Please check the URL and try again.
                </p>
                
                <div className="space-y-2">
                  <button
                    onClick={() => navigate('/')}
                    className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
                  >
                    <Home className="w-4 h-4 mr-2" />
                    Go Home
                  </button>
                  
                  <button
                    onClick={() => window.history.back()}
                    className="w-full inline-flex items-center justify-center px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors duration-200"
                  >
                    Go Back
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Available Redirects */}
        {redirectStatus === 'error' && (
          <div className="mt-6 bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Available Redirects:</h3>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {Object.keys(redirectMappings).map((key) => (
                <a
                  key={key}
                  href={`/redirect/${key}`}
                  className="flex items-center space-x-1 text-blue-600 hover:text-blue-700"
                >
                  <span>/redirect/{key}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-6 text-center text-xs text-gray-500">
          <p>Redirect ID: {target || 'unknown'}</p>
          <p>Timestamp: {new Date().toISOString()}</p>
        </div>
      </div>
    </div>
  );
};

export default RedirectPage;
