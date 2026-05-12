import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, Mail, Bell, ArrowRight, Calendar } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const ComingSoonPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-4xl w-full text-center">
        {/* Coming Soon Animation */}
        <div className="mb-8 relative">
          <div className="text-6xl font-bold text-blue-600 mb-4 animate-pulse">
            {t('pages.comingSoon.title')}
          </div>
          <div className="flex justify-center mb-8">
            <Clock className="w-16 h-16 text-blue-500 animate-spin-slow" />
          </div>
        </div>

        {/* Main Message */}
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          {t('pages.comingSoon.message')}
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          {t('pages.comingSoon.description')}
        </p>

        {/* Estimated Launch */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-center justify-center mb-4">
            <Calendar className="w-6 h-6 text-blue-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">
              {t('pages.comingSoon.estimatedLaunch')}
            </h2>
          </div>
          
          {/* Countdown Timer */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">45</div>
              <div className="text-sm text-gray-600">Days</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">12</div>
              <div className="text-sm text-gray-600">Hours</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">34</div>
              <div className="text-sm text-gray-600">Minutes</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">56</div>
              <div className="text-sm text-gray-600">Seconds</div>
            </div>
          </div>
        </div>

        {/* Notification Form */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {t('pages.comingSoon.notifyMe')}
          </h2>
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <div className="flex-1 relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => console.log('Notify me clicked')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
            >
              <Bell className="w-4 h-4 mr-2" />
              Notify Me
            </button>
          </div>
        </div>

        {/* Feature Preview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <ArrowRight className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Advanced Analytics</h3>
            <p className="text-gray-600">Cutting-edge market analysis tools and insights</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <ArrowRight className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Trading</h3>
            <p className="text-gray-600">Smart algorithms to optimize your trading strategies</p>
          </div>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <ArrowRight className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-time Data</h3>
            <p className="text-gray-600">Live market data and instant execution capabilities</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <Link
            to="/"
            className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            <ArrowRight className="w-5 h-5 mr-2" />
            Back to Dashboard
          </Link>
          
          <Link
            to="/contact"
            className="inline-flex items-center justify-center px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors duration-200"
          >
            <Mail className="w-5 h-5 mr-2" />
            Contact Us
          </Link>
        </div>

        {/* Social Links */}
        <div className="border-t border-gray-200 pt-8">
          <p className="text-gray-600 mb-4">Follow our progress</p>
          <div className="flex justify-center space-x-4">
            <a href="#" className="text-blue-600 hover:text-blue-700">Twitter</a>
            <a href="#" className="text-blue-600 hover:text-blue-700">LinkedIn</a>
            <a href="#" className="text-blue-600 hover:text-blue-700">GitHub</a>
            <a href="#" className="text-blue-600 hover:text-blue-700">Discord</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComingSoonPage;
