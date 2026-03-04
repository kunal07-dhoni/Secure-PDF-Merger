import React from 'react';
import clsx from 'clsx';
import Spinner from './Spinner';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className,
  ...props
}) {
  const variants = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
    ghost: 'bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 py-2.5 px-5 rounded-lg transition-all',
  };

  const sizes = {
    sm: 'text-sm py-1.5 px-3',
    md: 'text-sm py-2.5 px-5',
    lg: 'text-base py-3 px-6',
  };

  return (
    <button
      className={clsx(
        variants[variant],
        sizes[size],
        'inline-flex items-center justify-center gap-2 font-medium',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}