import React, { useState, useEffect } from 'react';
import {
  FileDown,
  FileText,
  FileSpreadsheet,
  Download,
  Shield,
  CheckCircle,
  Clock,
  Layers,
  Sparkles
} from 'lucide-react';
import api from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const ReportsPage = () => {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const res = await api.get('/incidents');
        setIncidents(res.data);
        if (res.data.length > 0) {
          setSelectedIncidentId(res.data[0].id);
        }
      } catch (err) {
        console.error("Failed to load incidents for report page", err);
      } finally {
        setLoading(false);
      }
    };
    fetchIncidents();
  }, []);

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-xl font-extrabold text-white tracking-wider flex items-center space-x-2">
          <FileDown className="w-5 h-5 text-cyan-400" />
          <span>Forensic Incident Report & Compliance Export Center</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Automated ReportLab PDF document compilation and CSV data feeds for academic evaluation and leadership briefing.
        </p>
      </div>

      {/* Main Report Export Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Executive Summary PDF */}
        <div className="p-6 rounded-xl bg-cyber-card border border-cyber-border hover:border-cyan-500/50 transition-all flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center mb-4 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">Executive Security Operations Summary</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Comprehensive executive overview containing DEFCON threat posture, MTTR statistics, incident distributions by severity and attack category, top targeted assets, and strategic security hardening recommendations.
            </p>

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5 text-[11px] font-mono text-slate-400 mb-6">
              <div className="flex justify-between">
                <span>Format:</span>
                <span className="text-cyan-400 font-bold">ReportLab PDF (Two-Pass Canvas)</span>
              </div>
              <div className="flex justify-between">
                <span>Audience:</span>
                <span className="text-slate-200">CISO, Academic Faculty, SOC Lead</span>
              </div>
              <div className="flex justify-between">
                <span>Scope:</span>
                <span className="text-emerald-400">All Correlated Platform Incidents</span>
              </div>
            </div>
          </div>

          <a
            href="/api/reports/summary/pdf"
            download="SentinelX_Executive_Security_Summary.pdf"
            className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            <Download className="w-4 h-4" />
            <span>Download Executive Summary PDF</span>
          </a>
        </div>

        {/* Individual Incident Forensic Investigation PDF */}
        <div className="p-6 rounded-xl bg-cyber-card border border-cyber-border hover:border-purple-500/50 transition-all flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/30 flex items-center justify-center mb-4 shadow-[0_0_15px_rgba(139,92,246,0.2)]">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">Individual Incident Forensic Report</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Detailed 12-section technical investigation docket including executive summary, raw correlated evidence logs, root cause analysis, 6-stage lifecycle timeline, mitigation response checklist, and analyst sign-off footer.
            </p>

            {/* Incident selector */}
            <div className="mb-6">
              <label className="block text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
                Select Case to Generate:
              </label>
              <select
                value={selectedIncidentId}
                onChange={(e) => setSelectedIncidentId(e.target.value)}
                disabled={loading || incidents.length === 0}
                className="w-full py-2.5 px-3 rounded-lg bg-slate-900 border border-cyber-border text-white text-xs font-mono focus:outline-none focus:border-cyan-400"
              >
                {incidents.map((inc) => (
                  <option key={inc.id} value={inc.id}>
                    [{inc.incident_id}] {inc.severity} - {inc.title.slice(0, 40)}...
                  </option>
                ))}
              </select>
            </div>
          </div>

          <a
            href={`/api/reports/incident/${selectedIncidentId}/pdf`}
            download={`SentinelX_Incident_${selectedIncidentId}_Investigation.pdf`}
            className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-[0_0_15px_rgba(139,92,246,0.3)]"
          >
            <Download className="w-4 h-4" />
            <span>Generate Incident Forensic PDF</span>
          </a>
        </div>
      </div>

      {/* CSV Raw Data Exports */}
      <div className="p-6 rounded-xl bg-cyber-card border border-cyber-border">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2 flex items-center space-x-2">
          <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
          <span>Raw Structured CSV Telemetry Exports</span>
        </h3>
        <p className="text-xs text-slate-400 mb-6">
          Export full database tables for external SIEM integration, forensic archiving, or spreadsheet verification.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <h4 className="text-xs font-bold text-white">Security Incidents CSV</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">All classified cases with root cause & status</p>
            </div>
            <a
              href="/api/reports/incidents/csv"
              download="sentinelx_incidents.csv"
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold border border-cyber-border transition-colors flex items-center space-x-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </a>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <h4 className="text-xs font-bold text-white">Ingested Security Logs CSV</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">Raw event logs with IPs, timestamps, & payloads</p>
            </div>
            <a
              href="/api/reports/logs/csv"
              download="sentinelx_security_logs.csv"
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-emerald-400 text-xs font-semibold border border-cyber-border transition-colors flex items-center space-x-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
