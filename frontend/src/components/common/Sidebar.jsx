import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  ShieldAlert,
  Cpu,
  Globe2,
  BarChart3,
  FileDown,
  ExternalLink
} from 'lucide-react';

export const Sidebar = () => {
  const navItems = [
    { name: 'SOC Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Security Logs', path: '/logs', icon: FileText },
    { name: 'Incidents', path: '/incidents', icon: ShieldAlert },
    { name: 'Simulation Center', path: '/simulation', icon: Cpu, badge: '8 Rules' },
    { name: 'Threat Intelligence', path: '/threat-intel', icon: Globe2 },
    { name: 'Analytics & Trends', path: '/analytics', icon: BarChart3 },
    { name: 'Report Center', path: '/reports', icon: FileDown },
  ];

  return (
    <aside className="w-64 bg-cyber-card border-r border-cyber-border flex flex-col justify-between shrink-0 h-[calc(100vh-4rem)] sticky top-16">
      <div className="p-4 space-y-6">
        <div>
          <p className="px-3 text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Operations Center
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-[0_0_12px_rgba(6,182,212,0.15)] font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`
                  }
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 font-semibold">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* PBL Demonstration Card */}
        <div className="p-3.5 rounded-xl bg-gradient-to-b from-slate-900 to-cyber-bg border border-slate-800">
          <div className="flex items-center space-x-2 mb-1.5 text-xs font-bold text-slate-200">
            <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
            <span>PBL Evaluation Ready</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
            Real-time rule evaluation, threat correlation, and ReportLab forensic PDF generation.
          </p>
          <div className="flex items-center justify-between text-[11px] font-mono text-cyan-400">
            <span>Detection: 8 / 8 Rules</span>
            <span className="text-emerald-400 font-bold">ACTIVE</span>
          </div>
        </div>
      </div>

      {/* Bottom system footer */}
      <div className="p-4 border-t border-cyber-border/70 text-xs text-slate-400 flex items-center justify-between">
        <div>
          <p className="font-mono text-slate-300">SentinelX Core</p>
          <p className="text-[10px]">PBL SOC Edition 2026</p>
        </div>
        <div className="flex items-center space-x-1 text-emerald-400 font-mono text-[11px]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Online</span>
        </div>
      </div>
    </aside>
  );
};
