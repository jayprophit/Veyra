import React, { useState, useCallback, useMemo } from 'react';
import { ChevronUp, ChevronDown, Copy, Check } from 'lucide-react';

interface Column<T> {
  key: string;
  header: string;
  width?: string;
  sortable?: boolean;
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T extends Record<string, unknown>> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  selectable?: boolean;
  onSelect?: (selectedIds: string[]) => void;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  className?: string;
}

type SortDirection = 'asc' | 'desc' | null;

interface SortState {
  key: string | null;
  direction: SortDirection;
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  keyExtractor,
  selectable = false,
  onSelect,
  onRowClick,
  emptyMessage = 'No data available',
  className = '',
}: DataTableProps<T>) {
  const [sort, setSort] = useState<SortState>({ key: null, direction: null });
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleSort = useCallback((key: string) => {
    setSort(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  }, []);

  const sortedData = useMemo(() => {
    if (!sort.key || !sort.direction) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sort.key!];
      const bVal = b[sort.key!];

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sort.direction === 'asc' ? aVal - bVal : bVal - aVal;
      }

      const aStr = String(aVal || '').toLowerCase();
      const bStr = String(bVal || '').toLowerCase();
      return sort.direction === 'asc' ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
  }, [data, sort]);

  const toggleSelection = useCallback((id: string) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      onSelect?.(Array.from(newSet));
      return newSet;
    });
  }, [onSelect]);

  const toggleAll = useCallback(() => {
    setSelectedIds(prev => {
      if (prev.size === data.length) {
        onSelect?.([]);
        return new Set();
      }
      const allIds = data.map(keyExtractor);
      onSelect?.(allIds);
      return new Set(allIds);
    });
  }, [data, keyExtractor, onSelect]);

  const copyToClipboard = useCallback(async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      console.error('Failed to copy to clipboard');
    }
  }, []);

  const renderCell = (row: T, column: Column<T>): React.ReactNode => {
    if (column.render) {
      return column.render(row);
    }

    const value = row[column.key];
    const stringValue = String(value ?? '-');

    return (
      <span
        className="copyable inline-flex items-center gap-1"
        onClick={(e) => {
          e.stopPropagation();
          copyToClipboard(stringValue, `${keyExtractor(row)}-${column.key}`);
        }}
        title="Click to copy"
      >
        {stringValue}
        {copiedId === `${keyExtractor(row)}-${column.key}` ? (
          <Check size={12} className="text-green-500" />
        ) : (
          <Copy size={12} className="opacity-0 group-hover:opacity-50" />
        )}
      </span>
    );
  };

  if (data.length === 0) {
    return (
      <div className="ds-card text-center py-8 text-muted">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className={`ds-table-wrap ${className}`}>
      <table className="ds-table">
        <thead>
          <tr>
            {selectable && (
              <th style={{ width: '32px' }}>
                <input
                  type="checkbox"
                  checked={selectedIds.size === data.length && data.length > 0}
                  onChange={toggleAll}
                  className="cursor-pointer"
                />
              </th>
            )}
            {columns.map(column => (
              <th
                key={column.key}
                style={{ width: column.width }}
                className={column.sortable ? 'cursor-pointer select-none' : ''}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                <div className="flex items-center gap-1">
                  {column.header}
                  {column.sortable && sort.key === column.key && (
                    sort.direction === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map(row => {
            const id = keyExtractor(row);
            const isSelected = selectedIds.has(id);

            return (
              <tr
                key={id}
                className={`group ${onRowClick ? 'cursor-pointer' : ''} ${isSelected ? 'bg-blue-900/20' : ''}`}
                onClick={() => onRowClick?.(row)}
              >
                {selectable && (
                  <td onClick={e => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleSelection(id)}
                      className="cursor-pointer"
                    />
                  </td>
                )}
                {columns.map(column => (
                  <td key={`${id}-${column.key}`}>
                    {renderCell(row, column)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

interface BulkActionsProps {
  selectedCount: number;
  onExport?: () => void;
  onDelete?: () => void;
  onAction?: (action: string) => void;
  actions?: { key: string; label: string; variant?: 'primary' | 'secondary' | 'danger' | 'success' }[];
}

export function BulkActions({
  selectedCount,
  onExport,
  onDelete,
  onAction,
  actions = [],
}: BulkActionsProps) {
  if (selectedCount === 0) return null;

  const getBtnClass = (variant?: string) => {
    switch (variant) {
      case 'primary': return 'ds-btn ds-btn-primary ds-btn-sm';
      case 'danger': return 'ds-btn ds-btn-danger ds-btn-sm';
      case 'success': return 'ds-btn ds-btn-success ds-btn-sm';
      default: return 'ds-btn ds-btn-secondary ds-btn-sm';
    }
  };

  return (
    <div
      className="ds-animate-in"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        background: 'var(--ds-bg-3)',
        border: '1px solid var(--ds-border-2)',
        borderRadius: '9px',
        padding: '9px 14px',
        marginBottom: '12px',
        fontSize: '0.82rem',
      }}
    >
      <span style={{ fontWeight: 600 }}>{selectedCount} selected</span>
      
      {onExport && (
        <button className="ds-btn ds-btn-secondary ds-btn-sm" onClick={onExport}>
          ⬇️ Export
        </button>
      )}
      
      {actions.map(action => (
        <button
          key={action.key}
          className={getBtnClass(action.variant)}
          onClick={() => onAction?.(action.key)}
        >
          {action.label}
        </button>
      ))}
      
      {onDelete && (
        <button className="ds-btn ds-btn-danger ds-btn-sm" onClick={onDelete}>
          🗑️ Delete
        </button>
      )}
    </div>
  );
}
