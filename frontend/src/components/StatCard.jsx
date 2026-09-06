import React from 'react';

const StatCard = ({
  title,
  value,
  icon: Icon = null,
  description = '',
  loading = false
}) => {
  return (
    <div className="stat-card">
      <div className="stat-header">
        <span>{title}</span>
        {Icon && <Icon size={16} style={{ color: 'var(--text-muted)' }} />}
      </div>
      
      {loading ? (
        <div 
          className="skeleton-bar" 
          style={{
            height: '24px',
            backgroundColor: 'var(--border)',
            borderRadius: '2px',
            width: '50%',
            marginTop: '4px',
            animation: 'pulse 1.5s infinite ease-in-out'
          }}
        />
      ) : (
        <div className="stat-value">{value}</div>
      )}
      
      {description && !loading && (
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
          {description}
        </span>
      )}
    </div>
  );
};

export default StatCard;
