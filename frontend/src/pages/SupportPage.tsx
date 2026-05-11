import React, { useState } from 'react';
import { Mail, Phone, MessageCircle, Send, Search, Book, HelpCircle, AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface SupportTicket {
  id: string;
  subject: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created: string;
  lastUpdated: string;
  description: string;
}

interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
}

const SupportPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'contact' | 'tickets' | 'faq' | 'docs'>('contact');
  const [ticketForm, setTicketForm] = useState({
    subject: '',
    description: '',
    priority: 'medium' as const,
    category: 'general'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFAQ, setSelectedFAQ] = useState<string | null>(null);

  // Mock data
  const myTickets: SupportTicket[] = [
    {
      id: 'TKT-001',
      subject: 'Portfolio data not updating',
      status: 'resolved',
      priority: 'high',
      created: '2024-01-10T10:30:00Z',
      lastUpdated: '2024-01-10T14:45:00Z',
      description: 'Portfolio values are not refreshing in real-time'
    },
    {
      id: 'TKT-002',
      subject: 'API rate limiting issues',
      status: 'in_progress',
      priority: 'medium',
      created: '2024-01-12T09:15:00Z',
      lastUpdated: '2024-01-12T16:20:00Z',
      description: 'Receiving 429 errors when making multiple API calls'
    }
  ];

  const faqs: FAQ[] = [
    {
      id: '1',
      question: 'How do I connect my broker account?',
      answer: 'Navigate to Settings > Broker Connections and follow the step-by-step instructions for your specific broker. We support Interactive Brokers, Alpaca, and Trading212.',
      category: 'Account Setup'
    },
    {
      id: '2',
      question: 'Why is my portfolio data not updating?',
      answer: 'Check your broker connection status in Settings. If connected, try refreshing the data manually. If issues persist, contact support with your broker and account details.',
      category: 'Technical Issues'
    },
    {
      id: '3',
      question: 'How often is market data updated?',
      answer: 'Real-time data updates every second during market hours. Delayed data (15-minute delay) is available for free users. Premium subscribers get real-time data.',
      category: 'Market Data'
    },
    {
      id: '4',
      question: 'What security measures are in place?',
      answer: 'We use bank-level encryption, two-factor authentication, and never store your broker credentials. All data is encrypted in transit and at rest.',
      category: 'Security'
    },
    {
      id: '5',
      question: 'How do I export my tax documents?',
      answer: 'Go to Tax Dashboard > Export Documents. You can generate PDF tax forms and CSV transaction data for any tax year.',
      category: 'Tax & Reporting'
    }
  ];

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'open':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleTicketSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    // Handle ticket submission
    console.log('Submitting ticket:', ticketForm);
    // Reset form
    setTicketForm({
      subject: '',
      description: '',
      priority: 'medium',
      category: 'general'
    });
  };

  const filteredFAQs = faqs.filter(faq =>
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <HelpCircle className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-semibold text-gray-900">Support Center</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search support..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'contact', label: 'Contact Support', icon: MessageCircle },
              { id: 'tickets', label: 'My Tickets', icon: AlertCircle },
              { id: 'faq', label: 'FAQ', icon: HelpCircle },
              { id: 'docs', label: 'Documentation', icon: Book }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Contact Support Tab */}
        {activeTab === 'contact' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Create Support Ticket</h2>
                <form onSubmit={handleTicketSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Subject
                    </label>
                    <input
                      type="text"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={ticketForm.subject}
                      onChange={(e) => setTicketForm({...ticketForm, subject: e.target.value})}
                      placeholder="Brief description of your issue"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Priority
                      </label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        value={ticketForm.priority}
                        onChange={(e) => setTicketForm({...ticketForm, priority: e.target.value as any})}
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Category
                      </label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        value={ticketForm.category}
                        onChange={(e) => setTicketForm({...ticketForm, category: e.target.value})}
                      >
                        <option value="general">General</option>
                        <option value="technical">Technical</option>
                        <option value="billing">Billing</option>
                        <option value="account">Account</option>
                        <option value="feature">Feature Request</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      required
                      rows={6}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={ticketForm.description}
                      onChange={(e) => setTicketForm({...ticketForm, description: e.target.value})}
                      placeholder="Please provide detailed information about your issue..."
                    />
                  </div>

                  <button
                    type="submit"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    Submit Ticket
                  </button>
                </form>
              </div>
            </div>

            <div>
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Contacts</h3>
                <div className="space-y-3">
                  <a href="mailto:support@veyra.dev" className="flex items-center space-x-3 text-gray-600 hover:text-blue-600">
                    <Mail className="w-5 h-5" />
                    <span>support@veyra.dev</span>
                  </a>
                  <a href="tel:+1-800-VEYRA" className="flex items-center space-x-3 text-gray-600 hover:text-blue-600">
                    <Phone className="w-5 h-5" />
                    <span>1-800-VEYRA</span>
                  </a>
                  <a href="#" className="flex items-center space-x-3 text-gray-600 hover:text-blue-600">
                    <MessageCircle className="w-5 h-5" />
                    <span>Live Chat</span>
                  </a>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">Response Times</h3>
                <div className="space-y-2 text-sm text-blue-800">
                  <div className="flex justify-between">
                    <span>Urgent:</span>
                    <span className="font-medium">1-2 hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span>High:</span>
                    <span className="font-medium">4-6 hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Medium:</span>
                    <span className="font-medium">24 hours</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Low:</span>
                    <span className="font-medium">48-72 hours</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* My Tickets Tab */}
        {activeTab === 'tickets' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">My Support Tickets</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {myTickets.map((ticket: SupportTicket) => (
                <div key={ticket.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-sm font-medium text-gray-900">{ticket.subject}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(ticket.status)}`}>
                          {ticket.status.replace('_', ' ')}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(ticket.priority)}`}>
                          {ticket.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{ticket.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>Ticket ID: {ticket.id}</span>
                        <span>Created: {new Date(ticket.created).toLocaleDateString()}</span>
                        <span>Updated: {new Date(ticket.lastUpdated).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* FAQ Tab */}
        {activeTab === 'faq' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Frequently Asked Questions</h2>
                </div>
                <div className="divide-y divide-gray-200">
                  {filteredFAQs.map((faq: FAQ) => (
                    <div key={faq.id} className="p-6">
                      <button
                        onClick={() => setSelectedFAQ(selectedFAQ === faq.id ? null : faq.id)}
                        className="w-full text-left"
                      >
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-medium text-gray-900">{faq.question}</h3>
                          <div className={`transform transition-transform ${selectedFAQ === faq.id ? 'rotate-180' : ''}`}>
                            <AlertCircle className="w-4 h-4 text-gray-400" />
                          </div>
                        </div>
                      </button>
                      {selectedFAQ === faq.id && (
                        <div className="mt-3 text-sm text-gray-600">
                          <p>{faq.answer}</p>
                          <span className="inline-block mt-2 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                            {faq.category}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Categories</h3>
                <div className="space-y-2">
                  {Array.from(new Set(faqs.map(faq => faq.category))).map((category: string) => (
                    <button
                      key={category}
                      onClick={() => setSearchQuery(category)}
                      className="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded"
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Documentation Tab */}
        {activeTab === 'docs' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Documentation</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { title: 'Getting Started', description: 'Learn the basics of Veyra', icon: Book },
                { title: 'API Reference', description: 'Complete API documentation', icon: Book },
                { title: 'Trading Guide', description: 'How to use trading features', icon: Book },
                { title: 'Portfolio Management', description: 'Managing your investments', icon: Book },
                { title: 'Security', description: 'Security best practices', icon: Book },
                { title: 'Troubleshooting', description: 'Common issues and solutions', icon: Book }
              ].map((doc: any, index: number) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <doc.icon className="w-8 h-8 text-blue-600 mb-3" />
                  <h3 className="font-medium text-gray-900 mb-1">{doc.title}</h3>
                  <p className="text-sm text-gray-600 mb-3">{doc.description}</p>
                  <a href="#" className="text-sm text-blue-600 hover:text-blue-700">
                    Read more →
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SupportPage;
