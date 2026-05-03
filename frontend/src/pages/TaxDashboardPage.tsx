import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from 'react-query';
import {
  Calculator,
  Receipt,
  AlertTriangle,
  CheckCircle,
  Download,
  FileText,
  TrendingUp,
  TrendingDown,
  Calendar,
  Filter,
  RefreshCw,
  DollarSign,
  Percent,
  Clock,
  ChevronDown,
  ChevronRight,
  Search,
  Bell,
  Settings,
  HelpCircle,
  PieChart,
  BarChart3,
  ArrowRightLeft,
  Wallet,
  Landmark,
  Receipt as ReceiptIcon,
  Camera,
  ScanLine
} from 'lucide-react';
import { DataTable, BulkActions } from '../components/UI/DataTable';
import { Modal, DetailModal, QualityScore } from '../components/UI/Modal';
import { StatCard, LineChart, PieChart as PieChartComponent, DateRangeSelector } from '../components/UI/ChartWidgets';
import { useLocalStorage } from '../hooks/useLocalStorage';
import toast from 'react-hot-toast';

// Types
interface TaxTransaction {
  id: string;
  date: string;
  type: 'buy' | 'sell' | 'dividend' | 'interest' | 'other';
  symbol: string;
  shares: number;
  price: number;
  total: number;
  costBasis: number;
  gainLoss: number;
  holdingPeriod: number; // days
  isLongTerm: boolean;
  taxRate: number;
  estimatedTax: number;
  status: 'pending' | 'calculated' | 'filed';
  source: string;
  receiptUrl?: string;
}

interface TaxSummary {
  totalProceeds: number;
  totalCostBasis: number;
  totalGainLoss: number;
  shortTermGains: number;
  longTermGains: number;
  estimatedTax: number;
  effectiveRate: number;
  washSaleLoss: number;
  qualifiedDividends: number;
  ordinaryDividends: number;
  interestIncome: number;
}

interface TaxBracket {
  bracket: string;
  rate: number;
  minIncome: number;
  maxIncome: number;
  estimatedTax: number;
}

interface Deduction {
  id: string;
  category: string;
  description: string;
  amount: number;
  date: string;
  receipt?: string;
  status: 'pending' | 'verified';
}

// Mock API functions
const fetchTaxTransactions = async (): Promise<TaxTransaction[]> => {
  await new Promise(resolve => setTimeout(resolve, 800));
  
  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'];
  const types: TaxTransaction['type'][] = ['buy', 'sell', 'dividend', 'interest'];
  
  return Array.from({ length: 25 }, (_, i) => {
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const type = types[Math.floor(Math.random() * types.length)];
    const shares = Math.floor(Math.random() * 100) + 1;
    const price = Math.random() * 500 + 50;
    const total = shares * price;
    const costBasis = type === 'sell' ? total * (0.7 + Math.random() * 0.3) : 0;
    const gainLoss = type === 'sell' ? total - costBasis : 0;
    const holdingPeriod = type === 'sell' ? Math.floor(Math.random() * 500) + 30 : 0;
    const isLongTerm = holdingPeriod > 365;
    const taxRate = isLongTerm ? 0.15 : 0.28;
    const estimatedTax = gainLoss > 0 ? gainLoss * taxRate : 0;
    
    return {
      id: `tax-${i}`,
      date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      type,
      symbol: type === 'interest' ? 'SAVINGS' : symbol,
      shares: type === 'sell' || type === 'buy' ? shares : 0,
      price: type === 'sell' || type === 'buy' ? price : 0,
      total,
      costBasis,
      gainLoss,
      holdingPeriod,
      isLongTerm,
      taxRate,
      estimatedTax,
      status: Math.random() > 0.3 ? 'calculated' : 'pending',
      source: ['broker', 'exchange', 'bank', 'manual'][Math.floor(Math.random() * 4)],
    };
  });
};

const fetchTaxSummary = async (): Promise<TaxSummary> => {
  await new Promise(resolve => setTimeout(resolve, 600));
  
  const totalProceeds = 245000;
  const totalCostBasis = 198000;
  const totalGainLoss = totalProceeds - totalCostBasis;
  const shortTermGains = 15000;
  const longTermGains = totalGainLoss - shortTermGains;
  const estimatedTax = shortTermGains * 0.28 + longTermGains * 0.15;
  
  return {
    totalProceeds,
    totalCostBasis,
    totalGainLoss,
    shortTermGains,
    longTermGains,
    estimatedTax,
    effectiveRate: estimatedTax / totalGainLoss,
    washSaleLoss: 2450,
    qualifiedDividends: 8500,
    ordinaryDividends: 3200,
    interestIncome: 1250,
  };
};

const fetchDeductions = async (): Promise<Deduction[]> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return [
    { id: 'ded-1', category: 'Investment Expenses', description: 'Trading Platform Fees', amount: 450, date: '2026-01-15', status: 'verified' },
    { id: 'ded-2', category: 'Investment Expenses', description: 'Financial Advisory', amount: 1200, date: '2026-02-20', status: 'verified' },
    { id: 'ded-3', category: 'Investment Expenses', description: 'Investment Software', amount: 299, date: '2026-03-01', status: 'pending' },
    { id: 'ded-4', category: 'Home Office', description: 'Office Equipment', amount: 850, date: '2026-01-10', status: 'pending' },
    { id: 'ded-5', category: 'Education', description: 'Investment Course', amount: 599, date: '2026-04-05', status: 'verified' },
  ];
};

// Tax Brackets 2026 (estimated)
const TAX_BRACKETS_2026 = [
  { bracket: '10%', rate: 0.10, minIncome: 0, maxIncome: 11925 },
  { bracket: '12%', rate: 0.12, minIncome: 11925, maxIncome: 48475 },
  { bracket: '22%', rate: 0.22, minIncome: 48475, maxIncome: 103350 },
  { bracket: '24%', rate: 0.24, minIncome: 103350, maxIncome: 197300 },
  { bracket: '32%', rate: 0.32, minIncome: 197300, maxIncome: 250525 },
  { bracket: '35%', rate: 0.35, minIncome: 250525, maxIncome: 626350 },
  { bracket: '37%', rate: 0.37, minIncome: 626350, maxIncome: Infinity },
];

const COLORS = {
  gain: '#10B981',
  loss: '#EF4444',
  neutral: '#6B7280',
  primary: '#4361EE',
  secondary: '#FF6000',
  longTerm: '#0D9488',
  shortTerm: '#D97706',
  dividend: '#8B5CF6',
  interest: '#EC4899'
};

export function TaxDashboardPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'forms' | 'deductions' | 'receipts'>('overview');
  const [selectedTransactions, setSelectedTransactions] = useState<Set<string>>(new Set());
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showReceiptModal, setShowReceiptModal] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<TaxTransaction | null>(null);
  const [taxYear, setTaxYear] = useState('2026');
  const [jurisdiction, setJurisdiction] = useLocalStorage('tax_jurisdiction', 'US');

  const { data: transactions, isLoading: transactionsLoading } = useQuery(
    ['tax-transactions', taxYear],
    fetchTaxTransactions,
    { refetchInterval: 30000 }
  );

  const { data: summary, isLoading: summaryLoading } = useQuery(
    ['tax-summary', taxYear],
    fetchTaxSummary,
    { refetchInterval: 30000 }
  );

  const { data: deductions, isLoading: deductionsLoading } = useQuery(
    ['deductions', taxYear],
    fetchDeductions
  );

  // Filtered transactions
  const filteredTransactions = useMemo(() => {
    if (!transactions) return [];
    return transactions.filter(t => {
      const typeMatch = filterType === 'all' || t.type === filterType;
      const statusMatch = filterStatus === 'all' || t.status === filterStatus;
      return typeMatch && statusMatch;
    });
  }, [transactions, filterType, filterStatus]);

  // Calculated metrics
  const metrics = useMemo(() => {
    if (!summary) return null;
    
    const totalDeductions = deductions?.reduce((sum, d) => sum + d.amount, 0) || 0;
    const taxableIncome = summary.totalGainLoss - totalDeductions;
    
    return {
      totalDeductions,
      taxableIncome,
      netTaxEstimate: Math.max(0, summary.estimatedTax - totalDeductions * 0.28),
      savingsFromDeductions: totalDeductions * 0.28
    };
  }, [summary, deductions]);

  // Chart data
  const gainsChartData = useMemo(() => {
    if (!summary) return [];
    return [
      { label: 'Long-Term Gains', value: summary.longTermGains, color: COLORS.longTerm },
      { label: 'Short-Term Gains', value: summary.shortTermGains, color: COLORS.shortTerm },
      { label: 'Wash Sale Loss', value: summary.washSaleLoss, color: COLORS.loss },
    ];
  }, [summary]);

  const incomeChartData = useMemo(() => {
    if (!summary) return [];
    return [
      { label: 'Qualified Dividends', value: summary.qualifiedDividends, color: COLORS.dividend },
      { label: 'Ordinary Dividends', value: summary.ordinaryDividends, color: COLORS.secondary },
      { label: 'Interest Income', value: summary.interestIncome, color: COLORS.interest },
    ];
  }, [summary]);

  // Handlers
  const handleExport8949 = () => {
    toast.success('Form 8949 exported for filing');
  };

  const handleExportScheduleD = () => {
    toast.success('Schedule D exported for filing');
  };

  const handleCaptureReceipt = () => {
    setShowReceiptModal(true);
  };

  const handleRefreshCalculations = () => {
    toast.success('Tax calculations refreshed with latest data');
  };

  const handleTransactionSelect = (id: string, selected: boolean) => {
    const newSet = new Set(selectedTransactions);
    if (selected) {
      newSet.add(id);
    } else {
      newSet.delete(id);
    }
    setSelectedTransactions(newSet);
  };

  const handleSelectAll = (selected: boolean) => {
    if (selected) {
      setSelectedTransactions(new Set(filteredTransactions.map(t => t.id)));
    } else {
      setSelectedTransactions(new Set());
    }
  };

  const renderOverview = () => (
    <div className="ds-space-y-6">
      {/* Tax Summary Cards */}
      <div className="ds-grid-4">
        <StatCard
          title="Total Gain/Loss"
          value={summary?.totalGainLoss || 0}
          format="currency"
          trend={summary && summary.totalGainLoss > 0 ? 'up' : 'down'}
          trendValue={summary ? `${((summary.totalGainLoss / summary.totalCostBasis) * 100).toFixed(1)}%` : '0%'}
          icon={<TrendingUp size={20} />}
          color={summary && summary.totalGainLoss >= 0 ? 'success' : 'danger'}
        />
        <StatCard
          title="Estimated Tax Due"
          value={summary?.estimatedTax || 0}
          format="currency"
          trend={metrics && metrics.netTaxEstimate < summary!.estimatedTax ? 'down' : 'up'}
          trendValue={`${metrics?.savingsFromDeductions.toFixed(0) || 0} saved`}
          icon={<Calculator size={20} />}
          color="warning"
        />
        <StatCard
          title="Effective Tax Rate"
          value={summary ? summary.effectiveRate * 100 : 0}
          format="percent"
          trend="neutral"
          icon={<Percent size={20} />}
          color="primary"
        />
        <StatCard
          title="Deductions Available"
          value={metrics?.totalDeductions || 0}
          format="currency"
          trend="up"
          trendValue={`${deductions?.length || 0} items`}
          icon={<Receipt size={20} />}
          color="success"
        />
      </div>

      {/* Gains Analysis & Income Breakdown */}
      <div className="ds-grid-2">
        <div className="ds-card">
          <div className="ds-card-header">
            <h3 className="ds-card-title">
              <BarChart3 size={18} style={{ marginRight: '8px', display: 'inline' }} />
              Capital Gains Analysis
            </h3>
            <div className="ds-card-actions">
              <button className="ds-btn ds-btn-sm ds-btn-ghost">
                <HelpCircle size={14} />
              </button>
            </div>
          </div>
          <div className="ds-card-body">
            <PieChartComponent
              data={gainsChartData}
              size={200}
              showLegend
            />
            <div className="ds-mt-4 ds-space-y-2">
              <div className="ds-flex-between ds-text-sm">
                <span className="ds-text-muted">Long-Term Rate:</span>
                <span className="ds-font-medium" style={{ color: COLORS.longTerm }}>15%</span>
              </div>
              <div className="ds-flex-between ds-text-sm">
                <span className="ds-text-muted">Short-Term Rate:</span>
                <span className="ds-font-medium" style={{ color: COLORS.shortTerm }}>28%</span>
              </div>
              <div className="ds-flex-between ds-text-sm">
                <span className="ds-text-muted">Wash Sale Adjustments:</span>
                <span className="ds-font-medium" style={{ color: COLORS.loss }}>
                  ${summary?.washSaleLoss.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="ds-card">
          <div className="ds-card-header">
            <h3 className="ds-card-title">
              <PieChart size={18} style={{ marginRight: '8px', display: 'inline' }} />
              Income Breakdown
            </h3>
          </div>
          <div className="ds-card-body">
            <PieChartComponent
              data={incomeChartData}
              size={200}
              showLegend
            />
            <div className="ds-mt-4 ds-space-y-2">
              <div className="ds-flex-between ds-text-sm">
                <span className="ds-text-muted">Qualified Div Rate:</span>
                <span className="ds-font-medium" style={{ color: COLORS.dividend }}>15%</span>
              </div>
              <div className="ds-flex-between ds-text-sm">
                <span className="ds-text-muted">Ordinary Income Rate:</span>
                <span className="ds-font-medium" style={{ color: COLORS.secondary }}>Marginal</span>
              </div>
              <div className="ds-flex-between ds-text-sm">
                <span className="ds-text-muted">Interest Income:</span>
                <span className="ds-font-medium" style={{ color: COLORS.interest }}>
                  ${summary?.interestIncome.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tax Bracket Visualization */}
      <div className="ds-card">
        <div className="ds-card-header">
          <h3 className="ds-card-title">
            <Landmark size={18} style={{ marginRight: '8px', display: 'inline' }} />
            Tax Bracket Analysis
          </h3>
          <span className="ds-badge ds-badge-info">2026 Tax Year</span>
        </div>
        <div className="ds-card-body">
          <div className="ds-space-y-3">
            {TAX_BRACKETS_2026.map((bracket, index) => {
              const progress = Math.min(100, Math.max(0, 
                ((summary?.totalGainLoss || 0) - bracket.minIncome) / (bracket.maxIncome - bracket.minIncome) * 100
              ));
              const isActive = summary && summary.totalGainLoss > bracket.minIncome;
              
              return (
                <div key={bracket.bracket} className="ds-space-y-1">
                  <div className="ds-flex-between ds-text-sm">
                    <span className={isActive ? 'ds-font-medium' : 'ds-text-muted'}>
                      {bracket.bracket} Bracket
                      {isActive && <span className="ds-ml-2 ds-badge ds-badge-sm ds-badge-primary">Active</span>}
                    </span>
                    <span className="ds-text-muted">
                      ${bracket.minIncome.toLocaleString()} - {bracket.maxIncome === Infinity ? '∞' : `$${bracket.maxIncome.toLocaleString()}`}
                    </span>
                  </div>
                  <div className="ds-progress-bar">
                    <div 
                      className="ds-progress-fill"
                      style={{ 
                        width: `${progress}%`,
                        backgroundColor: isActive ? COLORS.primary : 'var(--fa)',
                        opacity: isActive ? 1 : 0.5
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="ds-card">
        <div className="ds-card-header">
          <h3 className="ds-card-title">Quick Actions</h3>
        </div>
        <div className="ds-card-body">
          <div className="ds-grid-4">
            <button className="ds-btn ds-btn-primary" onClick={handleExport8949}>
              <FileText size={16} />
              Export Form 8949
            </button>
            <button className="ds-btn ds-btn-primary" onClick={handleExportScheduleD}>
              <FileText size={16} />
              Export Schedule D
            </button>
            <button className="ds-btn ds-btn-secondary" onClick={handleCaptureReceipt}>
              <Camera size={16} />
              Capture Receipt
            </button>
            <button className="ds-btn ds-btn-secondary" onClick={handleRefreshCalculations}>
              <RefreshCw size={16} />
              Refresh Calculations
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTransactions = () => {
    const columns = [
      { key: 'date', header: 'Date', sortable: true, width: '100px' },
      { key: 'symbol', header: 'Symbol', sortable: true, width: '80px' },
      { key: 'type', header: 'Type', sortable: true, width: '100px' },
      { key: 'shares', header: 'Shares', sortable: true, width: '80px', align: 'right' as const },
      { key: 'price', header: 'Price', sortable: true, width: '100px', align: 'right' as const, format: 'currency' as const },
      { key: 'total', header: 'Total', sortable: true, width: '120px', align: 'right' as const, format: 'currency' as const },
      { key: 'gainLoss', header: 'Gain/Loss', sortable: true, width: '120px', align: 'right' as const, format: 'currency' as const },
      { key: 'holdingPeriod', header: 'Hold Days', sortable: true, width: '90px', align: 'right' as const },
      { key: 'isLongTerm', header: 'Term', sortable: true, width: '80px' },
      { key: 'estimatedTax', header: 'Est. Tax', sortable: true, width: '100px', align: 'right' as const, format: 'currency' as const },
      { key: 'status', header: 'Status', sortable: true, width: '100px' },
    ];

    const bulkActions = [
      { label: 'Mark as Filed', action: () => toast.success('Transactions marked as filed') },
      { label: 'Export Selected', action: () => toast.success('Selected transactions exported') },
      { label: 'Recalculate', action: () => toast.success('Tax calculations updated') },
    ];

    return (
      <div className="ds-space-y-4">
        {/* Filters */}
        <div className="ds-flex-between ds-flex-wrap">
          <div className="ds-flex" style={{ gap: '12px' }}>
            <select 
              className="ds-input ds-input-sm"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
              <option value="dividend">Dividend</option>
              <option value="interest">Interest</option>
            </select>
            <select 
              className="ds-input ds-input-sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="calculated">Calculated</option>
              <option value="filed">Filed</option>
            </select>
          </div>
          <div className="ds-flex" style={{ gap: '8px' }}>
            <button className="ds-btn ds-btn-sm ds-btn-ghost" onClick={handleRefreshCalculations}>
              <RefreshCw size={14} />
            </button>
            <button className="ds-btn ds-btn-sm ds-btn-secondary">
              <Download size={14} />
              Export All
            </button>
          </div>
        </div>

        {/* Data Table */}
        <DataTable
          columns={columns}
          data={filteredTransactions}
          loading={transactionsLoading}
          selectable
          selectedIds={selectedTransactions}
          onSelect={handleTransactionSelect}
          onSelectAll={handleSelectAll}
          bulkActions={
            <BulkActions 
              selectedCount={selectedTransactions.size}
              actions={bulkActions}
            />
          }
          onRowClick={(row) => {
            setSelectedTransaction(row as TaxTransaction);
          }}
          rowClassName={(row) => {
            const t = row as TaxTransaction;
            if (t.gainLoss > 0) return 'ds-row-gain';
            if (t.gainLoss < 0) return 'ds-row-loss';
            return '';
          }}
        />
      </div>
    );
  };

  const renderForms = () => (
    <div className="ds-grid-2">
      <div className="ds-card">
        <div className="ds-card-header">
          <h3 className="ds-card-title">
            <FileText size={18} style={{ marginRight: '8px', display: 'inline' }} />
            Form 8949 - Sales and Dispositions
          </h3>
          <span className="ds-badge ds-badge-success">Ready</span>
        </div>
        <div className="ds-card-body ds-space-y-4">
          <p className="ds-text-muted ds-text-sm">
            Reports sales and exchanges of capital assets. Includes short-term and long-term transactions.
          </p>
          <div className="ds-stats">
            <div className="ds-stat">
              <span className="ds-stat-label">Short-term Transactions</span>
              <span className="ds-stat-value">12</span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Long-term Transactions</span>
              <span className="ds-stat-value">18</span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Total Proceeds</span>
              <span className="ds-stat-value">${summary?.totalProceeds.toLocaleString()}</span>
            </div>
          </div>
          <button className="ds-btn ds-btn-primary ds-btn-block" onClick={handleExport8949}>
            <Download size={16} />
            Download Form 8949 (PDF)
          </button>
        </div>
      </div>

      <div className="ds-card">
        <div className="ds-card-header">
          <h3 className="ds-card-title">
            <FileText size={18} style={{ marginRight: '8px', display: 'inline' }} />
            Schedule D - Capital Gains
          </h3>
          <span className="ds-badge ds-badge-success">Ready</span>
        </div>
        <div className="ds-card-body ds-space-y-4">
          <p className="ds-text-muted ds-text-sm">
            Summarizes capital gains and losses from Form 8949. Calculates net capital gain or loss.
          </p>
          <div className="ds-stats">
            <div className="ds-stat">
              <span className="ds-stat-label">Net Short-term</span>
              <span className="ds-stat-value" style={{ color: summary && summary.shortTermGains > 0 ? COLORS.gain : COLORS.loss }}>
                ${summary?.shortTermGains.toLocaleString()}
              </span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Net Long-term</span>
              <span className="ds-stat-value" style={{ color: summary && summary.longTermGains > 0 ? COLORS.gain : COLORS.loss }}>
                ${summary?.longTermGains.toLocaleString()}
              </span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Total Gain/Loss</span>
              <span className="ds-stat-value" style={{ color: summary && summary.totalGainLoss > 0 ? COLORS.gain : COLORS.loss }}>
                ${summary?.totalGainLoss.toLocaleString()}
              </span>
            </div>
          </div>
          <button className="ds-btn ds-btn-primary ds-btn-block" onClick={handleExportScheduleD}>
            <Download size={16} />
            Download Schedule D (PDF)
          </button>
        </div>
      </div>

      <div className="ds-card">
        <div className="ds-card-header">
          <h3 className="ds-card-title">
            <ReceiptIcon size={18} style={{ marginRight: '8px', display: 'inline' }} />
            Form 1099-DIV - Dividends
          </h3>
          <span className="ds-badge ds-badge-warning">Pending</span>
        </div>
        <div className="ds-card-body ds-space-y-4">
          <p className="ds-text-muted ds-text-sm">
            Reports dividend income from stocks and mutual funds.
          </p>
          <div className="ds-stats">
            <div className="ds-stat">
              <span className="ds-stat-label">Total Dividends</span>
              <span className="ds-stat-value">
                ${((summary?.qualifiedDividends || 0) + (summary?.ordinaryDividends || 0)).toLocaleString()}
              </span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Qualified</span>
              <span className="ds-stat-value" style={{ color: COLORS.dividend }}>
                ${summary?.qualifiedDividends.toLocaleString()}
              </span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Ordinary</span>
              <span className="ds-stat-value" style={{ color: COLORS.secondary }}>
                ${summary?.ordinaryDividends.toLocaleString()}
              </span>
            </div>
          </div>
          <button className="ds-btn ds-btn-secondary ds-btn-block" disabled>
            <Clock size={16} />
            Available Jan 31, 2027
          </button>
        </div>
      </div>

      <div className="ds-card">
        <div className="ds-card-header">
          <h3 className="ds-card-title">
            <Wallet size={18} style={{ marginRight: '8px', display: 'inline' }} />
            Form 1099-INT - Interest
          </h3>
          <span className="ds-badge ds-badge-warning">Pending</span>
        </div>
        <div className="ds-card-body ds-space-y-4">
          <p className="ds-text-muted ds-text-sm">
            Reports interest income from savings accounts, bonds, and other interest-bearing investments.
          </p>
          <div className="ds-stats">
            <div className="ds-stat">
              <span className="ds-stat-label">Total Interest</span>
              <span className="ds-stat-value" style={{ color: COLORS.interest }}>
                ${summary?.interestIncome.toLocaleString()}
              </span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Tax-Exempt</span>
              <span className="ds-stat-value">$0</span>
            </div>
            <div className="ds-stat">
              <span className="ds-stat-label">Sources</span>
              <span className="ds-stat-value">3 accounts</span>
            </div>
          </div>
          <button className="ds-btn ds-btn-secondary ds-btn-block" disabled>
            <Clock size={16} />
            Available Jan 31, 2027
          </button>
        </div>
      </div>
    </div>
  );

  const renderDeductions = () => (
    <div className="ds-space-y-4">
      <div className="ds-flex-between">
        <div className="ds-flex" style={{ gap: '12px' }}>
          <div className="ds-stat-card">
            <span className="ds-stat-label">Total Deductions</span>
            <span className="ds-stat-value">${metrics?.totalDeductions.toLocaleString()}</span>
          </div>
          <div className="ds-stat-card">
            <span className="ds-stat-label">Tax Savings</span>
            <span className="ds-stat-value" style={{ color: COLORS.gain }}>
              ~${metrics?.savingsFromDeductions.toFixed(0)}
            </span>
          </div>
        </div>
        <button className="ds-btn ds-btn-primary" onClick={handleCaptureReceipt}>
          <Camera size={16} />
          Add Receipt
        </button>
      </div>

      <div className="ds-card">
        <div className="ds-card-body">
          <table className="ds-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Receipt</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {deductions?.map((deduction) => (
                <tr key={deduction.id}>
                  <td>
                    <span className="ds-tag ds-tag-secondary">{deduction.category}</span>
                  </td>
                  <td>{deduction.description}</td>
                  <td className="ds-text-right ds-font-medium">
                    ${deduction.amount.toLocaleString()}
                  </td>
                  <td>{deduction.date}</td>
                  <td>
                    {deduction.receipt ? (
                      <button className="ds-btn ds-btn-xs ds-btn-ghost">
                        <FileText size={12} />
                        View
                      </button>
                    ) : (
                      <span className="ds-text-muted">-</span>
                    )}
                  </td>
                  <td>
                    <span className={`ds-badge ds-badge-sm ds-badge-${deduction.status === 'verified' ? 'success' : 'warning'}`}>
                      {deduction.status === 'verified' ? (
                        <><CheckCircle size={10} /> Verified</>
                      ) : (
                        <><Clock size={10} /> Pending</>
                      )}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="ds-card ds-card-info">
        <div className="ds-card-body">
          <div className="ds-flex" style={{ gap: '12px', alignItems: 'flex-start' }}>
            <HelpCircle size={20} style={{ color: COLORS.primary, flexShrink: 0 }} />
            <div>
              <h4 className="ds-font-medium ds-mb-1">Investment Expense Deductions</h4>
              <p className="ds-text-sm ds-text-muted">
                Certain investment-related expenses may be deductible. Keep receipts for:
                investment advisory fees, trading platform subscriptions, financial education,
                and home office expenses related to investment activities.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderReceipts = () => (
    <div className="ds-space-y-4">
      <div className="ds-card ds-card-dashed" onClick={handleCaptureReceipt} style={{ cursor: 'pointer' }}>
        <div className="ds-card-body ds-text-center ds-py-8">
          <div className="ds-mb-4" style={{ 
            width: '64px', 
            height: '64px', 
            borderRadius: '50%', 
            background: 'var(--bg3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto'
          }}>
            <ScanLine size={32} style={{ color: COLORS.primary }} />
          </div>
          <h3 className="ds-font-medium ds-mb-2">Capture Receipt</h3>
          <p className="ds-text-sm ds-text-muted ds-mb-4">
            Take a photo or upload a receipt for automatic OCR processing
          </p>
          <button className="ds-btn ds-btn-primary">
            <Camera size={16} />
            Scan Receipt
          </button>
        </div>
      </div>

      <div className="ds-grid-3">
        {[
          { category: 'Trading Fees', count: 12, total: 450 },
          { category: 'Advisory', count: 3, total: 1200 },
          { category: 'Software', count: 5, total: 750 },
          { category: 'Education', count: 2, total: 599 },
          { category: 'Home Office', count: 1, total: 850 },
        ].map((category) => (
          <div key={category.category} className="ds-card ds-card-hover">
            <div className="ds-card-body">
              <div className="ds-flex-between ds-mb-2">
                <span className="ds-tag ds-tag-secondary">{category.category}</span>
                <span className="ds-text-sm ds-text-muted">{category.count} receipts</span>
              </div>
              <div className="ds-font-medium ds-text-lg">
                ${category.total.toLocaleString()}
              </div>
              <div className="ds-text-xs ds-text-muted">
                Total deductions
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="ds-page tax-dashboard">
      {/* Header */}
      <div className="ds-page-header">
        <div className="ds-flex-between ds-flex-wrap">
          <div>
            <h1 className="ds-page-title">
              <Calculator size={24} style={{ marginRight: '12px', display: 'inline', verticalAlign: 'middle' }} />
              Tax Dashboard
            </h1>
            <p className="ds-page-subtitle">
              Real-time tax calculations and filing preparation
            </p>
          </div>
          <div className="ds-flex" style={{ gap: '12px' }}>
            <select 
              className="ds-input ds-input-sm"
              value={taxYear}
              onChange={(e) => setTaxYear(e.target.value)}
            >
              <option value="2026">2026 Tax Year</option>
              <option value="2025">2025 Tax Year</option>
              <option value="2024">2024 Tax Year</option>
            </select>
            <select 
              className="ds-input ds-input-sm"
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
            >
              <option value="US">United States</option>
              <option value="UK">United Kingdom</option>
              <option value="CA">Canada</option>
              <option value="AU">Australia</option>
            </select>
            <button className="ds-btn ds-btn-ghost ds-btn-sm">
              <Bell size={16} />
            </button>
            <button className="ds-btn ds-btn-ghost ds-btn-sm">
              <Settings size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="ds-tabs">
        <button 
          className={`ds-tab ${activeTab === 'overview' ? 'ds-tab-active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <PieChart size={16} />
          Overview
        </button>
        <button 
          className={`ds-tab ${activeTab === 'transactions' ? 'ds-tab-active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          <ArrowRightLeft size={16} />
          Transactions
          <span className="ds-badge ds-badge-sm ds-badge-secondary">
            {transactions?.length || 0}
          </span>
        </button>
        <button 
          className={`ds-tab ${activeTab === 'forms' ? 'ds-tab-active' : ''}`}
          onClick={() => setActiveTab('forms')}
        >
          <FileText size={16} />
          Tax Forms
        </button>
        <button 
          className={`ds-tab ${activeTab === 'deductions' ? 'ds-tab-active' : ''}`}
          onClick={() => setActiveTab('deductions')}
        >
          <Receipt size={16} />
          Deductions
          <span className="ds-badge ds-badge-sm ds-badge-secondary">
            {deductions?.length || 0}
          </span>
        </button>
        <button 
          className={`ds-tab ${activeTab === 'receipts' ? 'ds-tab-active' : ''}`}
          onClick={() => setActiveTab('receipts')}
        >
          <Camera size={16} />
          Receipts
        </button>
      </div>

      {/* Content */}
      <div className="ds-page-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'transactions' && renderTransactions()}
        {activeTab === 'forms' && renderForms()}
        {activeTab === 'deductions' && renderDeductions()}
        {activeTab === 'receipts' && renderReceipts()}
      </div>

      {/* Transaction Detail Modal */}
      {selectedTransaction && (
        <DetailModal
          isOpen={!!selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
          title={`Transaction Details: ${selectedTransaction.symbol}`}
          data={selectedTransaction}
          renderField={(key, value) => {
            if (key === 'gainLoss') {
              return (
                <span style={{ color: value >= 0 ? COLORS.gain : COLORS.loss }}>
                  {value >= 0 ? '+' : ''}${value.toLocaleString()}
                </span>
              );
            }
            if (['total', 'costBasis', 'estimatedTax', 'price'].includes(key)) {
              return `$${(value as number).toLocaleString()}`;
            }
            if (key === 'isLongTerm') {
              return value ? (
                <span style={{ color: COLORS.longTerm }}>Long-Term</span>
              ) : (
                <span style={{ color: COLORS.shortTerm }}>Short-Term</span>
              );
            }
            return String(value);
          }}
          actions={[
            { label: 'View Receipt', action: () => toast.success('Receipt viewer opened') },
            { label: 'Edit', action: () => toast.success('Transaction editor opened') },
            { label: 'Mark as Filed', action: () => toast.success('Transaction marked as filed') },
          ]}
        />
      )}

      {/* Receipt Capture Modal */}
      <Modal
        isOpen={showReceiptModal}
        onClose={() => setShowReceiptModal(false)}
        title="Capture Receipt"
        size="lg"
      >
        <div className="ds-space-y-4">
          <div className="ds-upload-area" style={{
            border: '2px dashed var(--bo)',
            borderRadius: 'var(--rad)',
            padding: '48px',
            textAlign: 'center',
            background: 'var(--bg2)'
          }}>
            <Camera size={48} style={{ color: COLORS.primary, marginBottom: '16px' }} />
            <h4 className="ds-font-medium ds-mb-2">Upload or Capture Receipt</h4>
            <p className="ds-text-sm ds-text-muted ds-mb-4">
              Drag and drop an image, or click to browse. We'll automatically extract
              the relevant information using OCR.
            </p>
            <button className="ds-btn ds-btn-primary">
              Choose File
            </button>
          </div>

          <div className="ds-card">
            <div className="ds-card-header">
              <h4 className="ds-card-title">Recent Captures</h4>
            </div>
            <div className="ds-card-body">
              <div className="ds-list">
                {[
                  { name: 'Trading_Fees_Q1.pdf', date: '2026-03-15', status: 'processed', amount: 150 },
                  { name: 'Advisory_Receipt.jpg', date: '2026-02-20', status: 'processed', amount: 1200 },
                  { name: 'Software_License.png', date: '2026-03-01', status: 'pending', amount: null },
                ].map((receipt, idx) => (
                  <div key={idx} className="ds-list-item ds-flex-between">
                    <div className="ds-flex" style={{ gap: '12px', alignItems: 'center' }}>
                      <FileText size={20} style={{ color: COLORS.primary }} />
                      <div>
                        <div className="ds-font-medium">{receipt.name}</div>
                        <div className="ds-text-xs ds-text-muted">{receipt.date}</div>
                      </div>
                    </div>
                    <div className="ds-flex" style={{ gap: '12px', alignItems: 'center' }}>
                      {receipt.amount && (
                        <span className="ds-font-medium">${receipt.amount}</span>
                      )}
                      <span className={`ds-badge ds-badge-sm ds-badge-${receipt.status === 'processed' ? 'success' : 'warning'}`}>
                        {receipt.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
}
