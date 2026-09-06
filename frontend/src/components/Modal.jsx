import React, { useEffect } from 'react';
import Button from './Button';

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = '', // '', 'lg'
  footerButtons = [], // [{label: 'Save', onClick: handleSave, variant: 'primary', disabled: false}]
}) => {
  
  // Close on Escape key press
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleEscape);
    }
    
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className={`modal-content ${size ? `modal-${size}` : ''}`} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>
        
        <div className="modal-body">
          {children}
        </div>
        
        {footerButtons && footerButtons.length > 0 && (
          <div className="modal-footer">
            {footerButtons.map((btn, idx) => (
              <Button
                key={idx}
                onClick={btn.onClick}
                variant={btn.variant || 'secondary'}
                disabled={btn.disabled}
                loading={btn.loading}
                size="sm"
              >
                {btn.label}
              </Button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Modal;
