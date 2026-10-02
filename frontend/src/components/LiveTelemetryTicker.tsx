import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  ShieldCheck, 
  Lock, 
  Cpu, 
  History, 
  Coins, 
  Server, 
  CheckCircle2, 
  Activity,
  Bot
} from 'lucide-react';
import { AgentryApi, FleetMetrics } from '../services/api.ts';

const BASE_ITEMS = [
  { icon: <Cpu className="w-3.5 h-3.5 text-sentry-emerald" />, text: 'Prior Labs TabPFN-3.5 Foundation Model' },
  { icon: <Zap className="w-3.5 h-3.5 text-sentry-cyan" />, text: '14.8ms Sub-20ms Bayesian In-Context Prior' },
  { icon: <Lock className="w-3.5 h-3.5 text-sentry-violet" />, text: '100% Zero-Prompt Transmission Privacy' },
  { icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />, text: '79/79 SWE-bench Test Suites Passed' },
  { icon: <ShieldCheck className="w-3.5 h-3.5 text-sentry-red" />, text: 'Deterministic In-Flight Blast Radius Shield' },
  { icon: <History className="w-3.5 h-3.5 text-amber-400" />, text: 'Closed-Loop Autonomic Disk Snapshot Rewind' },
  { icon: <Coins className="w-3.5 h-3.5 text-sentry-cyan" />, text: 'Fleet Token Budget Autopilot' },
  { icon: <Server className="w-3.5 h-3.5 text-slate-300" />, text: 'Drop-In OpenAI Proxy & MCP Server' },
];

export const LiveTelemetryTicker: React.FC = () => {
  const [metrics, setMetrics] = useState<FleetMetrics | null>(null);

  useEffect(() => {
    AgentryApi.getFleetMetrics()
      .then(setMetrics)
      .catch((err) => console.debug('Ticker metrics offline', err));
  }, []);

  const liveItems = [
    ...(metrics ? [
      { icon: <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />, text: `${metrics.total_audited_steps.toLocaleString()} Live Fleet Steps Audited` },
      { icon: <Bot className="w-3.5 h-3.5 text-sentry-cyan" />, text: `${metrics.unique_sessions} Monitored Agent Fleets` },
      { icon: <Coins className="w-3.5 h-3.5 text-sentry-emerald" />, text: `$${metrics.total_cost_saved_usd.toFixed(2)} USD Salvaged from Runaways` },
    ] : []),
    ...BASE_ITEMS
  ];

  return (
    <div className="w-full overflow-hidden border-y border-white/10 bg-black py-3 relative select-none">
      
      {/* Ambient edge gradients for smooth fade */}
      <div className="absolute top-0 bottom-0 left-0 w-24 bg-gradient-to-r from-black to-transparent z-10 pointer-events-none" />
      <div className="absolute top-0 bottom-0 right-0 w-24 bg-gradient-to-l from-black to-transparent z-10 pointer-events-none" />

      <div className="animate-ticker flex items-center gap-8">
        
        {/* First Loop */}
        {liveItems.map((item, idx) => (
          <div 
            key={`a-${idx}`} 
            className="flex items-center gap-2 text-xs font-mono text-slate-300 shrink-0 px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:border-white/20 transition-colors"
          >
            {item.icon}
            <span>{item.text}</span>
          </div>
        ))}

        {/* Duplicate Loop for Seamless Infinite Scroll */}
        {liveItems.map((item, idx) => (
          <div 
            key={`b-${idx}`} 
            className="flex items-center gap-2 text-xs font-mono text-slate-300 shrink-0 px-3 py-1 rounded-full bg-white/5 border border-white/5 hover:border-white/20 transition-colors"
          >
            {item.icon}
            <span>{item.text}</span>
          </div>
        ))}

      </div>
    </div>
  );
};
