import React, { useState, useEffect } from 'react';
import {
  Radio,
  Cpu,
  Activity,
  Shield,
  Zap,
  Terminal,
  FileCode,
  RefreshCw,
  Check,
  XOctagon,
  Shuffle,
  PauseCircle,
  BadgeDollarSign,
  Clock,
  Server,
  Layers,
  ArrowRight,
  AlertTriangle,
  Bot,
  Globe,
  Cable,
  MonitorSmartphone
} from 'lucide-react';
import {
  AgentryApi,
  McpUsageResponse,
  SourceMetrics,
  AuditEvent,
} from '../services/api.ts';

const SOURCE_META: Record<string, { label: string; icon: React.ReactNode; color: string; desc: string }> = {
  mcp: {
    label: 'MCP Server',
    icon: <Cable className="w-4 h-4" />,
    color: 'text-sentry-violet',
    desc: 'Claude Desktop, Cursor IDE, Windsurf agents via Model Context Protocol',
  },
  rest: {
    label: 'REST API',
    icon: <Globe className="w-4 h-4" />,
    color: 'text-sentry-cyan',
    desc: 'Direct HTTP calls via POST /v1/audit, Python SDK, cURL',
  },
  proxy: {
    label: 'OpenAI Proxy',
    icon: <Server className="w-4 h-4" />,
    color: 'text-sentry-emerald',
    desc: 'Zero-code middleware via POST /v1/chat/completions',
  },
  frontend: {
    label: 'Frontend UI',
    icon: <MonitorSmartphone className="w-4 h-4" />,
    color: 'text-amber-400',
    desc: 'Attack Simulator & interactive playground on this dashboard',
  },
};

export const McpUsageMonitor: React.FC = () => {
  const [usage, setUsage] = useState<McpUsageResponse | null>(null);
  const [mcpEvents, setMcpEvents] = useState<AuditEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [notification, setNotification] = useState<string | null>(null);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 4000);
  };

  const refreshData = async () => {
    try {
      const [usageRes, mcpEventsRes] = await Promise.all([
        AgentryApi.getMcpUsage(),
        AgentryApi.getEventsBySource('mcp', 10),
      ]);
      setUsage(usageRes);
      setMcpEvents(mcpEventsRes.events || []);
    } catch (err) {
      console.error('Failed to fetch MCP usage data', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Simulate an MCP audit call to demonstrate the integration
  const handleSimulateMcpCall = async () => {
    showToast('Simulating MCP tool invocation → agentry_audit_step ...');
    try {
      await AgentryApi.auditStep({
        session_id: `mcp_cursor_session_${Date.now()}`,
        tool_name: 'edit_file',
        input_text: 'Applying code patch to src/utils/auth.ts',
        thought_trace: 'Agent editing authentication middleware to add rate limiting',
        agent_role: 'MCP-Agent',
        model_name: 'claude-sonnet-4',
        latency_ms: 12.3,
      });
      await refreshData();
      showToast('MCP tool call audited successfully — check the live feed below!');
    } catch (err) {
      showToast('Simulation error: ' + (err as Error).message);
    }
  };

  // Calculate totals across all sources
  const allSources = usage?.sources || {};
  const sourceKeys = Object.keys(allSources);
  const totalSteps = sourceKeys.reduce((sum, k) => sum + (allSources[k]?.total_steps || 0), 0);
  const totalSessions = sourceKeys.reduce((sum, k) => sum + (allSources[k]?.unique_sessions || 0), 0);
  const totalTokensSaved = sourceKeys.reduce((sum, k) => sum + (allSources[k]?.tokens_saved || 0), 0);
  const totalCostSaved = sourceKeys.reduce((sum, k) => sum + (allSources[k]?.cost_saved_usd || 0), 0);

  // Get source-specific events when a source is selected
  const [sourceEvents, setSourceEvents] = useState<AuditEvent[]>([]);
  useEffect(() => {
    if (selectedSource) {
      AgentryApi.getEventsBySource(selectedSource, 8).then((res) => {
        setSourceEvents(res.events || []);
      });
    }
  }, [selectedSource]);

  return (
    <div className="flex-grow max-w-7xl mx-auto w-full px-4 lg:px-8 py-10 space-y-10 bg-black">

      {/* Toast */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#0E1520] border border-sentry-violet/40 p-4 rounded-xl text-xs font-mono text-sentry-violet shadow-2xl flex items-center gap-3 animate-fade-in">
          <Check className="w-4 h-4 text-sentry-violet shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* ================================================================= */}
      {/* HEADER                                                            */}
      {/* ================================================================= */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sentry-violet/10 border border-sentry-violet/20 text-sentry-violet text-xs font-mono font-medium mb-2">
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span>MCP INTEGRATION MONITOR • LIVE USAGE TELEMETRY</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-white tracking-tight">
            MCP ↔ Frontend Usage Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time visibility into every MCP tool invocation, REST API call, and OpenAI proxy request — all tracked in a unified audit trail.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={handleSimulateMcpCall}
            className="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-sentry-violet/15 hover:bg-sentry-violet/25 text-sentry-violet border border-sentry-violet/30 text-xs font-mono font-semibold transition-all hover:scale-[1.02]"
          >
            <Cable className="w-4 h-4" />
            <span>Simulate MCP Tool Call</span>
          </button>
          <button
            onClick={() => { refreshData(); showToast('Dashboard refreshed.'); }}
            className="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 text-xs font-mono transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* ================================================================= */}
      {/* AGGREGATE KPI CARDS                                                */}
      {/* ================================================================= */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">

        <div className="glass-card rounded-2xl p-5 border border-white/10 hover:border-white/20 transition-colors">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-mono uppercase tracking-wider">Total Integrations</span>
            <div className="w-8 h-8 rounded-lg bg-sentry-violet/10 flex items-center justify-center">
              <Layers className="w-4 h-4 text-sentry-violet" />
            </div>
          </div>
          <div className="text-3xl font-bold font-mono text-white mb-1">
            {sourceKeys.length} Source{sourceKeys.length !== 1 ? 's' : ''}
          </div>
          <div className="text-xs text-slate-400 font-mono">
            {sourceKeys.map(k => SOURCE_META[k]?.label || k).join(', ') || 'No data yet'}
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-white/10 hover:border-white/20 transition-colors">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-mono uppercase tracking-wider">Total Audited Steps</span>
            <div className="w-8 h-8 rounded-lg bg-sentry-cyan/10 flex items-center justify-center">
              <Activity className="w-4 h-4 text-sentry-cyan" />
            </div>
          </div>
          <div className="text-3xl font-bold font-mono text-sentry-cyan mb-1">
            {totalSteps.toLocaleString()}
          </div>
          <div className="text-xs text-slate-400 font-mono">
            Across {totalSessions} unique sessions
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-white/10 hover:border-white/20 transition-colors">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-mono uppercase tracking-wider">Tokens Saved</span>
            <div className="w-8 h-8 rounded-lg bg-sentry-emerald/10 flex items-center justify-center">
              <Zap className="w-4 h-4 text-sentry-emerald" />
            </div>
          </div>
          <div className="text-3xl font-bold font-mono text-sentry-emerald mb-1">
            {totalTokensSaved.toLocaleString()}
          </div>
          <div className="text-xs text-slate-400 font-mono">
            By early interception across all sources
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5 border border-white/10 hover:border-white/20 transition-colors">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="font-mono uppercase tracking-wider">Cost Saved</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <BadgeDollarSign className="w-4 h-4 text-amber-400" />
            </div>
          </div>
          <div className="text-3xl font-bold font-mono text-amber-400 mb-1">
            ${totalCostSaved.toFixed(2)}
          </div>
          <div className="text-xs text-slate-400 font-mono">
            Total USD preserved by TabPFN interventions
          </div>
        </div>

      </div>

      {/* ================================================================= */}
      {/* SOURCE BREAKDOWN CARDS                                             */}
      {/* ================================================================= */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-white/10">
          <div className="w-8 h-8 rounded-xl bg-sentry-violet/15 text-sentry-violet border border-sentry-violet/30 flex items-center justify-center font-mono font-bold text-sm shrink-0">
            <Cable className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">
              Integration Source Breakdown
            </h2>
            <p className="text-xs text-slate-400">
              Click a source card to see its recent audit events. All sources share the same SQLite WAL audit trail.
            </p>
          </div>
        </div>

        {/* Architecture Diagram */}
        <div className="glass-card rounded-2xl p-6 border border-white/10">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="w-4 h-4 text-sentry-cyan" />
            <h3 className="font-bold text-white text-sm">Live Integration Architecture</h3>
          </div>
          <div className="p-4 rounded-xl bg-black/60 border border-white/5">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-center">
              {/* Source Nodes */}
              <div className="space-y-2">
                <div className="p-2.5 rounded-lg bg-sentry-violet/10 border border-sentry-violet/20 text-center">
                  <Cable className="w-4 h-4 text-sentry-violet mx-auto mb-1" />
                  <div className="text-[10px] font-mono text-sentry-violet font-bold">MCP Server</div>
                  <div className="text-[9px] text-slate-400">Cursor / Claude</div>
                </div>
                <div className="p-2.5 rounded-lg bg-sentry-cyan/10 border border-sentry-cyan/20 text-center">
                  <Globe className="w-4 h-4 text-sentry-cyan mx-auto mb-1" />
                  <div className="text-[10px] font-mono text-sentry-cyan font-bold">REST API</div>
                  <div className="text-[9px] text-slate-400">Python SDK / cURL</div>
                </div>
                <div className="p-2.5 rounded-lg bg-sentry-emerald/10 border border-sentry-emerald/20 text-center">
                  <Server className="w-4 h-4 text-sentry-emerald mx-auto mb-1" />
                  <div className="text-[10px] font-mono text-sentry-emerald font-bold">OpenAI Proxy</div>
                  <div className="text-[9px] text-slate-400">/v1/chat/completions</div>
                </div>
              </div>

              {/* Arrow */}
              <div className="flex items-center justify-center">
                <ArrowRight className="w-6 h-6 text-slate-500" />
              </div>

              {/* Central Engine */}
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center">
                <Shield className="w-6 h-6 text-sentry-cyan mx-auto mb-2" />
                <div className="text-xs font-mono text-white font-bold">TabPFN-3.5</div>
                <div className="text-xs font-mono text-white font-bold">Sentry Engine</div>
                <div className="text-[9px] text-slate-400 mt-1">14.8ms Bayesian Prior</div>
              </div>

              {/* Arrow */}
              <div className="flex items-center justify-center">
                <ArrowRight className="w-6 h-6 text-slate-500" />
              </div>

              {/* Output Nodes */}
              <div className="space-y-2">
                <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
                  <div className="text-[10px] font-mono text-sentry-emerald font-bold">SQLite WAL</div>
                  <div className="text-[9px] text-slate-400">agentry_audit.db</div>
                </div>
                <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-center">
                  <div className="text-[10px] font-mono text-amber-400 font-bold">Frontend Dashboard</div>
                  <div className="text-[9px] text-slate-400">This view (polls /v1/mcp/usage)</div>
                </div>
                <div className="p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-center">
                  <div className="text-[10px] font-mono text-sentry-red font-bold">HITL Queue</div>
                  <div className="text-[9px] text-slate-400">Operator approval</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Source cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {['mcp', 'rest', 'proxy', 'frontend'].map((srcKey) => {
            const metrics = allSources[srcKey];
            const meta = SOURCE_META[srcKey] || { label: srcKey, icon: <Cpu className="w-4 h-4" />, color: 'text-slate-400', desc: '' };
            const isSelected = selectedSource === srcKey;
            const hasData = !!metrics;
            const steps = metrics?.total_steps || 0;
            const sessions = metrics?.unique_sessions || 0;
            const kills = metrics?.interventions.KILL || 0;
            const reroutes = metrics?.interventions.REROUTE || 0;
            const pauses = metrics?.interventions.PAUSE || 0;
            const passes = metrics?.interventions.PASS || 0;

            return (
              <button
                key={srcKey}
                onClick={() => setSelectedSource(isSelected ? null : srcKey)}
                className={`glass-card rounded-2xl p-5 border transition-all text-left
                  ${isSelected
                    ? 'border-sentry-violet/50 bg-sentry-violet/5 scale-[1.02]'
                    : hasData
                    ? 'border-white/10 hover:border-white/20 hover:scale-[1.01]'
                    : 'border-white/5 opacity-50'
                  }`}
              >
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center ${meta.color}`}>
                    {meta.icon}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-sm">{meta.label}</h3>
                    <span className="text-[10px] font-mono text-slate-400">{meta.desc}</span>
                  </div>
                </div>

                {hasData ? (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Steps</span>
                      <span className="text-white font-bold">{steps.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Sessions</span>
                      <span className="text-white font-bold">{sessions}</span>
                    </div>
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Cost Saved</span>
                      <span className="text-sentry-emerald font-bold">${(metrics?.cost_saved_usd || 0).toFixed(2)}</span>
                    </div>
                    {/* Mini intervention bar */}
                    <div className="pt-2 border-t border-white/5">
                      <div className="flex gap-1 h-2 rounded-full overflow-hidden bg-black/40">
                        {passes > 0 && <div className="bg-sentry-emerald" style={{ width: `${(passes / steps) * 100}%` }} />}
                        {kills > 0 && <div className="bg-sentry-red" style={{ width: `${(kills / steps) * 100}%` }} />}
                        {reroutes > 0 && <div className="bg-amber-400" style={{ width: `${(reroutes / steps) * 100}%` }} />}
                        {pauses > 0 && <div className="bg-sentry-violet" style={{ width: `${(pauses / steps) * 100}%` }} />}
                      </div>
                      <div className="flex justify-between text-[9px] font-mono text-slate-500 mt-1">
                        <span>{passes} pass</span>
                        <span>{kills} kill</span>
                        <span>{reroutes} reroute</span>
                        <span>{pauses} pause</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-xs font-mono text-slate-500 py-4 text-center">
                    No events recorded yet
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* ================================================================= */}
      {/* SELECTED SOURCE EVENT LOG                                          */}
      {/* ================================================================= */}
      {selectedSource && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 pb-3 border-b border-white/10">
            <div className="w-8 h-8 rounded-xl bg-sentry-cyan/15 text-sentry-cyan border border-sentry-cyan/30 flex items-center justify-center font-mono font-bold text-sm shrink-0">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">
                Recent Events: {SOURCE_META[selectedSource]?.label || selectedSource}
              </h2>
              <p className="text-xs text-slate-400">
                Last 8 audit decisions from this integration source, ordered by most recent.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {sourceEvents.length > 0 ? (
              sourceEvents.map((evt) => {
                const isKill = evt.action === 'KILL';
                const isPause = evt.action === 'PAUSE';
                const isReroute = evt.action === 'REROUTE';

                const cardBorder = isKill
                  ? 'border-red-500/40 bg-red-950/10'
                  : isPause
                  ? 'border-amber-500/40 bg-amber-950/10'
                  : isReroute
                  ? 'border-violet-500/30 bg-violet-950/10'
                  : 'border-white/10';

                const badgeClass = isKill
                  ? 'bg-red-500/20 text-sentry-red border-red-500/40'
                  : isPause
                  ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                  : isReroute
                  ? 'bg-violet-500/20 text-sentry-violet border-violet-500/40'
                  : 'bg-emerald-500/15 text-sentry-emerald border-emerald-500/30';

                return (
                  <div key={evt.id} className={`glass-card rounded-2xl p-4 border ${cardBorder} transition-all flex flex-col justify-between space-y-3`}>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                            {isKill ? <Terminal className="w-3.5 h-3.5 text-red-400" /> : <FileCode className="w-3.5 h-3.5 text-emerald-400" />}
                          </div>
                          <div>
                            <h3 className="font-bold text-white text-xs truncate max-w-[120px]">{evt.session_id}</h3>
                            <span className="text-[9px] font-mono text-slate-400">Step #{evt.step_index}</span>
                          </div>
                        </div>
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-mono font-bold border ${badgeClass}`}>
                          {evt.action}
                        </span>
                      </div>
                      <div className="p-2 rounded-lg bg-black/60 border border-white/5 font-mono text-[10px] text-slate-300 space-y-0.5">
                        <div className="text-sentry-cyan font-semibold truncate">{evt.sentry_provider}</div>
                        <div className="text-slate-400 line-clamp-2 leading-relaxed">{evt.reason}</div>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-white/10 text-[10px] font-mono flex items-center justify-between text-slate-400">
                      <span>Risk: <strong className={isKill ? 'text-sentry-red' : 'text-sentry-emerald'}>{(evt.failure_probability * 100).toFixed(1)}%</strong></span>
                      <span className="text-white font-semibold">
                        {evt.estimated_cost_saved_usd > 0 ? `$${evt.estimated_cost_saved_usd.toFixed(2)} saved` : `$${evt.projected_final_cost_usd.toFixed(2)}`}
                      </span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="col-span-4 p-8 glass-card rounded-2xl text-center font-mono text-xs text-slate-400">
                No events recorded from {SOURCE_META[selectedSource]?.label || selectedSource} yet.
                {selectedSource === 'mcp' && (
                  <span className="block mt-2 text-sentry-violet">
                    Run <code className="bg-white/5 px-1.5 py-0.5 rounded">python run.py mcp</code> and use tools from Cursor/Claude Desktop to see events appear here.
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ================================================================= */}
      {/* MCP CONNECTION GUIDE                                               */}
      {/* ================================================================= */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-white/10">
          <div className="w-8 h-8 rounded-xl bg-sentry-emerald/15 text-sentry-emerald border border-sentry-emerald/30 flex items-center justify-center font-mono font-bold text-sm shrink-0">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">
              How MCP Events Flow to This Dashboard
            </h2>
            <p className="text-xs text-slate-400">
              Every MCP tool call from Cursor or Claude Desktop is audited, persisted to SQLite, and appears here within 5 seconds.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Step 1 */}
          <div className="glass-card rounded-2xl p-5 border border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-sentry-cyan/10 border border-sentry-cyan/20 flex items-center justify-center text-sentry-cyan font-mono font-bold text-xs">1</div>
              <h3 className="text-sm font-bold text-white">Start MCP Server</h3>
            </div>
            <div className="p-3 rounded-xl bg-black/60 border border-white/5 font-mono text-xs text-sentry-cyan mb-3">
              <div className="text-[10px] text-slate-400 mb-1"># Terminal 1: MCP Server (stdio)</div>
              <div>python run.py mcp</div>
              <div className="text-[10px] text-slate-400 mt-2 mb-1"># Terminal 2: REST Daemon (port 8000)</div>
              <div>python run.py serve --port 8000</div>
            </div>
            <p className="text-[11px] text-slate-400">
              The MCP server and REST daemon share the same SQLite WAL database. Events from MCP are tagged with <code className="text-sentry-violet">source=mcp</code>.
            </p>
          </div>

          {/* Step 2 */}
          <div className="glass-card rounded-2xl p-5 border border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-sentry-emerald/10 border border-sentry-emerald/20 flex items-center justify-center text-sentry-emerald font-mono font-bold text-xs">2</div>
              <h3 className="text-sm font-bold text-white">Agent Uses MCP Tools</h3>
            </div>
            <div className="p-3 rounded-xl bg-black/60 border border-white/5 font-mono text-xs text-slate-300 mb-3 space-y-1">
              <div className="text-[10px] text-slate-400">Claude/Cursor invokes:</div>
              <div className="text-sentry-violet">agentry_audit_step</div>
              <div className="text-sentry-violet">agentry_evaluate_blast_radius</div>
              <div className="text-sentry-violet">agentry_redact_secrets</div>
              <div className="text-sentry-violet">agentry_check_swarm_deadlock</div>
            </div>
            <p className="text-[11px] text-slate-400">
              Each tool call is processed by TabPFN-3.5 and the decision is persisted to the shared audit database.
            </p>
          </div>

          {/* Step 3 */}
          <div className="glass-card rounded-2xl p-5 border border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-mono font-bold text-xs">3</div>
              <h3 className="text-sm font-bold text-white">Events Appear Here</h3>
            </div>
            <div className="p-3 rounded-xl bg-black/60 border border-white/5 font-mono text-xs text-slate-300 mb-3 space-y-1">
              <div className="text-[10px] text-slate-400">This dashboard polls every 5s:</div>
              <div className="text-amber-400">GET /v1/mcp/usage</div>
              <div className="text-amber-400">GET /v1/events/mcp?limit=10</div>
            </div>
            <p className="text-[11px] text-slate-400">
              KPIs update automatically. Click source cards above to drill into event logs. HITL escalations surface in Mission Control.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
};
