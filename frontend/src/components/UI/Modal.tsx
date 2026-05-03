import React, { useEffect, useCallback } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
};

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
}) => {
  const handleEscape = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleEscape]);

  if (!isOpen) return null;

  return (
    <div
      className="ds-modal-overlay open"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className={`ds-modal ${sizeClasses[size]}`}>
        {title && (
          <div className="ds-modal-header flex items-center justify-between">
            <span>{title}</span>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/10 rounded transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        )}
        
        <div className="modal-content">
          {children}
        </div>
        
        {footer && (
          <div className="ds-modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

interface DetailModalProps<T> {
  isOpen: boolean;
  onClose: () => void;
  data: T | null;
  title?: string;
  renderDetails: (data: T) => React.ReactNode;
  onExport?: (data: T) => void;
  onDelete?: (data: T) => void;
}

export function DetailModal<T>({
  isOpen,
  onClose,
  data,
  title = 'Record Details',
  renderDetails,
  onExport,
  onDelete,
}: DetailModalProps<T>) {
  if (!data) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="lg"
      footer={
        <>
          {onExport && (
            <button
              className="ds-btn ds-btn-secondary ds-btn-sm"
              onClick={() => onExport(data)}
            >
              ⬇️ Export
            </button>
          )}
          {onDelete && (
            <button
              className="ds-btn ds-btn-danger ds-btn-sm"
              onClick={() => {
                onDelete(data);
                onClose();
              }}
            >
              🗑️ Delete
            </button>
          )}
          <button className="ds-btn ds-btn-secondary ds-btn-sm" onClick={onClose}>
            ✕ Close
          </button>
        </>
      }
    >
      {renderDetails(data)}
    </Modal>
  );
}

// Quality score display component
interface QualityScoreProps {
  score: number;
  issues?: string[];
  recommendation?: string;
}

export const QualityScore: React.FC<QualityScoreProps> = ({
  score,
  issues = [],
  recommendation,
}) => {
  const getColor = () => {
    if (score >= 0.8) return 'var(--ds-success)';
    if (score >= 0.5) return 'var(--ds-warning)';
    return 'var(--ds-danger)';
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <div className="ds-quality-bar" style={{ width: '110px', height: '7px' }}>
          <div
            className="ds-quality-fill"
            style={{
              width: `${Math.round(score * 100)}%`,
              background: getColor(),
            }}
          />
        </div>
        <span className="ds-mono" style={{ fontSize: '0.79rem', color: getColor() }}>
          {Math.round(score * 100)}% quality
        </span>
      </div>
      
      {issues.length > 0 && (
        <div style={{ color: 'var(--ds-warning)', fontSize: '0.79rem', marginBottom: '6px' }}>
          ⚠ Issues: {issues.join(', ')}
        </div>
      )}
      
      {recommendation && (
        <div style={{ fontStyle: 'italic', fontSize: '0.81rem', color: getColor(), marginBottom: '11px' }}>
          {recommendation}
        </div>
      )}
    </div>
  );
};
