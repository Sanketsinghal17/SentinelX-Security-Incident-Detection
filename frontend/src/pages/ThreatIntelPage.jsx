import React, { useState, useEffect } from 'react';
import {
  Globe2,
  Search,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Server,
  MapPin,
  ExternalLink,
  PlusCircle,
  Database
} from 'lucide-react';
import api from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const ThreatIntelPage = () => {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);

  // IP Search State
  const [searchIp, setSearchIp] = useState('185.220.101.45');
  const [lookupResult, setLookupResult] = useState(null);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState('');

  const fetchThreats = async () => {
    try {
      const res = await api.get('/threat-intel/list');
      setThreats(res.data);
    } catch (err) {
      console.error("Failed to fetch threat list", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLookup = async (ipToQuery) => {
    const ip = ipToQuery || searchIp.trim();
    if (!ip) return;

    setLookupLoading(true);
    setLookupError('');
    try {
      const res = await api.get(`/threat-intel/lookup/${ip}`);
      setLookupResult(res.data);
    } catch (err) {
      setLookupError("Failed to lookup IP reputation.");
    } finally {
      setLookupLoading(false);
    }
  };

  useEffect(() => {
    fetchThreats();
    handleLookup('185.220.101.45');
  }, []);

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-red-400 border-red-500/40 bg-red-500/10 shadow-[0_0_15px_rgba(239,68,68,0.25)]';
    if (score >= 50) return 'text-orange-400 border-orange-500/40 bg-orange-500/10';
    return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-wider flex items-center space-x-2">
            <Globe2 className="w-5 h-5 text-cyan-400" />
            <span>Threat Intelligence & IP Reputation</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Local threat telemetry database, malicious indicator scoring, and adversary intelligence lookup.
          </p>
        </div>
      </div>

      {/* IP Reputation Lookup Card */}
      <div className="p-5 rounded-xl bg-cyber-card border border-cyber-border shadow-xl">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2 flex items-center space-x-2">
          <Search className="w-4 h-4 text-cyan-400" />
          <span>Adversary IP Telemetry Lookup</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Query IP addresses against verified SOC feeds. Non-cataloged public IPs will evaluate via simulated scoring engine.
        </p>

        <form onSubmit={(e) => { e.preventDefault(); handleLookup(); }} className="flex items-center gap-3 max-w-2xl">
          <div className="relative flex-1">
            <input
              type="text"
              value={searchIp}
              onChange={(e) => setSearchIp(e.target.value)}
              placeholder="e.g. 185.220.101.45, 91.240.118.88, 10.0.1.15..."
              className="w-full pl-4 pr-4 py-2.5 rounded-lg bg-slate-900 border border-cyber-border text-white text-xs focus:outline-none focus:border-cyan-400 font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={lookupLoading}
            className="px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all shrink-0 flex items-center space-x-2 shadow-[0_0_12px_rgba(6,182,212,0.3)]"
          >
            {lookupLoading ? <span>Searching...</span> : <span>Query Reputation</span>}
          </button>
        </form>

        {/* Lookup Result Box */}
        {lookupResult && (
          <div className="mt-6 p-5 rounded-xl bg-slate-900/90 border border-cyber-border">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-cyber-border">
              <div className="flex items-center space-x-4">
                <div className={`p-4 rounded-xl border flex flex-col items-center justify-center font-mono ${getScoreColor(lookupResult.reputation_score)}`}>
                  <span className="text-2xl font-black">{lookupResult.reputation_score}</span>
                  <span className="text-[9px] uppercase tracking-wider font-bold">Threat Score</span>
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-lg font-mono font-bold text-white">{lookupResult.ip_address}</span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                      lookupResult.is_known_attacker
                        ? 'bg-red-950 text-red-400 border border-red-800'
                        : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}>
                      {lookupResult.is_known_attacker ? 'CONFIRMED MALICIOUS' : 'BENIGN / UNCLASSIFIED'}
                    </span>
                  </div>
                  <p className="text-xs text-cyan-400 font-medium mt-0.5">{lookupResult.threat_type}</p>
                </div>
              </div>

              <div className="text-xs text-slate-400 space-y-1 text-right">
                <p>Telemetry Source: <b className="text-slate-200">{lookupResult.data_source}</b></p>
                <p>Reported Incidents: <b className="text-cyan-400 font-mono">{lookupResult.reports_count}</b></p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 text-xs">
              <div className="flex items-start space-x-2">
                <MapPin className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-400">Origin Geolocation</p>
                  <p className="font-semibold text-white">{lookupResult.country}</p>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <Server className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-400">Autonomous System / ISP</p>
                  <p className="font-semibold text-white">{lookupResult.isp}</p>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <Database className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-400">Analyst Telemetry Notes</p>
                  <p className="text-slate-300 leading-snug">{lookupResult.notes}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Cataloged Threat Intelligence Feed */}
      <div className="rounded-xl bg-cyber-card border border-cyber-border overflow-hidden">
        <div className="p-4 bg-slate-900/90 border-b border-cyber-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-red-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              Cataloged Threat Indicators & Blocklist Feeds
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">{threats?.length || 0} Indicators Active</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-slate-400 uppercase font-mono tracking-wider border-b border-cyber-border">
                <th className="py-3 px-4">Threat Indicator IP</th>
                <th className="py-3 px-4">Reputation Score</th>
                <th className="py-3 px-4">Threat Classification</th>
                <th className="py-3 px-4">Origin Country</th>
                <th className="py-3 px-4">Hosting ISP</th>
                <th className="py-3 px-4">Reports</th>
                <th className="py-3 px-4">Analyst Notes</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/50">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center">
                    <LoadingSpinner message="Querying threat intelligence database..." />
                  </td>
                </tr>
              ) : threats && threats.length > 0 ? (
                threats.map((threat) => (
                  <tr key={threat.id} className="hover:bg-slate-800/30">
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400 whitespace-nowrap">
                      {threat.ip_address}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                        threat.reputation_score >= 80
                          ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                          : 'bg-orange-500/10 text-orange-400 border border-orange-500/30'
                      }`}>
                        {threat.reputation_score} / 100
                      </span>
                    </td>
                    <td className="py-3 px-4 text-white font-medium whitespace-nowrap">
                      {threat.threat_type}
                    </td>
                    <td className="py-3 px-4 text-slate-300 whitespace-nowrap">
                      {threat.country}
                    </td>
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                      {threat.isp}
                    </td>
                    <td className="py-3 px-4 font-mono text-cyan-400">
                      {threat.reports_count}
                    </td>
                    <td className="py-3 px-4 text-slate-300 max-w-xs truncate" title={threat.notes}>
                      {threat.notes}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => { setSearchIp(threat.ip_address); handleLookup(threat.ip_address); }}
                        className="text-cyan-400 hover:text-cyan-300 text-[11px] font-semibold underline"
                      >
                        Lookup
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500 text-xs">
                    No threat intelligence indicators found.
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
