import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, User, AlertCircle, ArrowRight, KeyRound } from 'lucide-react';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please provide both username and password.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoCreds = (user, pass) => {
    setUsername(user);
    setPassword(pass);
    setError('');
  };

  return (
    <div className="min-h-screen bg-cyber-bg flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative cyber grid backdrop */}
      <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-30"></div>
      
      {/* Glow shapes */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="max-w-md w-full bg-cyber-card border border-cyber-border rounded-2xl p-8 relative z-10 shadow-2xl">
        {/* Brand Icon & Heading */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500/20 to-blue-500/20 border border-cyan-500/40 mx-auto flex items-center justify-center mb-4 shadow-[0_0_25px_rgba(6,182,212,0.3)]">
            <Shield className="w-8 h-8 text-cyan-400" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-wider">
            SENTINEL<span className="text-cyan-400">X</span> SOC
          </h1>
          <p className="text-sm text-slate-400 mt-1">Security Incident Detection & Analysis Platform</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Analyst Identifier
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                <User className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="analyst@sentinelx.io"
                className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-900/90 border border-cyber-border text-white text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 font-mono transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
              Access Token / Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-900/90 border border-cyber-border text-white text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 font-mono transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 mt-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-sm tracking-wide transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)] flex items-center justify-center space-x-2"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            ) : (
              <>
                <span>Authenticate to SOC Console</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Demo Quick Fill Buttons */}
        <div className="mt-8 pt-6 border-t border-cyber-border/70">
          <p className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-3 text-center">
            PBL Demo Credentials (1-Click Fill)
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => fillDemoCreds('analyst@sentinelx.io', 'Sentinel@2025')}
              className="p-2.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-left transition-colors"
            >
              <div className="flex items-center space-x-1.5 text-xs font-bold text-cyan-400 mb-0.5">
                <KeyRound className="w-3.5 h-3.5" />
                <span>Analyst Demo</span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono truncate">analyst@sentinelx.io</p>
            </button>

            <button
              type="button"
              onClick={() => fillDemoCreds('admin', 'SentinelPass123!')}
              className="p-2.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-left transition-colors"
            >
              <div className="flex items-center space-x-1.5 text-xs font-bold text-purple-400 mb-0.5">
                <KeyRound className="w-3.5 h-3.5" />
                <span>SOC Lead Admin</span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono truncate">admin</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
