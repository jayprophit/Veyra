import React, { useState, useMemo } from 'react';
import { useQuery } from 'react-query';
import { TrendingUp, TrendingDown, DollarSign, Activity, Download, Filter } from 'lucide-react';
import { api } from '../services/api';
import { DataTable, BulkActions } from '../components/UI/DataTable';
import { Modal, QualityScore } from '../components/UI/Modal';
import { LineChart, PieChart, StatCard, DateRangeSelector } from '../components/UI/ChartWidgets';
import { useLocalStorage } from '../hooks/useLocalStorage';

// Mock data generator for demo
const generateMockPositions = () => [
  { id: '1', symbol: 'AAPL', name: 'Apple Inc.', quantity: 100, avg_cost: 150.00, current_price: 175.50, market_value: 17550, unrealized_pnl: 2550, unrealized_pnl_pct: 17.0, sector: 'Technology', quality_score: 0.92 },
  { id: '2', symbol: 'MSFT', name: 'Microsoft Corp.', quantity: 50, avg_cost: 280.00, current_price: 310.25, market_value: 15512.50, unrealized_pnl: 1512.50, unrealized_pnl_pct: 10.8, sector: 'Technology', quality_score: 0.95 },
  { id: '3', symbol: 'GOOGL', name: 'Alphabet Inc.', quantity: 25, avg_cost: 120.00, current_price: 135.80, market_value: 3395, unrealized_pnl: 395, unrealized_pnl_pct: 13.2, sector: 'Technology', quality_score: 0.88 },
  { id: '4', symbol: 'AMZN', name: 'Amazon.com', quantity: 40, avg_cost: 140.00, current_price: 145.20, market_value: 5808, unrealized_pnl: 208, unrealized_pnl_pct: 3.7, sector: 'Consumer', quality_score: 0.85 },
  { id: '5', symbol: 'TSLA', name: 'Tesla Inc.', quantity: 30, avg_cost: 220.00, current_price: 195.00, market_value: 5850, unrealized_pnl: -750, unrealized_pnl_pct: -11.4, sector: 'Automotive', quality_score: 0.72 },
  { id: '6', symbol: 'NVDA', name: 'NVIDIA Corp.', quantity: 20, avg_cost: 400.00, current_price: 480.00, market_value: 9600, unrealized_pnl: 1600, unrealized_pnl_pct: 20.0, sector: 'Technology', quality_score: 0.90 },
  { id: '7', symbol: 'JPM', name: 'JPMorgan Chase', quantity: 60, avg_cost: 145.00, current_price: 152.30, market_value: 9138, unrealized_pnl: 438, unrealized_pnl_pct: 5.0, sector: 'Financial', quality_score: 0.87 },
  { id: '8', symbol: 'JNJ', name: 'Johnson & Johnson', quantity: 45, avg_cost: 165.00, current_price: 158.50, market_value: 7132.50, unrealized_pnl: -292.50, unrealized_pnl_pct: -3.9, sector: 'Healthcare', quality_score: 0.83 },
];

const generatePerformanceData = () => {
  const data = [];
  let value = 95000;
  for (let i = 0; i < 30; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (30 - i));
    value = value * (1 + (Math.random() - 0.45) * 0.02);
    data.push({
      label: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      value: Math.round(value),
    });
  }
  return data;
};

interface Position {
  id: string;
  symbol: string;
  name: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  sector: string;
  quality_score: number;
}

export const EnhancedPortfolioPage: React.FC = () => {
  const [dateRange, setDateRange] = useLocalStorage<'7d' | '30d' | '90d' | 'all'>('fm_dateRange', '30d');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);
  const [filterSector, setFilterSector] = useState<string>('all');
  
  // Fetch data
  const { data: portfolioData, isLoading } = useQuery('portfolio-enhanced', () =>
    api.get('/portfolio').then((res) => res.data).catch(() => ({
      total_value: 73986,
      day_pnl: 1250,
      positions: generateMockPositions(),
    }))
  );

  const positions = portfolioData?.positions || generateMockPositions();
  const performanceData = useMemo(() => generatePerformanceData(), []);

  // Calculate allocation data
  const allocationData = useMemo(() => {
    const sectors: Record<string, number> = {};
    positions.forEach((pos: Position) => {
      sectors[pos.sector] = (sectors[pos.sector] || 0) + pos.market_value;
    });
    const colors = ['#FF6000', '#4361EE', '#0D9488', '#D97706', '#DC2626', '#8B5CF6'];
    return Object.entries(sectors).map(([label, value], idx) => ({
      label,
      value,
      color: colors[idx % colors.length],
    }));
  }, [positions]);

  // Filter positions
  const filteredPositions = useMemo(() => {
    if (filterSector === 'all') return positions;
    return positions.filter((pos: Position) => pos.sector === filterSector);
  }, [positions, filterSector]);

  // Calculate totals
  const totalValue = positions.reduce((sum: number, pos: Position) => sum + pos.market_value, 0);
  const totalPnL = positions.reduce((sum: number, pos: Position) => sum + pos.unrealized_pnl, 0);
  const totalPnLPct = (totalPnL / (totalValue - totalPnL)) * 100;

  // DataTable columns
  const columns = [
    { key: 'symbol', header: 'Symbol', sortable: true },
    { key: 'name', header: 'Name', sortable: true, width: '200px' },
    { key: 'sector', header: 'Sector', sortable: true },
    { key: 'quantity', header: 'Qty', sortable: true, render: (row: Position) => row.quantity.toLocaleString() },
    { key: 'avg_cost', header: 'Avg Cost', sortable: true, render: (row: Position) => `$${row.avg_cost.toFixed(2)}` },
    { key: 'current_price', header: 'Price', sortable: true, render: (row: Position) => `$${row.current_price.toFixed(2)}` },
    { key: 'market_value', header: 'Value', sortable: true, render: (row: Position) => `$${row.market_value.toLocaleString()}` },
    { key: 'unrealized_pnl', header: 'P&L ($)', sortable: true, render: (row: Position) => (
      <span style={{ color: row.unrealized_pnl >= 0 ? 'var(--ds-success)' : 'var(--ds-danger)' }}>
        {row.unrealized_pnl >= 0 ? '+' : ''}${row.unrealized_pnl.toLocaleString()}
      </span>
    )},
    { key: 'unrealized_pnl_pct', header: 'P&L %', sortable: true, render: (row: Position) => (
      <span style={{ color: row.unrealized_pnl_pct >= 0 ? 'var(--ds-success)' : 'var(--ds-danger)' }}>
        {row.unrealized_pnl_pct >= 0 ? '↑' : '↓'} {Math.abs(row.unrealized_pnl_pct).toFixed(1)}%
      </span>
    )},
    { key: 'quality_score', header: 'Quality', sortable: true, render: (row: Position) => (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div className="ds-quality-bar">
          <div 
            className="ds-quality-fill" 
            style={{ 
              width: `${Math.round(row.quality_score * 100)}%`,
              background: row.quality_score >= 0.8 ? 'var(--ds-success)' : row.quality_score >= 0.5 ? 'var(--ds-warning)' : 'var(--ds-danger)'
            }} 
          />
        </div>
        <span className="ds-mono" style={{ fontSize: '0.75rem' }}>{Math.round(row.quality_score * 100)}%</span>
      </div>
    )},
  ];

  const sectors = ['all', ...new Set(positions.map((p: Position) => p.sector))];

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px' }}>
        <div className="animate-pulse" style={{ fontSize: '1.2rem', color: 'var(--ds-text-muted)' }}>
          Loading portfolio...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 ds-animate-in">
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 className="ds-display" style={{ fontSize: '1.3rem', fontWeight: 700 }}>Portfolio Overview</h2>
          <p style={{ fontSize: '0.83rem', color: 'var(--ds-text-muted)' }}>Real-time position tracking with quality metrics</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <DateRangeSelector value={dateRange} onChange={setDateRange} />
          <button className="ds-btn ds-btn-secondary ds-btn-sm">
            <Download size={14} /> Export
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="ds-grid-responsive">
        <StatCard
          value={`$${totalValue.toLocaleString()}`}
          label="Total Portfolio Value"
          trend={totalPnL >= 0 ? 'up' : 'down'}
          trendValue={`${Math.abs(totalPnLPct).toFixed(2)}%`}
          subtext="vs cost basis"
        />
        <StatCard
          value={`$${Math.abs(totalPnL).toLocaleString()}`}
          label="Unrealized P&L"
          trend={totalPnL >= 0 ? 'up' : 'down'}
          trendValue={`${totalPnL >= 0 ? '+' : '-'}$${Math.abs(totalPnL).toLocaleString()}`}
        />
        <StatCard
          value={`${positions.length}`}
          label="Active Positions"
          subtext={`${sectors.length - 1} sectors`}
        />
        <StatCard
          value={`${Math.round((positions.filter((p: Position) => p.unrealized_pnl >= 0).length / positions.length) * 100)}%`}
          label="Win Rate"
          trend="neutral"
          trendValue={`${positions.filter((p: Position) => p.unrealized_pnl >= 0).length}/${positions.length}`}
        />
      </div>

      {/* Charts */}
      <div className="ds-grid-2">
        <LineChart
          data={performanceData}
          title="Portfolio Performance"
          color="#FF6000"
          height={280}
        />
        <PieChart
          data={allocationData}
          title="Sector Allocation"
          height={280}
        />
      </div>

      {/* Filter Bar */}
      <div className="ds-chip-bar">
        <span style={{ fontSize: '0.76rem', color: 'var(--ds-text-muted)' }}>
          <Filter size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />
          Filter:
        </span>
        {sectors.map(sector => (
          <div
            key={sector}
            className={`ds-chip ${filterSector === sector ? 'active' : ''}`}
            onClick={() => setFilterSector(sector)}
          >
            {sector === 'all' ? 'All Sectors' : sector}
          </div>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: '0.76rem', color: 'var(--ds-text-muted)' }}>
          {filteredPositions.length} positions
        </span>
      </div>

      {/* Bulk Actions */}
      <BulkActions
        selectedCount={selectedIds.length}
        onExport={() => {
          const selected = positions.filter((p: Position) => selectedIds.includes(p.id));
          const csv = selected.map((p: Position) => 
            `${p.symbol},${p.name},${p.quantity},${p.current_price},${p.market_value}`
          ).join('\n');
          const blob = new Blob([csv], { type: 'text/csv' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `positions-${new Date().toISOString().slice(0, 10)}.csv`;
          a.click();
        }}
        onDelete={() => {
          setSelectedIds([]);
          alert(`Deleted ${selectedIds.length} positions (demo)`);
        }}
      />

      {/* Positions Table */}
      <DataTable
        columns={columns}
        data={filteredPositions}
        keyExtractor={(row: Position) => row.id}
        selectable
        onSelect={setSelectedIds}
        onRowClick={(row: Position) => setSelectedPosition(row)}
      />

      {/* Position Detail Modal */}
      {selectedPosition && (
        <Modal
          isOpen={!!selectedPosition}
          onClose={() => setSelectedPosition(null)}
          title={`${selectedPosition.symbol} - Position Details`}
          size="lg"
          footer={
            <>
              <button 
                className="ds-btn ds-btn-secondary ds-btn-sm"
                onClick={() => {
                  const csv = `Symbol,Name,Quantity,Avg Cost,Current Price,Market Value,P&L,P&L %\n${selectedPosition.symbol},${selectedPosition.name},${selectedPosition.quantity},${selectedPosition.avg_cost},${selectedPosition.current_price},${selectedPosition.market_value},${selectedPosition.unrealized_pnl},${selectedPosition.unrealized_pnl_pct}`;
                  const blob = new Blob([csv], { type: 'text/csv' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${selectedPosition.symbol}-position.csv`;
                  a.click();
                }}
              >
                <Download size={14} /> Export
              </button>
              <button className="ds-btn ds-btn-secondary ds-btn-sm" onClick={() => setSelectedPosition(null)}>
                Close
              </button>
            </>
          }
        >
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.85rem' }}>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Symbol:</span>
              <strong style={{ marginLeft: '8px' }}>{selectedPosition.symbol}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Company:</span>
              <strong style={{ marginLeft: '8px' }}>{selectedPosition.name}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Sector:</span>
              <span className="ds-tag ds-tag-info" style={{ marginLeft: '8px' }}>{selectedPosition.sector}</span>
            </div>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Quantity:</span>
              <strong style={{ marginLeft: '8px' }}>{selectedPosition.quantity.toLocaleString()}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Avg Cost:</span>
              <strong style={{ marginLeft: '8px' }}>${selectedPosition.avg_cost.toFixed(2)}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Current Price:</span>
              <strong style={{ marginLeft: '8px' }}>${selectedPosition.current_price.toFixed(2)}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Market Value:</span>
              <strong style={{ marginLeft: '8px' }}>${selectedPosition.market_value.toLocaleString()}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--ds-text-muted)' }}>Day's Change:</span>
              <strong style={{ marginLeft: '8px', color: selectedPosition.unrealized_pnl >= 0 ? 'var(--ds-success)' : 'var(--ds-danger)' }}>
                {selectedPosition.unrealized_pnl >= 0 ? '+' : ''}{selectedPosition.unrealized_pnl_pct.toFixed(2)}%
              </strong>
            </div>
          </div>
          
          <div style={{ marginTop: '20px' }}>
            <h4 style={{ fontSize: '0.85rem', marginBottom: '10px' }}>Position Quality Score</h4>
            <QualityScore 
              score={selectedPosition.quality_score}
              recommendation={selectedPosition.quality_score >= 0.8 
                ? 'Strong position with consistent performance'
                : selectedPosition.quality_score >= 0.5
                ? 'Moderate quality - monitor closely'
                : 'Consider reviewing position strategy'
              }
            />
          </div>

          <div className="ds-codebox" style={{ marginTop: '16px' }}>
            {JSON.stringify({
              id: selectedPosition.id,
              symbol: selectedPosition.symbol,
              metrics: {
                cost_basis: selectedPosition.avg_cost * selectedPosition.quantity,
                current_value: selectedPosition.market_value,
                total_return: selectedPosition.unrealized_pnl,
                total_return_pct: selectedPosition.unrealized_pnl_pct,
              },
              quality: selectedPosition.quality_score,
            }, null, 2)}
          </div>
        </Modal>
      )}
    </div>
  );
};

export default EnhancedPortfolioPage;
