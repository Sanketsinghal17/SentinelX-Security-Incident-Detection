import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, Cpu, Bell, LogOut, RefreshCw } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useDashboard } from '../../context/DashboardContext';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../services/api';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const { refreshTrigger, triggerRefresh } = useDashboard();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await api.get('/dashboard/summary');
        setSummary(res.data.summary);
      } catch (err) {
        console.error("Failed to load status summary", err);
      }
    };
    fetchStatus();
  }, [refreshTrigger]);

  const handleManualRefresh = async () => {
    setRefreshing(true);
    triggerRefresh();
    setTimeout(() => setRefreshing(false), 600);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const statusColorMap = {
    red: 'bg-red-500/10 text-red-400 border-red-500/40 shadow-[0_0_10px_rgba(239,68,68,0.25)]',
    orange: 'bg-orange-500/10 text-orange-400 border-orange-500/40 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.25)]',
  };

  const statusColor = summary ? summary.status_color : 'green';
  const statusText = summary ? summary.system_status : 'OPERATIONAL NORMAL';

  return (
    <header className="h-16 bg-cyber-card border-b border-cyber-border px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/30 border border-cyan-500/40 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.25)]">
          <Shield className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-lg font-extrabold text-white tracking-wider">SENTINEL<span className="text-cyan-400">X</span></span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800">SOC v2.4</span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Security Incident Detection & Analysis Platform</p>
        </div>
      </div>

      {/* Center status & Quick simulator */}
      <div className="hidden md:flex items-center space-x-4">
        {/* System Threat Posture */}
        <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-mono font-semibold ${statusColorMap[statusColor]}`}>
          <span className={`w-2 h-2 rounded-full ${statusColor === 'red' ? 'bg-red-400 animate-ping' : statusColor === 'orange' ? 'bg-orange-400' : 'bg-emerald-400'}`}></span>
          <span>DEFCON POSTURE: {statusText}</span>
        </div>

        {/* Simulation Shortcut */}
        <Link
          to="/simulation"
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-semibold transition-all shadow-[0_0_10px_rgba(6,182,212,0.15)]"
        >
          <Cpu className="w-3.5 h-3.5" />
          <span>Simulation Center</span>
        </Link>

        {/* Refresh button */}
        <button
          onClick={handleManualRefresh}
          title="Refresh SOC Dashboard"
          className="p-2 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-300 hover:text-white border border-cyber-border transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-cyan-400' : ''}`} />
        </button>
      </div>

      {/* Right User & Actions */}
      <div className="flex items-center space-x-4">
        <div className="text-right hidden sm:block">
          <p className="text-xs font-bold text-white leading-tight">{user?.full_name || 'Alex Vance'}</p>
          <p className="text-[11px] text-cyan-400 font-mono">{user?.role || 'Lead SOC Analyst'}</p>
        </div>

        <div className="w-9 h-9 rounded-full bg-slate-800 border border-cyan-500/40 flex items-center justify-center text-xs font-bold text-cyan-300 font-mono">
          {user?.username ? user.username.slice(0, 2).toUpperCase() : 'AV'}
        </div>

        <button
          onClick={handleLogout}
          title="Sign Out"
          className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
