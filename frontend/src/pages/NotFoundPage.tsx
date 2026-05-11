import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Search, ArrowLeft, Mail } from 'lucide-react';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* 404 Animation */}
        <div className="mb-8 relative">
          <div className="text-9xl font-bold text-gray-300 animate-pulse">404</div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-6xl font-bold text-blue-600 opacity-20">404</div>
          </div>
        </div>

        {/* Error Message */}
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Page Not Found
        </h1>
        
        <p className="text-xl text-gray-600 mb-8">
          Oops! The page you're looking for seems to have vanished into the digital void.
        </p>

        {/* Error Details */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8 text-left">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            What might have happened?
          </h2>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">•</span>
              The page may have been moved or deleted
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">•</span>
              You might have typed the URL incorrectly
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">•</span>
              The link you followed may be broken
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">•</span>
              The page might be temporarily unavailable
            </li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <Link
            to="/"
            className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            <Home className="w-5 h-5 mr-2" />
            Go Home
          </Link>
          
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center justify-center px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors duration-200"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Go Back
          </button>
        </div>

        {/* Search Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            Looking for something specific?
          </h2>
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search Veyra..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
                  if (e.key === 'Enter') {
                    // Implement search functionality
                    console.log('Search for:', e.currentTarget.value);
                  }
                }}
              />
            </div>
            <button
              onClick={(): void => {
                const input = document.querySelector('input[type="text"]') as HTMLInputElement;
                if (input?.value) {
                  console.log('Search for:', input.value);
                }
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Search
            </button>
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          <Link
            to="/portfolio"
            className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200"
          >
            <div className="text-blue-600 font-medium">Portfolio</div>
          </Link>
          <Link
            to="/trading"
            className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200"
          >
            <div className="text-blue-600 font-medium">Trading</div>
          </Link>
          <Link
            to="/analysis"
            className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200"
          >
            <div className="text-blue-600 font-medium">Analysis</div>
          </Link>
          <Link
            to="/settings"
            className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200"
          >
            <div className="text-blue-600 font-medium">Settings</div>
          </Link>
        </div>

        {/* Contact Support */}
        <div className="border-t border-gray-200 pt-8">
          <p className="text-gray-600 mb-4">
            Still can't find what you're looking for?
          </p>
          <Link
            to="/support"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
          >
            <Mail className="w-4 h-4 mr-2" />
            Contact Support
          </Link>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-sm text-gray-500">
          <p>Error Code: 404 | Timestamp: {new Date().toISOString()}</p>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
