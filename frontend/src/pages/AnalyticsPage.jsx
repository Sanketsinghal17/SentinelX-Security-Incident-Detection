import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Clock,
  ShieldCheck,
  TrendingUp,
  Activity,
  Layers,
  Award,
  AlertTriangle
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import api from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const AnalyticsPage = () => {
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get('/analytics/trends');
        setTrends(res.data);
      } catch (err) {
        console.error("Failed to load analytics trends", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Executing Pandas statistical modeling & risk scoring..." />;
  }

  const {
    attack_type_breakdown = [],
    severity_matrix = [],
    asset_risk_scores = [],
    resolution_metrics = {},
    hourly_heat_pattern = [],
    impact_distribution = []
  } = trends || {};

  const SEVERITY_COLORS = ['#ef4444', '#f97316', '#eab308', '#06b6d4'];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-xl font-extrabold text-white tracking-wider flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-cyan-400" />
          <span>Incident Trend & Statistical Impact Analysis</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Pandas-powered analytical engine: Mean Time to Resolution (MTTR), recurring adversary attack patterns, and organizational risk scoring.
        </p>
      </div>

      {/* KPI Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-mono uppercase text-slate-400">Mean Time to Resolution</p>
            <Clock className="w-4 h-4 text-cyan-400" />
          </div>
          <h3 className="text-3xl font-black text-white font-mono">
            {resolution_metrics.mttr_hours} <span className="text-sm font-normal text-slate-400">hrs</span>
          </h3>
          <p className="text-[11px] text-emerald-400 mt-1 flex items-center space-x-1">
            <TrendingUp className="w-3 h-3" />
            <span>Optimal SLA Response window</span>
          </p>
        </div>

        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-mono uppercase text-slate-400">Resolution Rate</p>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <h3 className="text-3xl font-black text-emerald-400 font-mono">
            {resolution_metrics.resolution_rate}%
          </h3>
          <p className="text-[11px] text-slate-400 mt-1">Containment & remediation success</p>
        </div>

        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-mono uppercase text-slate-400">Average Detection Latency</p>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <h3 className="text-3xl font-black text-purple-400 font-mono">
            {resolution_metrics.avg_detection_minutes} <span className="text-sm font-normal text-slate-400">min</span>
          </h3>
          <p className="text-[11px] text-slate-400 mt-1">Real-time log stream processing</p>
        </div>

        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-mono uppercase text-slate-400">Cataloged Cases</p>
            <Layers className="w-4 h-4 text-orange-400" />
          </div>
          <h3 className="text-3xl font-black text-white font-mono">
            {resolution_metrics.total_analyzed || 0}
          </h3>
          <p className="text-[11px] text-slate-400 mt-1">Total analyzed incidents</p>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Incident Frequency Heat Pattern */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Adversary Activity Patterns by Hour of Day (24h)
              </h3>
              <p className="text-xs text-slate-400">Identifies peak attack frequency windows</p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourly_heat_pattern}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(h) => `${h}:00`} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0c1322', borderColor: '#1b253b', borderRadius: '8px', color: '#fff' }}
                  labelFormatter={(h) => `Hour ${h}:00 UTC`}
                />
                <Bar dataKey="incidents" fill="#06b6d4" radius={[3, 3, 0, 0]} name="Incidents" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Asset Risk Scoring Index */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Enterprise Asset Risk Scoring Index
              </h3>
              <p className="text-xs text-slate-400">Weighted formula: Incidents × Severity Severity Coefficient</p>
            </div>
            <Award className="w-4 h-4 text-purple-400" />
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={asset_risk_scores} margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis dataKey="affected_asset" type="category" stroke="#64748b" tick={{ fontSize: 10 }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0c1322', borderColor: '#1b253b', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="risk_score" fill="#ec4899" radius={[0, 4, 4, 0]} name="Cumulative Risk Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Business Impact Distribution Breakdown */}
      <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
          Organizational Business Impact Tier Assessment
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Categorization of threats according to operational disruption, compliance exposure, and forensic scope.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {impact_distribution.map((tier, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                idx === 0 ? 'bg-red-950 text-red-400' : idx === 1 ? 'bg-orange-950 text-orange-400' : 'bg-slate-800 text-slate-300'
              }`}>
                Tier {idx + 1}
              </span>
              <h4 className="text-xs font-bold text-white mt-2 mb-1">{tier.tier}</h4>
              <p className="text-2xl font-black font-mono text-cyan-400 mt-2">{tier.count} <span className="text-xs font-normal text-slate-400">cases</span></p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
