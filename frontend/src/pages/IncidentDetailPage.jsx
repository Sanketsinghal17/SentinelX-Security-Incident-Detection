import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ShieldAlert,
  ArrowLeft,
  Download,
  Clock,
  Layers,
  Terminal,
  FileText,
  CheckCircle,
  AlertTriangle,
  Send,
  User,
  Activity,
  CheckSquare,
  Square,
  ShieldCheck,
  Zap,
  Globe2
} from 'lucide-react';
import api from '../services/api';
import { useDashboard } from '../context/DashboardContext';
import { SeverityBadge, StatusBadge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const IncidentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { triggerRefresh } = useDashboard();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);
  const [pdfDownloading, setPdfDownloading] = useState(false);

  const fetchIncidentDetail = async () => {
    try {
      const res = await api.get(`/incidents/${id}`);
      setData(res.data);
    } catch (err) {
      console.error("Failed to load incident detail", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidentDetail();
  }, [id]);

  const handleStatusChange = async (newStatus) => {
    try {
      await api.patch(`/incidents/${id}`, { status: newStatus });
      triggerRefresh();
      fetchIncidentDetail();
    } catch (err) {
      console.error("Failed to update status", err);
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    setSubmittingNote(true);
    try {
      await api.post(`/incidents/${id}/notes`, {
        note: newNote.trim(),
        author: 'Alex Vance (Lead Analyst)'
      });
      setNewNote('');
      fetchIncidentDetail();
    } catch (err) {
      console.error("Failed to append note", err);
    } finally {
      setSubmittingNote(false);
    }
  };

  const handleToggleActionStatus = async (actionId, currentStatus) => {
    const nextStatus = currentStatus === 'Completed' ? 'In Progress' : (currentStatus === 'In Progress' ? 'Pending' : 'Completed');
    try {
      await api.patch(`/incidents/${id}/actions/${actionId}`, { status: nextStatus });
      fetchIncidentDetail();
    } catch (err) {
      console.error("Failed to update response action", err);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Reconstructing forensic incident investigation timeline..." />;
  }

  if (!data || !data.incident) {
    return (
      <div className="p-8 text-center bg-cyber-card border border-cyber-border rounded-xl">
        <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-2" />
        <h3 className="text-base font-bold text-white">Incident Not Found</h3>
        <p className="text-xs text-slate-400 mt-1 mb-4">The requested incident ID does not exist in the database.</p>
        <Link to="/incidents" className="text-xs text-cyan-400 font-semibold hover:underline">
          Return to Incident Queue
        </Link>
      </div>
    );
  }

  const { incident, alerts, correlated_logs, notes, response_actions, timeline } = data;

  return (
    <div className="space-y-6 pb-12">
      {/* Navigation & Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate('/incidents')}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-cyber-border transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-sm font-bold text-cyan-400">{incident.incident_id}</span>
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={incident.status} />
            </div>
            <h1 className="text-xl font-black text-white mt-0.5">{incident.title}</h1>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
          {/* Status quick select */}
          <select
            value={incident.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="py-2 px-3 rounded-lg bg-slate-900 border border-cyber-border text-slate-200 text-xs font-semibold focus:outline-none focus:border-cyan-400"
          >
            <option value="Open">Status: Open</option>
            <option value="Investigating">Status: Investigating</option>
            <option value="Contained">Status: Contained</option>
            <option value="Resolved">Status: Resolved</option>
            <option value="Closed">Status: Closed</option>
          </select>

          {/* Download PDF Report */}
          <a
            href={`/api/reports/incident/${incident.id}/pdf`}
            download={`SentinelX_${incident.incident_id}_Report.pdf`}
            className="px-3.5 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold flex items-center space-x-2 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            <Download className="w-4 h-4" />
            <span>Generate PDF Report</span>
          </a>
        </div>
      </div>

      {/* Incident Metadata Overview Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3.5 rounded-xl bg-cyber-card border border-cyber-border">
          <p className="text-[10px] font-mono text-slate-400 uppercase">Category</p>
          <p className="text-xs font-bold text-white mt-1">{incident.category}</p>
        </div>
        <div className="p-3.5 rounded-xl bg-cyber-card border border-cyber-border">
          <p className="text-[10px] font-mono text-slate-400 uppercase">Source IP</p>
          <p className="text-xs font-bold font-mono text-cyan-400 mt-1">{incident.source_ip}</p>
        </div>
        <div className="p-3.5 rounded-xl bg-cyber-card border border-cyber-border">
          <p className="text-[10px] font-mono text-slate-400 uppercase">Destination</p>
          <p className="text-xs font-bold font-mono text-slate-300 mt-1">{incident.destination_ip || 'N/A'}</p>
        </div>
        <div className="p-3.5 rounded-xl bg-cyber-card border border-cyber-border">
          <p className="text-[10px] font-mono text-slate-400 uppercase">Target Asset</p>
          <p className="text-xs font-bold font-mono text-purple-400 mt-1 truncate">{incident.affected_asset}</p>
        </div>
        <div className="p-3.5 rounded-xl bg-cyber-card border border-cyber-border">
          <p className="text-[10px] font-mono text-slate-400 uppercase">Assigned Analyst</p>
          <p className="text-xs font-bold text-slate-200 mt-1 truncate">{incident.owner}</p>
        </div>
        <div className="p-3.5 rounded-xl bg-cyber-card border border-cyber-border">
          <p className="text-[10px] font-mono text-slate-400 uppercase">Detection Time</p>
          <p className="text-xs font-bold font-mono text-slate-400 mt-1">
            {incident.detection_timestamp?.split('T')[1]?.slice(0, 8) || 'N/A'} UTC
          </p>
        </div>
      </div>

      {/* Technical Forensic Breakdown: Attack Vector, Root Cause, Impact */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Attack Vector */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center space-x-2 text-cyan-400 mb-2">
            <Zap className="w-4 h-4" />
            <h3 className="text-xs font-bold uppercase tracking-wider">Identified Attack Vector</h3>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed font-mono">
            {incident.attack_vector || 'Network reconnaissance and anomalous payload execution.'}
          </p>
        </div>

        {/* Root Cause Analysis */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center space-x-2 text-orange-400 mb-2">
            <AlertTriangle className="w-4 h-4" />
            <h3 className="text-xs font-bold uppercase tracking-wider">Root Cause Analysis</h3>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed">
            {incident.root_cause || 'Exposed perimeter port without adaptive threshold rate limiting.'}
          </p>
        </div>

        {/* Business Impact Assessment */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
          <div className="flex items-center space-x-2 text-red-400 mb-2">
            <Activity className="w-4 h-4" />
            <h3 className="text-xs font-bold uppercase tracking-wider">Business Impact</h3>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed">
            {incident.business_impact || 'Operational latency and risk of unauthorized credential exposure.'}
          </p>
        </div>
      </div>

      {/* 6-Stage Incident Response Lifecycle Timeline */}
      <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Incident Response Lifecycle Timeline (6 Stages)
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">SOC SLA Standard Flow</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
          {timeline?.map((item) => (
            <div
              key={item.step}
              className={`p-3.5 rounded-xl border relative ${
                item.status === 'Completed'
                  ? 'bg-slate-900/90 border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.1)]'
                  : item.status === 'In Progress'
                  ? 'bg-slate-900/90 border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.15)]'
                  : 'bg-slate-900/40 border-slate-800 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                  Stage {item.step}
                </span>
                <span
                  className={`text-[10px] font-mono font-bold ${
                    item.status === 'Completed'
                      ? 'text-emerald-400'
                      : item.status === 'In Progress'
                      ? 'text-cyan-400 animate-pulse'
                      : 'text-slate-500'
                  }`}
                >
                  {item.status}
                </span>
              </div>
              <h4 className="text-xs font-bold text-white mb-1">{item.stage}</h4>
              <p className="text-[11px] text-slate-400 leading-snug">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Correlated Security Logs Section */}
      <div className="rounded-xl bg-cyber-card border border-cyber-border overflow-hidden">
        <div className="p-4 bg-slate-900/90 border-b border-cyber-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Correlated Security Telemetry & Evidence ({correlated_logs?.length || 0} events)
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">Matched via Detection Engine Filter</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-slate-400 uppercase font-mono tracking-wider border-b border-cyber-border">
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Source IP</th>
                <th className="py-2.5 px-4">Target IP</th>
                <th className="py-2.5 px-4">Action</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Raw Payload / Command Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/50">
              {correlated_logs && correlated_logs.length > 0 ? (
                correlated_logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-4 font-mono text-slate-300 whitespace-nowrap">
                      {log.timestamp?.replace('T', ' ')?.slice(0, 19)}
                    </td>
                    <td className="py-2.5 px-4 font-mono font-bold text-cyan-400 whitespace-nowrap">
                      {log.source_ip}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-slate-400 whitespace-nowrap">
                      {log.destination_ip || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-white whitespace-nowrap font-semibold">
                      {log.action}
                    </td>
                    <td className="py-2.5 px-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        log.status === 'FAILED' || log.status === 'BLOCKED' || log.status === 'ALERT'
                          ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 font-mono text-[11px] text-slate-300">
                      <span className="p-1 rounded bg-slate-950 border border-slate-800 inline-block max-w-lg truncate" title={log.raw_payload || log.description}>
                        {log.raw_payload || log.description}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 text-xs">
                    No raw log evidence correlated with this incident yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Two Column Section: Response Actions Playbook & Investigation Notes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mitigation Response Playbook (Interactive checklist) */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  Containment & Mitigation Playbook
                </h3>
              </div>
              <span className="text-[11px] font-mono text-slate-400">Click to Toggle Status</span>
            </div>

            <div className="space-y-3">
              {response_actions && response_actions.length > 0 ? (
                response_actions.map((act) => (
                  <div
                    key={act.id}
                    onClick={() => handleToggleActionStatus(act.id, act.status)}
                    className="p-3.5 rounded-lg bg-slate-900/80 border border-cyber-border hover:border-slate-700 cursor-pointer transition-colors flex items-start space-x-3"
                  >
                    <div className="mt-0.5 text-cyan-400 shrink-0">
                      {act.status === 'Completed' ? (
                        <CheckSquare className="w-5 h-5 text-emerald-400" />
                      ) : (
                        <Square className="w-5 h-5 text-slate-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-bold ${act.status === 'Completed' ? 'line-through text-slate-500' : 'text-white'}`}>
                          {act.action_title}
                        </span>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                          act.status === 'Completed'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : act.status === 'In Progress'
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                            : 'bg-slate-800 text-slate-400'
                        }`}>
                          {act.status}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1">{act.analyst_notes}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 py-4 text-center">No mitigation actions defined.</p>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-cyber-border text-[11px] text-slate-400 flex items-center justify-between">
            <span>Simulated Playbook Execution Mode</span>
            <span className="text-emerald-400 font-mono font-semibold">Ready</span>
          </div>
        </div>

        {/* Investigation Notes Thread */}
        <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Analyst Investigation Notes & Findings
              </h3>
            </div>

            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {notes && notes.length > 0 ? (
                notes.map((note) => (
                  <div key={note.id} className="p-3 rounded-lg bg-slate-900/90 border border-slate-800">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-cyan-400 flex items-center space-x-1.5">
                        <User className="w-3.5 h-3.5" />
                        <span>{note.author}</span>
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {note.created_at?.replace('T', ' ')?.slice(0, 16)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed">{note.note}</p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 py-6 text-center">No analyst notes recorded yet.</p>
              )}
            </div>
          </div>

          {/* Add Note Form */}
          <form onSubmit={handleAddNote} className="mt-4 pt-3 border-t border-cyber-border flex items-center space-x-2">
            <input
              type="text"
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Record forensic observation, containment action, or hypothesis..."
              className="flex-1 py-2 px-3 rounded-lg bg-slate-900 border border-cyber-border text-white text-xs focus:outline-none focus:border-cyan-400 font-mono"
            />
            <button
              type="submit"
              disabled={submittingNote || !newNote.trim()}
              className="p-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white transition-colors shrink-0"
              title="Add Note"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
