import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Cpu,
  KeyRound,
  Radar,
  UserCheck,
  Bug,
  HardDriveUpload,
  ShieldBan,
  Activity,
  Mail,
  RotateCcw,
  CheckCircle2,
  Terminal,
  ArrowRight,
  Flame,
  AlertTriangle,
  Play
} from 'lucide-react';
import api from '../services/api';
import { useDashboard } from '../context/DashboardContext';
import { Modal } from '../components/common/Modal';

export const SimulationPage = () => {
  const { triggerRefresh } = useDashboard();
  const navigate = useNavigate();

  const [activeSimulation, setActiveSimulation] = useState(null);
  const [simulationLog, setSimulationLog] = useState([]);
  const [lastResult, setLastResult] = useState(null);
  const [simHistory, setSimHistory] = useState([]);
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [resetting, setResetting] = useState(false);

  const fetchHistory = async () => {
    try {
      const res = await api.get('/simulation/history');
      setSimHistory(res.data);
    } catch (err) {
      console.error("Failed to fetch simulation history", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const runSimulation = async (type, name) => {
    setActiveSimulation(type);
    const steps = [
      `[*] Initializing synthetic test scenario: ${name}`,
      `[*] Generating randomized RFC compliant network telemetry...`,
      `[+] Persisting raw logs into SQLite security_logs table...`,
      `[*] Invoking SentinelX Detection Engine rule evaluator...`
    ];

    setSimulationLog(steps);
    setLastResult(null);

    try {
      const res = await api.post(`/simulation/trigger/${type}`);
      const data = res.data.data;
      setLastResult(data);

      setSimulationLog((prev) => [
        ...prev,
        `[✓] Rule Match: ${data.alerts_created} alert(s) generated successfully!`,
        `[✓] Incident Correlation: ${data.incidents_created} incident(s) registered/updated.`,
        `[✓] Global SOC dashboard state updated.`
      ]);

      // Automatically refresh dashboard and fetch updated history
      triggerRefresh();
      fetchHistory();
    } catch (err) {
      setSimulationLog((prev) => [
        ...prev,
        `[!] ERROR: Failed to execute simulation: ${err.response?.data?.error || err.message}`
      ]);
    } finally {
      setActiveSimulation(null);
    }
  };

  const handleResetConfirm = async () => {
    setResetting(true);
    try {
      await api.post('/simulation/reset');
      setResetModalOpen(false);
      setSimulationLog([
        "[*] Full SOC Demo Data reset initiated...",
        "[✓] Cleared dynamic test logs, alerts, and incidents.",
        "[✓] Re-seeded baseline dataset: 2 Users, 5 Threat Feeds, 4 Baseline Incidents."
      ]);
      setLastResult(null);
      triggerRefresh();
      fetchHistory();
    } catch (err) {
      console.error("Reset failed", err);
    } finally {
      setResetting(false);
    }
  };

  // 8 Detection Rule Simulations
  const simulations = [
    {
      type: 'brute_force',
      name: 'Brute Force Attack',
      description: 'Generates 7 rapid failed SSH/RDP authentication attempts within 2 minutes targeting administrative accounts.',
      rule: 'Rule 001: Brute Force Detection (>5 failed attempts in 5m)',
      severity: 'Critical / High',
      icon: KeyRound,
      color: 'red',
    },
    {
      type: 'port_scan',
      name: 'Port Scanning Reconnaissance',
      description: 'Simulates TCP SYN port sweep across 14 distinct services (21, 22, 80, 443, 3389, 8080) to detect open services.',
      rule: 'Rule 002: Reconnaissance Port Sweep (>=5 distinct ports)',
      severity: 'High / Medium',
      icon: Radar,
      color: 'orange',
    },
    {
      type: 'suspicious_login',
      name: 'Suspicious Login / Credential Stuffing',
      description: 'Generates multiple failed Web SSO authentications immediately followed by a successful login from an anomalous IP.',
      rule: 'Rule 003: Post-Failure Successful Login Anomaly',
      severity: 'High',
      icon: UserCheck,
      color: 'orange',
    },
    {
      type: 'malware',
      name: 'Malware & EDR Indicator',
      description: 'Simulates execution of mimikatz.exe credential dumping, encoded PowerShell commands, and shadow copy deletion.',
      rule: 'Rule 004: Malware & Suspicious Process Activity',
      severity: 'Critical',
      icon: Bug,
      color: 'red',
    },
    {
      type: 'data_exfiltration',
      name: 'Data Exfiltration Surge',
      description: 'Simulates high-volume outbound data streaming (>24MB) from production database vaults to unclassified external cloud IPs.',
      rule: 'Rule 005: Abnormal Outbound Data Egress (>15MB)',
      severity: 'Critical',
      icon: HardDriveUpload,
      color: 'purple',
    },
    {
      type: 'unauthorized_access',
      name: 'Unauthorized Access & Traversal',
      description: 'Simulates path traversal (../../etc/shadow) and SQL injection (UNION SELECT) probes hitting web API endpoints.',
      rule: 'Rule 006: Privilege Violation & Directory Traversal',
      severity: 'High',
      icon: ShieldBan,
      color: 'orange',
    },
    {
      type: 'ddos',
      name: 'Denial of Service (DDoS)',
      description: 'Simulates a volumetric HTTP flood surge of 20 rapid bursts within seconds overwhelming search catalog endpoints.',
      rule: 'Rule 007: Volumetric Request Flood / Traffic Surge',
      severity: 'Critical / High',
      icon: Activity,
      color: 'red',
    },
    {
      type: 'phishing',
      name: 'Phishing & Malicious Domain',
      description: 'Simulates employee workstation navigating to deceptive credential-harvesting domain login-verify-corp.xyz and opening invoice.xlsm.',
      rule: 'Rule 008: Phishing Indicators & Credential Harvester',
      severity: 'High',
      icon: Mail,
      color: 'cyan',
    },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Reset Button */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-wider flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span>Cybersecurity Attack Simulation Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Execute controlled synthetic attack scenarios across all 8 detection rules to evaluate real-time SOC response.
          </p>
        </div>

        <button
          onClick={() => setResetModalOpen(true)}
          className="px-3.5 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-semibold flex items-center space-x-2 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset Demo Data</span>
        </button>
      </div>

      {/* Confirmation Modal for Reset */}
      <Modal
        isOpen={resetModalOpen}
        onClose={() => setResetModalOpen(false)}
        onConfirm={handleResetConfirm}
        title="Reset All SOC Demo Data?"
        message="This action will delete all dynamically created test logs, generated alerts, and incidents, returning the SentinelX database to its clean baseline state."
        confirmText="Confirm Reset"
        isDanger={true}
        confirmLoading={resetting}
      />

      {/* Live Simulation Terminal Console */}
      <div className="rounded-xl bg-slate-950 border border-cyber-border overflow-hidden shadow-2xl">
        <div className="p-3 bg-slate-900 border-b border-cyber-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-mono font-bold text-slate-300">
              SOC SIMULATION ENGINE CONSOLE [AUTOPILOT]
            </span>
          </div>
          <span className="flex items-center space-x-1.5 text-[11px] font-mono text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Interactive Sandbox Ready</span>
          </span>
        </div>

        <div className="p-4 font-mono text-xs space-y-1.5 min-h-[120px] max-h-56 overflow-y-auto bg-black/60">
          {simulationLog.length > 0 ? (
            simulationLog.map((log, idx) => (
              <div
                key={idx}
                className={
                  log.startsWith('[✓]')
                    ? 'text-emerald-400'
                    : log.startsWith('[!]')
                    ? 'text-red-400'
                    : log.startsWith('[+]')
                    ? 'text-cyan-400'
                    : 'text-slate-400'
                }
              >
                {log}
              </div>
            ))
          ) : (
            <div className="text-slate-500 italic py-4">
              Select any of the 8 attack simulations below to launch realistic synthetic traffic and watch the detection engine correlate incidents in real time...
            </div>
          )}
        </div>

        {/* Success Banner with Navigation to Detected Incident */}
        {lastResult && (
          <div className="p-3 bg-cyan-950/40 border-t border-cyan-800/40 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-cyan-300 font-mono">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>
                Generated: <b>{lastResult.logs_generated}</b> logs | Created: <b>{lastResult.alerts_created}</b> alerts, <b>{lastResult.incidents_created}</b> incidents
              </span>
            </div>
            {lastResult.incidents && lastResult.incidents.length > 0 && (
              <button
                onClick={() => navigate(`/incidents/${lastResult.incidents[0].id}`)}
                className="px-3 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-bold font-mono flex items-center space-x-1 transition-all"
              >
                <span>Investigate Incident {lastResult.incidents[0].incident_id}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* 8 Attack Simulation Cards Grid */}
      <div>
        <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center space-x-2">
          <span>Available Threat Scenarios (All 8 Detection Rules)</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
            8 / 8 Fully Implemented
          </span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {simulations.map((sim) => {
            const Icon = sim.icon;
            const isRunning = activeSimulation === sim.type;

            return (
              <div
                key={sim.type}
                className="p-5 rounded-xl bg-cyber-card border border-cyber-border hover:border-slate-600 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-cyan-400">
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                      {sim.severity}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white mb-1.5">{sim.name}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed mb-3">{sim.description}</p>
                  
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800 mb-4 text-[10px] font-mono text-cyan-300">
                    {sim.rule}
                  </div>
                </div>

                <button
                  onClick={() => runSimulation(sim.type, sim.name)}
                  disabled={isRunning || activeSimulation !== null}
                  className="w-full py-2.5 px-3 rounded-lg bg-cyan-600/90 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold flex items-center justify-center space-x-2 transition-all shadow-[0_0_12px_rgba(6,182,212,0.25)]"
                >
                  {isRunning ? (
                    <>
                      <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      <span>Injecting & Detecting...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Simulate Attack</span>
                    </>
                  )}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Simulation History Table */}
      <div className="rounded-xl bg-cyber-card border border-cyber-border overflow-hidden">
        <div className="p-4 bg-slate-900/90 border-b border-cyber-border flex items-center justify-between">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Attack Simulation Audit Trail
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">Verified Execution Records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-slate-400 uppercase font-mono tracking-wider border-b border-cyber-border">
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Simulation Scenario</th>
                <th className="py-2.5 px-4">Logs Injected</th>
                <th className="py-2.5 px-4">Alerts Fired</th>
                <th className="py-2.5 px-4">Incidents Linked</th>
                <th className="py-2.5 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/50 font-mono">
              {simHistory && simHistory.length > 0 ? (
                simHistory.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-4 text-slate-400 whitespace-nowrap">
                      {h.timestamp?.replace('T', ' ')?.slice(0, 19)}
                    </td>
                    <td className="py-2.5 px-4 text-white font-bold">{h.simulation_name}</td>
                    <td className="py-2.5 px-4 text-cyan-400">{h.logs_generated}</td>
                    <td className="py-2.5 px-4 text-orange-400">{h.alerts_generated}</td>
                    <td className="py-2.5 px-4 text-purple-400">{h.incidents_created}</td>
                    <td className="py-2.5 px-4 text-emerald-400">{h.status}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-slate-500 text-xs">
                    No simulations executed yet.
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
