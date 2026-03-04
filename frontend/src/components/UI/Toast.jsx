import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import clsx from 'clsx';

const VARIANTS = {
  success: {
    icon: CheckCircle,
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-200 dark:border-green-800',
    iconColor: 'text-green-500',
    textColor: 'text-green-800 dark:text-green-200',
  },
  error: {
    icon: XCircle,
    bg: 'bg-red-50 dark:bg-red-900/30',
    border: 'border-red-200 dark:border-red-800',
    iconColor: 'text-red-500',
    textColor: 'text-red-800 dark:text-red-200',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-yellow-50 dark:bg-yellow-900/30',
    border: 'border-yellow-200 dark:border-yellow-800',
    iconColor: 'text-yellow-500',
    textColor: 'text-yellow-800 dark:text-yellow-200',
  },
  info: {
    icon: Info,
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-200 dark:border-blue-800',
    iconColor: 'text-blue-500',
    textColor: 'text-blue-800 dark:text-blue-200',
  },
};

export default function Toast({
  message,
  variant = 'info',
  title,
  onClose,
  className,
}) {
  const config = VARIANTS[variant] || VARIANTS.info;
  const IconComponent = config.icon;

  return (
    <div
      className={clsx(
        'flex items-start gap-3 p-4 rounded-xl border shadow-lg',
        'animate-in slide-in-from-right',
        config.bg,
        config.border,
        className
      )}
      role="alert"
    >
      <IconComponent className={clsx('w-5 h-5 shrink-0 mt-0.5', config.iconColor)} />

      <div className="flex-1 min-w-0">
        {title && (
          <p className={clsx('font-semibold text-sm', config.textColor)}>
            {title}
          </p>
        )}
        <p className={clsx('text-sm', config.textColor, title && 'mt-0.5')}>
          {message}
        </p>
      </div>

      {onClose && (
        <button
          onClick={onClose}
          className={clsx(
            'shrink-0 p-1 rounded-lg transition-colors',
            'hover:bg-black/5 dark:hover:bg-white/5',
            config.textColor
          )}
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}