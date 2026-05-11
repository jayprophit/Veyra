import React, { useEffect, useRef } from 'react';

// Chart.js type declarations for minimal implementation
interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
  tension?: number;
}

interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

interface ChartOptions {
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  plugins?: {
    legend?: {
      display?: boolean;
      position?: 'top' | 'bottom' | 'left' | 'right';
    };
  };
  scales?: {
    x?: {
      display?: boolean;
      grid?: { color?: string };
      ticks?: { color?: string };
    };
    y?: {
      display?: boolean;
      grid?: { color?: string };
      ticks?: { color?: string };
    };
  };
}

interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut';
  data: ChartData;
  options?: ChartOptions;
}

// Simple Chart component using canvas API
// In production, you'd use Chart.js library
interface LineChartProps {
  data: { label: string; value: number }[];
  title?: string;
  color?: string;
  height?: number;
}

export const LineChart: React.FC<LineChartProps> = ({
  data,
  title,
  color = '#FF6000',
  height = 250,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || data.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;

    const maxValue = Math.max(...data.map(d => d.value));
    const minValue = Math.min(...data.map(d => d.value));
    const valueRange = maxValue - minValue || 1;

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;

    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(padding + chartWidth, y);
      ctx.stroke();
    }

    // Draw line
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.forEach((point, index) => {
      const x = padding + (chartWidth / (data.length - 1 || 1)) * index;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();

    // Draw fill
    ctx.fillStyle = color + '20'; // Add transparency
    ctx.lineTo(padding + chartWidth, padding + chartHeight);
    ctx.lineTo(padding, padding + chartHeight);
    ctx.closePath();
    ctx.fill();

    // Draw points
    data.forEach((point, index) => {
      const x = padding + (chartWidth / (data.length - 1 || 1)) * index;
      const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fill();
    });

    // Draw labels
    ctx.fillStyle = '#8892AD';
    ctx.font = '11px Outfit, sans-serif';
    ctx.textAlign = 'center';

    const labelInterval = Math.ceil(data.length / 6);
    data.forEach((point, index) => {
      if (index % labelInterval === 0) {
        const x = padding + (chartWidth / (data.length - 1 || 1)) * index;
        ctx.fillText(point.label, x, canvas.height - 10);
      }
    });
  }, [data, color]);

  return (
    <div className="ds-chart-box">
      {title && <div className="ds-chart-title">{title}</div>}
      <div className="ds-chart-wrap" style={{ height }}>
        <canvas
          ref={canvasRef}
          width={600}
          height={height}
          style={{ width: '100%', height: '100%' }}
        />
      </div>
    </div>
  );
};

interface BarChartProps {
  data: { label: string; value: number; color?: string }[];
  title?: string;
  height?: number;
}

export const BarChart: React.FC<BarChartProps> = ({
  data,
  title,
  height = 250,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || data.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const padding = 40;
    const chartWidth = canvas.width - padding * 2;
    const chartHeight = canvas.height - padding * 2;

    const maxValue = Math.max(...data.map(d => d.value));
    const barWidth = chartWidth / data.length * 0.7;
    const barSpacing = chartWidth / data.length * 0.3;

    // Draw bars
    data.forEach((point, index) => {
      const x = padding + index * (barWidth + barSpacing) + barSpacing / 2;
      const barHeight = (point.value / maxValue) * chartHeight;
      const y = padding + chartHeight - barHeight;

      // Bar
      ctx.fillStyle = point.color || '#4361EE';
      ctx.fillRect(x, y, barWidth, barHeight);

      // Label
      ctx.fillStyle = '#8892AD';
      ctx.font = '10px Outfit, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(point.label.slice(0, 8), x + barWidth / 2, canvas.height - 10);

      // Value
      ctx.fillStyle = '#F0F2FF';
      ctx.fillText(point.value.toString(), x + barWidth / 2, y - 5);
    });
  }, [data]);

  return (
    <div className="ds-chart-box">
      {title && <div className="ds-chart-title">{title}</div>}
      <div className="ds-chart-wrap" style={{ height }}>
        <canvas
          ref={canvasRef}
          width={600}
          height={height}
          style={{ width: '100%', height: '100%' }}
        />
      </div>
    </div>
  );
};

interface PieChartProps {
  data: { label: string; value: number; color: string }[];
  title?: string;
  height?: number;
  size?: number;
  showLegend?: boolean;
}

export const PieChart: React.FC<PieChartProps> = ({
  data,
  title,
  height = 220,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || data.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;

    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = -Math.PI / 2;

    data.forEach(item => {
      const sliceAngle = (item.value / total) * Math.PI * 2;

      // Draw slice
      ctx.fillStyle = item.color;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      ctx.closePath();
      ctx.fill();

      // Draw label
      const labelAngle = currentAngle + sliceAngle / 2;
      const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
      const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);

      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 11px Outfit, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${Math.round((item.value / total) * 100)}%`, labelX, labelY);

      currentAngle += sliceAngle;
    });
  }, [data]);

  return (
    <div className="ds-chart-box">
      {title && <div className="ds-chart-title">{title}</div>}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ height, flex: 1 }}>
          <canvas
            ref={canvasRef}
            width={220}
            height={height}
            style={{ width: '100%', height: '100%' }}
          />
        </div>
        <div style={{ minWidth: '120px' }}>
          {data.map(item => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <div style={{ width: 12, height: 12, background: item.color, borderRadius: 2 }} />
              <span style={{ fontSize: '0.75rem', color: 'var(--ds-text-muted)' }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Stat card with trend indicator
interface StatCardProps {
  title?: string;
  value: string | number;
  label?: string;
  subtext?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  format?: string;
  icon?: React.ReactNode;
  color?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  label,
  subtext,
  trend,
  trendValue,
  format,
  icon,
  color,
}) => {
  const getTrendColor = () => {
    if (trend === 'up') return 'var(--ds-success)';
    if (trend === 'down') return 'var(--ds-danger)';
    return 'var(--ds-text-muted)';
  };

  const getTrendIcon = () => {
    if (trend === 'up') return '↑';
    if (trend === 'down') return '↓';
    return '→';
  };

  return (
    <div className="ds-stat-card" style={{ borderLeft: color ? `4px solid ${color}` : undefined }}>
      <div className="ds-stat-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        {title && <div className="ds-stat-title" style={{ fontSize: '0.875rem', fontWeight: '500' }}>{title}</div>}
        {icon && <div className="ds-stat-icon">{icon}</div>}
      </div>
      <div className="ds-stat-value" style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '4px' }}>
        {format ? (typeof value === 'number' ? value.toLocaleString() : value) : value}
      </div>
      <div className="ds-stat-label" style={{ fontSize: '0.875rem', color: 'var(--ds-text-muted)', marginBottom: '8px' }}>
        {label || title}
      </div>
      {(subtext || trend) && (
        <div className="ds-stat-sub" style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem' }}>
          {trend && (
            <span style={{ color: getTrendColor() }}>
              {getTrendIcon()} {trendValue}
            </span>
          )}
          {subtext && <span>{subtext}</span>}
        </div>
      )}
    </div>
  );
};

// Date range selector
interface DateRangeProps {
  value: '7d' | '30d' | '90d' | 'all';
  onChange: (value: '7d' | '30d' | '90d' | 'all') => void;
}

export const DateRangeSelector: React.FC<DateRangeProps> = ({ value, onChange }) => {
  const options: { key: '7d' | '30d' | '90d' | 'all'; label: string }[] = [
    { key: '7d', label: '7D' },
    { key: '30d', label: '30D' },
    { key: '90d', label: '90D' },
    { key: 'all', label: 'All' },
  ];

  return (
    <div style={{ display: 'flex', background: 'var(--ds-bg-3)', borderRadius: '8px', padding: '3px' }}>
      {options.map(option => (
        <button
          key={option.key}
          onClick={() => onChange(option.key)}
          style={{
            padding: '4px 12px',
            borderRadius: '6px',
            border: 'none',
            background: value === option.key ? 'var(--ds-bg-4)' : 'transparent',
            color: value === option.key ? 'var(--ds-text)' : 'var(--ds-text-muted)',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.12s',
          }}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};
