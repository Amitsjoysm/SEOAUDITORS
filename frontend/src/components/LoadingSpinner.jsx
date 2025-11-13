import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ size = 'default', text = 'Loading...' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    default: 'w-12 h-12',
    large: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative">
        <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-400`} />
        <div className="absolute inset-0 blur-xl bg-blue-500/30 animate-pulse"></div>
      </div>
      {text && (
        <p className="text-slate-300 text-lg font-medium animate-pulse">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
