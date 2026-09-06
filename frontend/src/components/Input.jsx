import React from 'react';

const Input = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error = '',
  options = [], // [{value: 'val', label: 'label'}] - for select inputs
  rows = 3, // for textarea
  className = '',
  ...props
}) => {
  const isSelect = type === 'select';
  const isTextarea = type === 'textarea';

  return (
    <div className={`input-group ${className}`}>
      {label && (
        <label className="input-label" htmlFor={name}>
          {label}
          {required && <span className="required-indicator">*</span>}
        </label>
      )}

      {isSelect ? (
        <select
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          required={required}
          className={`form-select ${error ? 'border-red-500' : ''}`}
          style={error ? { borderColor: 'var(--danger)' } : {}}
          {...props}
        >
          {placeholder && <option value="">{placeholder}</option>}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : isTextarea ? (
        <textarea
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          rows={rows}
          className={`form-textarea ${error ? 'border-red-500' : ''}`}
          style={error ? { borderColor: 'var(--danger)' } : {}}
          {...props}
        />
      ) : (
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          className={`form-input ${error ? 'border-red-500' : ''}`}
          style={error ? { borderColor: 'var(--danger)' } : {}}
          {...props}
        />
      )}

      {error && <span className="form-error-msg">{error}</span>}
    </div>
  );
};

export default Input;
