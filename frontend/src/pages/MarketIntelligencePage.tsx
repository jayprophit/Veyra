import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useQuery } from 'react-query';
import {
  Globe,
  Search,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  Clock,
  Filter,
  Download,
  Share2,
  Bell,
  Activity,
  MessageSquare,
  Newspaper,
  Twitter,
  BarChart3,
  Target,
  Zap,
  ChevronDown,
  ChevronRight,
  Play,
  Pause,
  Settings,
  Database,
  Shield,
  CheckCircle,
  XCircle,
  Loader2,
  ExternalLink,
  FileText,
  PieChart,
  Users,
  Hash,
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Repeat
} from 'lucide-react';
import { DataTable, BulkActions } from '../components/UI/DataTable';
import { Modal, DetailModal } from '../components/UI/Modal';
import { StatCard, LineChart, BarChart } from '../components/UI/ChartWidgets';
import { useLocalStorage } from '../hooks/useLocalStorage';
import toast from 'react-hot-toast';

// Types
interface ScrapedData {
  id: string;
  source: string;
  url: string;
  title: string;
  content: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  sentimentScore: number;
  relevance: number;
  timestamp: string;
  category: 'news' | 'social' | 'earnings' | 'analyst' | 'insider';
  entities: string[];
  quality: number;
}

interface ScrapingJob {
  id: string;
  name: string;
  source: string;
  status: 'idle' | 'running' | 'completed' | 'error';
  lastRun: string;
  nextRun: string;
  frequency: string;
  itemsCollected: number;
  errorCount: number;
}

interface SentimentTrend {
  timestamp: string;
  positive: number;
  negative: number;
  neutral: number;
  total: number;
}

// Mock API functions
const fetchScrapedData = async (): Promise<ScrapedData[]> => {
  await new Promise(resolve => setTimeout(resolve, 800));
  
  const sources = ['Bloomberg', 'Reuters', 'Twitter', 'Reddit', 'SEC Filings', 'Yahoo Finance'];
  const categories: ScrapedData['category'][] = ['news', 'social', 'earnings', 'analyst', 'insider'];
  const entities = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC'];
  
  return Array.from({ length: 50 }, (_, i) => {
    const sentiment = Math.random() > 0.6 ? 'positive' : Math.random() > 0.3 ? 'negative' : 'neutral';
    const sentimentScore = sentiment === 'positive' ? Math.random() * 0.5 + 0.5 : sentiment === 'negative' ? -(Math.random() * 0.5 + 0.5) : (Math.random() - 0.5) * 0.3;
    
    return {
      id: `scrape-${i}`,
      source: sources[Math.floor(Math.random() * sources.length)],
      url: `https://example.com/article-${i}`,
      title: `Market Update: ${entities[Math.floor(Math.random() * entities.length)]} shows ${sentiment} momentum`,
      content: `Latest market analysis shows ${sentiment} trends for major tech stocks. Analysts recommend ${Math.random() > 0.5 ? 'buy' : 'hold'} positions.`,
      sentiment,
      sentimentScore,
      relevance: Math.random() * 0.4 + 0.6,
      timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      category: categories[Math.floor(Math.random() * categories.length)],
      entities: entities.slice(0, Math.floor(Math.random() * 3) + 1),
      quality: Math.floor(Math.random() * 30) + 70,
    };
  });
};

const fetchScrapingJobs = async (): Promise<ScrapingJob[]> => {
  await new Promise(resolve => setTimeout(resolve, 400));
  
  return [
    { id: 'job-1', name: 'Bloomberg Market News', source: 'Bloomberg API', status: 'running', lastRun: '2 min ago', nextRun: 'In 13 min', frequency: 'Every 15 min', itemsCollected: 1247, errorCount: 0 },
    { id: 'job-2', name: 'Twitter Financial Sentiment', source: 'Twitter API', status: 'running', lastRun: '5 min ago', nextRun: 'In 10 min', frequency: 'Every 15 min', itemsCollected: 8934, errorCount: 2 },
    { id: 'job-3', name: 'SEC EDGAR Filings', source: 'SEC EDGAR', status: 'completed', lastRun: '1 hour ago', nextRun: 'In 23 hours', frequency: 'Daily', itemsCollected: 56, errorCount: 0 },
    { id: 'job-4', name: 'Reddit WallStreetBets', source: 'Reddit API', status: 'running', lastRun: '3 min ago', nextRun: 'In 12 min', frequency: 'Every 15 min', itemsCollected: 3421, errorCount: 0 },
    { id: 'job-5', name: 'Yahoo Finance News', source: 'Yahoo Finance', status: 'error', lastRun: '30 min ago', nextRun: 'In 5 min', frequency: 'Every 15 min', itemsCollected: 892, errorCount: 5 },
  ];
};

const fetchSentimentTrends = async (): Promise<SentimentTrend[]> => {
  await new Promise(resolve => setTimeout(resolve, 600));
  
  return Array.from({ length: 24 }, (_, i) => ({
    timestamp: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
    positive: Math.floor(Math.random() * 100) + 50,
    negative: Math.floor(Math.random() * 80) + 20,
    neutral: Math.floor(Math.random() * 60) + 30,
    total: 0,
  })).map(t => ({ ...t, total: t.positive + t.negative + t.neutral }));
};

const COLORS = {
  positive: '#10B981',
  negative: '#EF4444',
  neutral: '#6B7280',
  primary: '#4361EE',
  news: '#3B82F6',
  social: '#8B5CF6',
  earnings: '#F59E0B',
  analyst: '#10B981',
  insider: '#EC4899',
};

export function MarketIntelligencePage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'scraping' | 'sources' | 'alerts'>('dashboard');
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterSentiment, setFilterSentiment] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState<ScrapedData | null>(null);
  const [isAutoRefresh, setIsAutoRefresh] = useLocalStorage('market_intelligence_auto_refresh', true);
  const [refreshInterval, setRefreshInterval] = useState(30000);

  const { data: scrapedData, isLoading: dataLoading, refetch: refetchData } = useQuery(
    ['scraped-data'],
    fetchScrapedData,
    { 
      refetchInterval: isAutoRefresh ? refreshInterval : false,
      staleTime: 10000 
    }
  );

  const { data: scrapingJobs, isLoading: jobsLoading } = useQuery(
    ['scraping-jobs'],
    fetchScrapingJobs,
    { refetchInterval: 10000 }
  );

  const { data: sentimentTrends } = useQuery(
    ['sentiment-trends'],
    fetchSentimentTrends
  );

  const filteredData = useMemo(() => {
    if (!scrapedData) return [];
    return scrapedData.filter(item => {
      const categoryMatch = filterCategory === 'all' || item.category === filterCategory;
      const sentimentMatch = filterSentiment === 'all' || item.sentiment === filterSentiment;
      const searchMatch = !searchQuery || 
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.entities.some(e => e.toLowerCase().includes(searchQuery.toLowerCase()));
      return categoryMatch && sentimentMatch && searchMatch;
    });
  }, [scrapedData, filterCategory, filterSentiment, searchQuery]);

  const stats = useMemo(() => {
    if (!scrapedData) return null;
    
    const total = scrapedData.length;
    const positive = scrapedData.filter(d => d.sentiment === 'positive').length;
    const negative = scrapedData.filter(d => d.sentiment === 'negative').length;
    const neutral = total - positive - negative;
    const avgQuality = scrapedData.reduce((sum, d) => sum + d.quality, 0) / total;
    const avgRelevance = scrapedData.reduce((sum, d) => sum + d.relevance, 0) / total;
    
    return {
      total,
      positive,
      negative,
      neutral,
      avgQuality,
      avgRelevance,
      positiveRatio: (positive / total) * 100,
    };
  }, [scrapedData]);

  const handleManualRefresh = () => {
    refetchData();
    toast.success('Data refreshed manually');
  };

  const handleToggleJob = (jobId: string) => {
    toast.success(`Job ${jobId} toggled`);
  };

  return (
    <div className="ds-page market-intelligence">
      <div className="ds-page-header">
        <div className="ds-flex-between ds-flex-wrap">
          <div>
            <h1 className="ds-page-title">
              <Globe size={24} style={{ marginRight: '12px', display: 'inline', verticalAlign: 'middle' }} />
              Market Intelligence
            </h1>
            <p className="ds-page-subtitle">
              Live scraping dashboard for sentiment analysis
            </p>
          </div>
          <div className="ds-flex" style={{ gap: '12px' }}>
            <button className="ds-btn ds-btn-primary" onClick={handleManualRefresh}>
              <RefreshCw size={16} />
              Refresh
            </button>
            <button className="ds-btn ds-btn-secondary">
              <Settings size={16} />
              Configure
            </button>
          </div>
        </div>
      </div>

      <div className="ds-tabs">
        <button 
          className={`ds-tab ${activeTab === 'dashboard' ? 'ds-tab-active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <Activity size={16} />
          Dashboard
        </button>
        <button 
          className={`ds-tab ${activeTab === 'scraping' ? 'ds-tab-active' : ''}`}
          onClick={() => setActiveTab('scraping')}
        >
          <Zap size={16} />
          Scraping Jobs
        </button>
      </div>

      <div className="ds-page-content">
        {activeTab === 'dashboard' && (
          <div className="ds-space-y-6">
            <div className="ds-grid-4">
              <StatCard
                title="Total Mentions"
                value={stats?.total || 0}
                format="number"
                trend="up"
                trendValue="12% vs last hour"
                icon={<Activity size={20} />}
                color="primary"
              />
              <StatCard
                title="Positive Sentiment"
                value={stats?.positiveRatio || 0}
                format="percent"
                trend={stats && stats.positiveRatio > 50 ? 'up' : 'down'}
                trendValue={`${stats?.positive} items`}
                icon={<TrendingUp size={20} />}
                color="success"
              />
              <StatCard
                title="Avg Data Quality"
                value={stats?.avgQuality || 0}
                format="number"
                trend="up"
                trendValue="Out of 100"
                icon={<Shield size={20} />}
                color="primary"
              />
              <StatCard
                title="Active Sources"
                value={scrapingJobs?.filter(j => j.status === 'running').length || 0}
                format="number"
                trend="neutral"
                trendValue={`${scrapingJobs?.length || 0} total`}
                icon={<Database size={20} />}
                color="warning"
              />
            </div>

            <div className="ds-card">
              <div className="ds-card-header">
                <h3 className="ds-card-title">Live Intelligence Feed</h3>
                <div className="ds-flex" style={{ gap: '12px' }}>
                  <input
                    type="text"
                    placeholder="Search..."
                    className="ds-input ds-input-sm"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <select 
                    className="ds-input ds-input-sm"
                    value={filterCategory}
                    onChange={(e) => setFilterCategory(e.target.value)}
                  >
                    <option value="all">All</option>
                    <option value="news">News</option>
                    <option value="social">Social</option>
                  </select>
                </div>
              </div>
              <div className="ds-card-body">
                {filteredData.slice(0, 10).map((item) => (
                  <div key={item.id} className="ds-list-item" onClick={() => setSelectedItem(item)}>
                    <div className="ds-flex-between">
                      <span className="ds-font-medium">{item.title}</span>
                      <span className={`ds-badge ds-badge-${item.sentiment === 'positive' ? 'success' : item.sentiment === 'negative' ? 'danger' : 'secondary'}`}>
                        {item.sentiment}
                      </span>
                    </div>
                    <div className="ds-text-sm ds-text-muted">
                      {item.source} • {item.entities.join(', ')} • Quality: {item.quality}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'scraping' && (
          <div className="ds-card">
            <div className="ds-card-body">
              <table className="ds-table">
                <thead>
                  <tr>
                    <th>Job Name</th>
                    <th>Source</th>
                    <th>Status</th>
                    <th>Last Run</th>
                    <th>Items</th>
                    <th>Errors</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {scrapingJobs?.map((job) => (
                    <tr key={job.id}>
                      <td className="ds-font-medium">{job.name}</td>
                      <td>{job.source}</td>
                      <td>
                        <span className={`ds-badge ds-badge-${job.status === 'running' ? 'success' : job.status === 'error' ? 'danger' : 'secondary'}`}>
                          {job.status === 'running' && <Loader2 size={12} className="ds-spin" />}
                          {job.status}
                        </span>
                      </td>
                      <td>{job.lastRun}</td>
                      <td>{job.itemsCollected.toLocaleString()}</td>
                      <td>{job.errorCount > 0 ? <span className="ds-text-danger">{job.errorCount}</span> : job.errorCount}</td>
                      <td>
                        <button 
                          className="ds-btn ds-btn-xs ds-btn-ghost"
                          onClick={() => handleToggleJob(job.id)}
                        >
                          {job.status === 'running' ? <Pause size={12} /> : <Play size={12} />}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {selectedItem && (
        <Modal
          isOpen={!!selectedItem}
          onClose={() => setSelectedItem(null)}
          title={selectedItem.title}
        >
          <div className="ds-space-y-4">
            <div className="ds-flex" style={{ gap: '8px' }}>
              <span className="ds-tag" style={{ backgroundColor: COLORS[selectedItem.category] }}>
                {selectedItem.category}
              </span>
              <span className={`ds-badge ds-badge-${selectedItem.sentiment === 'positive' ? 'success' : selectedItem.sentiment === 'negative' ? 'danger' : 'secondary'}`}>
                {selectedItem.sentiment} ({(selectedItem.sentimentScore * 100).toFixed(0)}%)
              </span>
            </div>
            <p>{selectedItem.content}</p>
            <div className="ds-text-sm ds-text-muted">
              Source: {selectedItem.source} | Quality: {selectedItem.quality}% | Relevance: {(selectedItem.relevance * 100).toFixed(0)}%
            </div>
            <div className="ds-flex" style={{ gap: '8px' }}>
              {selectedItem.entities.map(e => (
                <span key={e} className="ds-tag ds-tag-secondary">${e}</span>
              ))}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
