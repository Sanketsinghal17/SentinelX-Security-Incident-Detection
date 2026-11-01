import React from 'react';
import { Shield } from 'lucide-react';

export const LoadingSpinner = ({ message = "Analyzing SOC Telemetry..." }) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-4">
      <div className="relative">
        <div className="w-16 h-16 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Shield className="w-6 h-6 text-cyan-400/80 animate-pulse" />
        </div>
      </div>
      <p className="text-sm font-medium text-slate-400 tracking-wide font-mono animate-pulse">{message}</p>
    </div>
  );
};
