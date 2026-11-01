import React from 'react';

export const SeverityBadge = ({ severity }) => {
  const sev = (severity || 'Medium').toLowerCase();

  const styles = {
    critical: 'bg-red-950/70 text-red-400 border border-red-600/60 shadow-[0_0_8px_rgba(239,68,68,0.25)]',
    high: 'bg-orange-950/70 text-orange-400 border border-orange-500/50',
    medium: 'bg-yellow-950/70 text-yellow-300 border border-yellow-500/40',
    low: 'bg-sky-950/70 text-sky-400 border border-sky-500/40',
  };

  const styleClass = styles[sev] || styles.medium;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider ${styleClass}`}>
      {sev === 'critical' && <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-ping mr-1.5"></span>}
      {severity}
    </span>
  );
};

export const StatusBadge = ({ status }) => {
  const st = (status || 'Open').toLowerCase();

  const styles = {
    open: 'bg-red-500/10 text-red-400 border border-red-500/30',
    investigating: 'bg-amber-500/10 text-amber-400 border border-amber-500/30',
    contained: 'bg-purple-500/10 text-purple-400 border border-purple-500/30',
    resolved: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
    closed: 'bg-slate-500/10 text-slate-400 border border-slate-500/30',
  };

  const styleClass = styles[st] || styles.open;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styleClass}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-70"></span>
      {status}
    </span>
  );
};
