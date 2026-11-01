import React, { useState, useEffect } from 'react';
import {
  Upload,
  Search,
  Filter,
  FileSpreadsheet,
  FileCode,
  Download,
  CheckCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Database,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';
import { useDashboard } from '../context/DashboardContext';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const LogsPage = () => {
  const { triggerRefresh } = useDashboard();
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('ALL');
  const [status, setStatus] = useState('ALL');

  // File upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        per_page: 15,
        search: search.trim(),
        event_type: category,
        status,
      };
      const res = await api.get('/logs/list', { params });
      setLogs(res.data.logs);
      setTotal(res.data.total);
      setTotalPages(res.data.total_pages);
    } catch (err) {
      console.error("Failed to fetch logs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, category, status]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError("Please select a valid CSV or JSON log file.");
      return;
    }

    setUploading(true);
    setUploadError('');
    setUploadResult(null);

    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      const res = await api.post('/logs/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadResult(res.data);
      setUploadFile(null);
      // Trigger global dashboard refresh
      triggerRefresh();
      // Re-fetch current page
      fetchLogs();
    } catch (err) {
      setUploadError(err.response?.data?.error || "Failed to process log file upload.");
    } finally {
      setUploading(false);
    }
  };

  const categories = ['ALL', 'Authentication', 'Network', 'Firewall', 'System', 'Application', 'Endpoint'];
  const statuses = ['ALL', 'SUCCESS', 'FAILED', 'BLOCKED', 'ALLOWED', 'ALERT'];

  return (
    <div className="space-y-6">
      {/* Top Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-wider flex items-center space-x-2">
            <Database className="w-5 h-5 text-cyan-400" />
            <span>Security Log Management & Ingestion</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Ingest, parse, index, and validate enterprise telemetry logs across all 6 core categories.
          </p>
        </div>

        {/* Sample Log Downloads */}
        <div className="flex items-center space-x-2">
          <a
            href="/api/logs/sample/csv"
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-cyber-border transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Sample CSV</span>
            <Download className="w-3 h-3 ml-0.5 text-slate-400" />
          </a>
          <a
            href="/api/logs/sample/json"
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-cyber-border transition-colors"
          >
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            <span>Sample JSON</span>
            <Download className="w-3 h-3 ml-0.5 text-slate-400" />
          </a>
        </div>
      </div>

      {/* Ingestion Upload Card */}
      <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2 flex items-center space-x-2">
          <Upload className="w-4 h-4 text-cyan-400" />
          <span>Ingest New Security Logs (CSV / JSON)</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Upload structured logs. The detection engine will automatically validate records and evaluate rules.
        </p>

        {uploadError && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}

        {uploadResult && (
          <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs space-y-1">
            <div className="flex items-center space-x-2 font-bold">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{uploadResult.message}</span>
            </div>
            <div className="pl-6 text-[11px] text-slate-300 font-mono space-x-4">
              <span>Imported: <b>{uploadResult.imported_count}</b> records</span>
              <span>Duplicate skipped: <b>{uploadResult.duplicate_count}</b></span>
              <span className="text-cyan-400">
                Rule Alerts Generated: <b>{uploadResult.detection_engine?.alerts_created || 0}</b>
              </span>
              <span className="text-orange-400">
                Incidents Created: <b>{uploadResult.detection_engine?.incidents_created || 0}</b>
              </span>
            </div>
          </div>
        )}

        <form onSubmit={handleFileUpload} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="w-full relative">
            <input
              type="file"
              accept=".csv,.json"
              onChange={(e) => setUploadFile(e.target.files[0] || null)}
              className="w-full text-xs text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-cyan-400 hover:file:bg-slate-700 cursor-pointer bg-slate-900/60 rounded-lg border border-cyber-border"
            />
          </div>
          <button
            type="submit"
            disabled={uploading || !uploadFile}
            className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold shrink-0 transition-all flex items-center justify-center space-x-2"
          >
            {uploading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Parsing & Evaluating...</span>
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                <span>Upload & Run Engine</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Filters & Search Toolbar */}
      <div className="p-4 rounded-xl bg-cyber-card border border-cyber-border flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="w-full md:w-96 relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search IP, username, hostname, description..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-cyber-border text-white text-xs focus:outline-none focus:border-cyan-400 font-mono"
          />
        </form>

        {/* Category & Status Selectors */}
        <div className="flex items-center space-x-3 w-full md:w-auto justify-end">
          <div className="flex items-center space-x-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Category:</span>
          </div>
          <select
            value={category}
            onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            className="py-1.5 px-3 rounded-lg bg-slate-900 border border-cyber-border text-slate-200 text-xs focus:outline-none focus:border-cyan-400 font-medium"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>

          <span className="text-xs text-slate-400">Status:</span>
          <select
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1); }}
            className="py-1.5 px-3 rounded-lg bg-slate-900 border border-cyber-border text-slate-200 text-xs focus:outline-none focus:border-cyan-400 font-medium"
          >
            {statuses.map((st) => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Security Logs Table */}
      <div className="rounded-xl bg-cyber-card border border-cyber-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-900/90 text-slate-400 uppercase font-mono tracking-wider border-b border-cyber-border">
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Source IP</th>
                <th className="py-3 px-4">Destination IP</th>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Host / Port</th>
                <th className="py-3 px-4">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/60">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center">
                    <LoadingSpinner message="Filtering log records..." />
                  </td>
                </tr>
              ) : logs && logs.length > 0 ? (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-300 whitespace-nowrap">
                      {log.timestamp?.replace('T', ' ')?.slice(0, 19)}
                    </td>
                    <td className="py-3 px-4 font-mono text-cyan-400 font-bold whitespace-nowrap">
                      {log.source_ip}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                      {log.destination_ip || 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-slate-200 font-medium">
                      {log.username || '-'}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px] font-mono text-slate-300">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-white">
                      {log.action}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                        log.status === 'FAILED' || log.status === 'BLOCKED' || log.status === 'ALERT'
                          ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                      {log.hostname}:{log.port || 0}
                    </td>
                    <td className="py-3 px-4 text-slate-300 max-w-xs truncate" title={log.description}>
                      {log.description}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500 text-xs">
                    No log events match current query parameters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-900/60 border-t border-cyber-border flex items-center justify-between text-xs text-slate-400">
          <span>
            Showing page <b>{page}</b> of <b>{totalPages || 1}</b> ({total} records total)
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 text-white"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-cyan-400 font-bold px-2">{page}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700 text-white"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
