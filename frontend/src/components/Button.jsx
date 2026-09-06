import React from 'react';

const Button = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary', // 'primary', 'secondary', 'danger'
  size = '', // 'sm'
  disabled = false,
  loading = false,
  className = '',
  icon: Icon = null,
  ...props
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`btn btn-${variant} ${size ? `btn-${size}` : ''} ${className}`}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          {/* Simple rotating spinner */}
          <svg className="animate-spin h-4 width-4 border-2 border-white border-t-transparent rounded-full" viewBox="0 0 24 24" style={{
            width: '12px',
            height: '12px',
            border: '2px solid currentColor',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            display: 'inline-block',
            animation: 'spin 1s linear infinite'
          }} />
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
          Loading...
        </span>
      ) : (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          {Icon && <Icon size={14} />}
          {children}
        </span>
      )}
    </button>
  );
};

export default Button;
