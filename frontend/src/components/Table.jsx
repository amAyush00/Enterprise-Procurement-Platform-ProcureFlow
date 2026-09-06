import React from 'react';

const Table = ({
  headers = [], // [{ key: 'sku', label: 'SKU', sortable: true, align: 'left' }]
  data = [],
  isLoading = false,
  onSort = null,
  currentSort = { key: '', order: 'asc' }, // { key: 'sku', order: 'asc' }
  onRowClick = null,
  emptyMessage = 'No records found.'
}) => {
  
  const handleHeaderClick = (header) => {
    if (!header.sortable || !onSort) return;
    const nextOrder = currentSort.key === header.key && currentSort.order === 'asc' ? 'desc' : 'asc';
    onSort(header.key, nextOrder);
  };

  return (
    <div className="table-container">
      <table className="ent-table">
        <thead>
          <tr>
            {headers.map((header) => {
              const isSorted = currentSort.key === header.key;
              const alignClass = header.align ? `text-${header.align}` : '';
              return (
                <th
                  key={header.key}
                  onClick={() => handleHeaderClick(header)}
                  className={`${header.sortable ? 'sortable' : ''} ${alignClass}`}
                  style={{
                    textAlign: header.align || 'left',
                    cursor: header.sortable ? 'pointer' : 'default'
                  }}
                >
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    {header.label}
                    {header.sortable && isSorted && (
                      <span style={{ fontSize: '10px', color: 'var(--primary)' }}>
                        {currentSort.order === 'asc' ? '▲' : '▼'}
                      </span>
                    )}
                    {header.sortable && !isSorted && (
                      <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                        ↕
                      </span>
                    )}
                  </div>
                </th>
              );
            })}
          </tr>
        </thead>
        
        <tbody>
          {isLoading ? (
            // Animated loading skeletons
            Array.from({ length: 5 }).map((_, rowIndex) => (
              <tr key={rowIndex}>
                {headers.map((h, colIndex) => (
                  <td key={colIndex}>
                    <div 
                      className="skeleton-bar" 
                      style={{
                        height: '14px',
                        backgroundColor: 'var(--border)',
                        borderRadius: '2px',
                        width: colIndex === 0 ? '60%' : colIndex === 1 ? '85%' : '40%',
                        animation: 'pulse 1.5s infinite ease-in-out'
                      }}
                    />
                  </td>
                ))}
              </tr>
            ))
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={headers.length} style={{ textAlign: 'center', padding: '30px 14px', color: 'var(--text-secondary)' }}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr 
                key={row.id || rowIndex} 
                onClick={() => onRowClick && onRowClick(row)}
                style={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {headers.map((h) => {
                  const val = row[h.key];
                  return (
                    <td 
                      key={h.key} 
                      style={{ textAlign: h.align || 'left' }}
                    >
                      {h.render ? h.render(row) : val}
                    </td>
                  );
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>

      <style>{`
        @keyframes pulse {
          0% { opacity: 0.6; }
          50% { opacity: 0.3; }
          100% { opacity: 0.6; }
        }
      `}</style>
    </div>
  );
};

export default Table;
