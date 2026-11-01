import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'cyan', glow = false }) => {
  const colorMap = {
    cyan: {
      text: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
      border: 'border-cyan-500/30',
      glow: 'shadow-[0_0_15px_rgba(6,182,212,0.15)]',
    },
    red: {
      text: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      glow: 'shadow-[0_0_15px_rgba(239,68,68,0.2)]',
    },
    orange: {
      text: 'text-orange-400',
      bg: 'bg-orange-500/10',
      border: 'border-orange-500/30',
      glow: 'shadow-[0_0_15px_rgba(245,158,11,0.2)]',
    },
    green: {
      text: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      glow: 'shadow-[0_0_15px_rgba(16,185,129,0.2)]',
    },
    purple: {
      text: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/30',
      glow: 'shadow-[0_0_15px_rgba(139,92,246,0.2)]',
    },
  };

  const c = colorMap[color] || colorMap.cyan;

  return (
    <div className={`p-5 rounded-xl bg-cyber-card border border-cyber-border hover:border-slate-700 transition-all ${glow ? c.glow : ''}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-1">{title}</p>
          <h3 className="text-3xl font-extrabold text-white font-mono tracking-tight">{value}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg ${c.bg} ${c.text} border ${c.border}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
    </div>
  );
};
