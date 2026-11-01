import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  Filter,
  ArrowUpRight,
  UserCheck,
  Clock,
  Download,
  AlertTriangle
} from 'lucide-react';
import api from '../services/api';
import { useDashboard } from '../context/DashboardContext';
import { SeverityBadge, StatusBadge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const IncidentsPage = () => {
  const { refreshTrigger, triggerRefresh } = useDashboard();
  const navigate = useNavigate();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState('ALL');
  const [category, setCategory] = useState('ALL');
  const [status, setStatus] = useState('ALL');

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const params = {
        severity,
        category,
        status,
        search: search.trim()
      };
      const res = await api.get('/incidents', { params });
      setIncidents(res.data);
    } catch (err) {
      console.error("Failed to fetch incidents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [severity, category, status, refreshTrigger]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchIncidents();
  };

  const handleStatusChange = async (incidentId, newStatus, e) => {
    e.stopPropagation();
    try {
      await api.patch(`/incidents/${incidentId}`, { status: newStatus });
      triggerRefresh();
      fetchIncidents();
    } catch (err) {
      console.error("Failed to update status", err);
    }
  };

  const categories = [
    'ALL',
    'Malware',
    'Phishing',
    'DDoS',
    'Insider Threat',
    'Brute Force',
    'Data Breach',
    'Port Scanning',
    'Unauthorized Access'
  ];

  const severities = ['ALL', 'Critical', 'High', 'Medium', 'Low'];
  const statuses = ['ALL', 'Open', 'Investigating', 'Contained', 'Resolved', 'Closed'];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-wider flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            <span>Incident Classification & Prioritization</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Triaged security incidents, root-cause categorization, and remediation lifecycle.
          </p>
        </div>

        <a
          href="/api/reports/incidents/csv"
          download
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-cyber-border transition-colors shadow-sm"
        >
          <Download className="w-3.5 h-3.5 text-cyan-400" />
          <span>Export Incidents CSV</span>
        </a>
      </div>

      {/* Filters Toolbar */}
      <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="w-full md:w-80 relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search incident ID, title, IP, asset..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-cyber-border text-white text-xs focus:outline-none focus:border-cyan-400 font-mono"
          />
        </form>

        {/* Filter dropdowns */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto justify-end">
          {/* Severity */}
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="py-1.5 px-3 rounded-lg bg-slate-900 border border-cyber-border text-slate-200 text-xs focus:outline-none focus:border-cyan-400 font-medium"
          >
            {severities.map((s) => (
              <option key={s} value={s}>Severity: {s}</option>
            ))}
          </select>

          {/* Category */}
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="py-1.5 px-3 rounded-lg bg-slate-900 border border-cyber-border text-slate-200 text-xs focus:outline-none focus:border-cyan-400 font-medium"
          >
            {categories.map((c) => (
              <option key={c} value={c}>Category: {c}</option>
            ))}
          </select>

          {/* Status */}
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="py-1.5 px-3 rounded-lg bg-slate-900 border border-cyber-border text-slate-200 text-xs focus:outline-none focus:border-cyan-400 font-medium"
          >
            {statuses.map((st) => (
              <option key={st} value={st}>Status: {st}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="rounded-xl bg-cyber-card border border-cyber-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-900/90 text-slate-400 uppercase font-mono tracking-wider border-b border-cyber-border">
                <th className="py-3 px-4">Incident ID</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Incident Title</th>
                <th className="py-3 px-4">Source IP</th>
                <th className="py-3 px-4">Affected Asset</th>
                <th className="py-3 px-4">Detection Time</th>
                <th className="py-3 px-4">Owner</th>
                <th className="py-3 px-4">Status Transition</th>
                <th className="py-3 px-4 text-right">Investigation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/60">
              {loading ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center">
                    <LoadingSpinner message="Loading triaged incidents..." />
                  </td>
                </tr>
              ) : incidents && incidents.length > 0 ? (
                incidents.map((inc) => (
                  <tr
                    key={inc.id}
                    onClick={() => navigate(`/incidents/${inc.id}`)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400 whitespace-nowrap">
                      {inc.incident_id}
                    </td>
                    <td className="py-3 px-4">
                      <SeverityBadge severity={inc.severity} />
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[11px] font-mono text-slate-300">
                        {inc.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-white max-w-xs truncate" title={inc.title}>
                      {inc.title}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300 whitespace-nowrap">
                      {inc.source_ip}
                    </td>
                    <td className="py-3 px-4 text-slate-300 whitespace-nowrap font-mono">
                      {inc.affected_asset}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                      {inc.detection_timestamp?.replace('T', ' ')?.slice(0, 16)}
                    </td>
                    <td className="py-3 px-4 text-slate-300 whitespace-nowrap">
                      <div className="flex items-center space-x-1.5">
                        <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{inc.owner}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                      <select
                        value={inc.status}
                        onChange={(e) => handleStatusChange(inc.id, e.target.value, e)}
                        className="py-1 px-2 rounded bg-slate-900 border border-slate-700 text-slate-200 text-xs font-semibold focus:outline-none focus:border-cyan-400"
                      >
                        <option value="Open">Open</option>
                        <option value="Investigating">Investigating</option>
                        <option value="Contained">Contained</option>
                        <option value="Resolved">Resolved</option>
                        <option value="Closed">Closed</option>
                      </select>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => { e.stopPropagation(); navigate(`/incidents/${inc.id}`); }}
                        className="p-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 transition-colors"
                        title="Open Investigation Room"
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-500 text-xs">
                    No security incidents match the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
