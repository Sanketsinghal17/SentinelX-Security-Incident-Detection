import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  ShieldAlert,
  Flame,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Layers,
  ArrowUpRight,
  Radio,
  Server,
  Terminal,
  Cpu
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
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
import { useDashboard } from '../context/DashboardContext';
import { StatCard } from '../components/common/StatCard';
import { SeverityBadge, StatusBadge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const DashboardPage = () => {
  const { refreshTrigger } = useDashboard();
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [charts, setCharts] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [topIps, setTopIps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [sumRes, chartsRes, alertsRes, ipsRes] = await Promise.all([
          api.get('/dashboard/summary'),
          api.get('/dashboard/charts'),
          api.get('/dashboard/recent-alerts'),
          api.get('/dashboard/top-suspicious-ips')
        ]);
        setSummary(sumRes.data.summary);
        setCharts(chartsRes.data);
        setAlerts(alertsRes.data);
        setTopIps(ipsRes.data);
      } catch (err) {
        console.error("Error fetching dashboard data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [refreshTrigger]);

  if (loading) {
    return <LoadingSpinner message="Querying real-time SIEM telemetry & correlation engine..." />;
  }

  // Color palettes for Recharts
  const SEVERITY_COLORS = {
    Critical: '#ef4444',
    High: '#f97316',
    Medium: '#eab308',
    Low: '#06b6d4',
  };

  const PIE_COLORS = ['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#10b981'];

  return (
    <div className="space-y-6">
      {/* Top Banner Alert / Threat Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900 via-cyber-card to-slate-900 border border-cyber-border flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <span>SentinelX Real-Time Threat Correlation Active</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            </h2>
            <p className="text-xs text-slate-400">
              Correlating authentication events, perimeter sweeps, malware telemetry, and outbound exfiltration.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <Link
            to="/simulation"
            className="px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            <Cpu className="w-4 h-4" />
            <span>Launch Attack Simulation</span>
          </Link>
          <Link
            to="/reports"
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <span>Export Executive PDF</span>
          </Link>
        </div>
      </div>

      {/* KPI Stat Cards (6 Summary Cards required) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Total Events"
          value={summary?.total_events || 0}
          subtitle="Processed logs"
          icon={Layers}
          color="cyan"
        />
        <StatCard
          title="Total Incidents"
          value={summary?.total_incidents || 0}
          subtitle="All recorded cases"
          icon={ShieldAlert}
          color="purple"
        />
        <StatCard
          title="Critical Threats"
          value={summary?.critical_incidents || 0}
          subtitle="Immediate triage"
          icon={Flame}
          color="red"
          glow={summary?.critical_incidents > 0}
        />
        <StatCard
          title="High Severity"
          value={summary?.high_incidents || 0}
          subtitle="Active investigation"
          icon={AlertTriangle}
          color="orange"
        />
        <StatCard
          title="Open Incidents"
          value={summary?.open_incidents || 0}
          subtitle="Under active response"
          icon={Activity}
          color="cyan"
        />
        <StatCard
          title="Resolved"
          value={summary?.resolved_incidents || 0}
          subtitle="Containment achieved"
          icon={CheckCircle2}
          color="green"
        />
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity & Incident Trend (Area Chart) */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Security Telemetry & Incidents Timeline (7 Days)
              </h3>
              <p className="text-xs text-slate-400">Correlation volume versus confirmed security incidents</p>
            </div>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              Live Aggregation
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts?.activity_timeline || []}>
                <defs>
                  <linearGradient id="colorEvents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.5}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0c1322', borderColor: '#1b253b', borderRadius: '8px', color: '#fff' }}
                />
                <Area type="monotone" dataKey="events" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#colorEvents)" name="Telemetry Logs" />
                <Area type="monotone" dataKey="incidents" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorIncidents)" name="Incidents" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution (Donut Chart) */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-1">
              Incidents by Severity
            </h3>
            <p className="text-xs text-slate-400 mb-4">Risk prioritization breakdown</p>
          </div>

          <div className="h-48 w-full flex items-center justify-center">
            {charts?.severity_distribution && charts.severity_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={charts.severity_distribution}
                    dataKey="count"
                    nameKey="severity"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {charts.severity_distribution.map((entry) => (
                      <Cell key={`cell-${entry.severity}`} fill={SEVERITY_COLORS[entry.severity] || '#3b82f6'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0c1322', borderColor: '#1b253b', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-xs text-slate-500">No incident data yet</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-cyber-border text-xs">
            {charts?.severity_distribution?.map((item) => (
              <div key={item.severity} className="flex items-center justify-between">
                <span className="flex items-center space-x-1.5 text-slate-400">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: SEVERITY_COLORS[item.severity] || '#3b82f6' }}
                  ></span>
                  <span>{item.severity}</span>
                </span>
                <span className="font-mono font-bold text-white">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Second Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Incidents by Attack Type */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Incidents by Attack Type
              </h3>
              <p className="text-xs text-slate-400">Classification across 8 detection categories</p>
            </div>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts?.attack_type_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="category" stroke="#64748b" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={45} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0c1322', borderColor: '#1b253b', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} name="Incidents" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Targeted Assets */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Top Targeted Enterprise Assets
              </h3>
              <p className="text-xs text-slate-400">Infrastructure endpoints under adversary focus</p>
            </div>
            <Server className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={charts?.targeted_assets || []}
                margin={{ left: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis dataKey="asset" type="category" stroke="#64748b" tick={{ fontSize: 10 }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0c1322', borderColor: '#1b253b', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="incidents" fill="#818cf8" radius={[0, 4, 4, 0]} name="Incidents" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Section: Recent Alerts & Suspicious IPs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts Feed (2 cols) */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Live Security Alerts Feed
              </h3>
            </div>
            <Link
              to="/incidents"
              className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1"
            >
              <span>View All Incidents</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-cyber-border/70 overflow-hidden">
            {alerts && alerts.length > 0 ? (
              alerts.slice(0, 6).map((alert) => (
                <div
                  key={alert.id}
                  onClick={() => alert.incident_id && navigate(`/incidents/${alert.incident_id}`)}
                  className={`py-3 px-2 flex items-center justify-between hover:bg-slate-800/40 rounded-lg transition-colors ${
                    alert.incident_id ? 'cursor-pointer' : ''
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="mt-1">
                      <SeverityBadge severity={alert.severity} />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold text-white">{alert.attack_type}</span>
                        <span className="text-[11px] font-mono text-cyan-400">{alert.alert_id}</span>
                      </div>
                      <p className="text-xs text-slate-300 line-clamp-1 mt-0.5">{alert.description}</p>
                      <div className="flex items-center space-x-3 text-[10px] text-slate-400 mt-1 font-mono">
                        <span>SRC: {alert.source_ip}</span>
                        <span>TARGET: {alert.target_system}</span>
                        <span>RULE: {alert.detection_rule}</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right shrink-0 ml-4">
                    <span className="text-[11px] text-slate-400 font-mono">
                      {alert.detection_timestamp?.split('T')[1]?.slice(0, 8) || 'Just now'}
                    </span>
                    {alert.incident_id && (
                      <div className="mt-1">
                        <span className="text-[10px] text-cyan-400 hover:underline flex items-center justify-end space-x-0.5 font-semibold">
                          <span>Investigate</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">No alerts recorded yet.</p>
            )}
          </div>
        </div>

        {/* Top Suspicious IPs (1 col) */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Top Threat Indicators
            </h3>
            <Link
              to="/threat-intel"
              className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold"
            >
              Intelligence
            </Link>
          </div>

          <div className="space-y-3">
            {topIps && topIps.length > 0 ? (
              topIps.map((ip) => (
                <div
                  key={ip.ip_address}
                  className="p-3 rounded-lg bg-slate-900/80 border border-cyber-border/80 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono font-bold text-white">{ip.ip_address}</span>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold ${
                        ip.threat_score >= 80
                          ? 'bg-red-950 text-red-400 border border-red-800'
                          : 'bg-orange-950 text-orange-400 border border-orange-800'
                      }`}
                    >
                      Risk: {ip.threat_score}/100
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{ip.country} • {ip.isp}</span>
                    <span className="text-cyan-400 font-mono">{ip.incidents_count} Incidents</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">No high risk IPs cataloged yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
