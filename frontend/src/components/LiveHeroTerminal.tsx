import React, { useState, useEffect } from 'react';
import { 
  Terminal, 
  Cpu, 
  ShieldAlert, 
  Sparkles, 
  Zap, 
  OctagonAlert, 
  Play, 
  Pause, 
  RotateCcw,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

interface TelemetryStep {
  step: number;
  time: string;
  tool: string;
  action: string;
  status: 'nominal' | 'warn' | 'reroute' | 'kill';
  statusText: string;
  prob: string;
  extra?: string;
}

const STREAM_STEPS: TelemetryStep[] = [
  {
    step: 1,
    time: 't=1',
    tool: 'read_file("auth/tokens.py")',
    action: 'Tool Execution Request',
    status: 'nominal',
    statusText: 'NOMINAL • PASS',
    prob: 'P_fail = 0.03',
  },
  {
    step: 2,
    time: 't=2',
    tool: 'replace_code("tokens.py:42", "new_logic")',
    action: 'Code Mutation',
    status: 'nominal',
    statusText: 'NOMINAL • PASS',
    prob: 'P_fail = 0.07',
  },
  {
    step: 3,
    time: 't=3',
    tool: 'run_command("pytest tests/test_auth.py")',
    action: 'Test Execution',
    status: 'warn',
    statusText: 'ANOMALY_RUNAWAY • WARN',
    prob: 'P_fail = 0.68',
    extra: 'Exit: 1 Crash Detected',
  },
  {
    step: 4,
    time: 't=4',
    tool: 'run_command("pytest tests/test_auth.py")',
    action: 'Retry Without Modification',
    status: 'reroute',
    statusText: 'CRITICAL_LOOP • REROUTE',
    prob: 'P_fail = 0.94',
    extra: 'Repeated Error Loop streak=2',
  },
  {
    step: 5,
    time: 't=5',
    tool: 'run_command("rm -rf /var/cache/*")',
    action: 'Unconstrained Root Mutation',
    status: 'kill',
    statusText: 'CIRCUIT-BREAKER KILL',
    prob: 'P_fail = 0.998',
    extra: 'BLAST RADIUS VIOLATION (14.8ms)',
  },
];

export const LiveHeroTerminal: React.FC = () => {
  const [visibleCount, setVisibleCount] = useState<number>(2);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [showHealer, setShowHealer] = useState<boolean>(false);

  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setVisibleCount((prev) => {
        if (prev < STREAM_STEPS.length) {
          if (prev + 1 === STREAM_STEPS.length) {
            setTimeout(() => setShowHealer(true), 600);
          }
          return prev + 1;
        } else {
          // Loop restart after pause
          setShowHealer(false);
          return 1;
        }
      });
    }, 1800);

    return () => clearInterval(interval);
  }, [isPlaying]);

  const handleRestart = () => {
    setVisibleCount(1);
    setShowHealer(false);
    setIsPlaying(true);
  };

  return (
    <div className="mt-14 max-w-4xl mx-auto glass-card rounded-2xl overflow-hidden border border-white/15 shadow-2xl relative text-left transition-all duration-300 hover:border-sentry-cyan/40">
      
      {/* Top Laser Scanning Beam */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-sentry-cyan to-transparent animate-beam-sweep z-30" />

      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-surface-1/95 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
          <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          <span className="ml-2 font-mono text-xs text-slate-300 flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-sentry-cyan" />
            LIVE RADAR: <span className="text-white">swe_bench_fix_auth_regress.jsonl</span>
          </span>
        </div>

        <div className="flex items-center gap-2 sm:gap-3 font-mono text-xs">
          <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald border border-emerald-500/30 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            <span className="hidden sm:inline">AGENT:</span> CoderAgent-01
          </span>

          {/* Controls */}
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            title={isPlaying ? "Pause Stream" : "Play Stream"}
            className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-sentry-emerald" />}
          </button>
          <button 
            onClick={handleRestart}
            title="Restart Stream"
            className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Telemetry Body */}
      <div className="p-5 font-mono text-xs space-y-3 bg-void/90 min-h-[260px] relative">
        {STREAM_STEPS.slice(0, visibleCount).map((item, idx) => {
          const isLatest = idx === visibleCount - 1;
          return (
            <div 
              key={item.step}
              className={`flex items-start justify-between flex-wrap gap-2 p-2 rounded-lg transition-all duration-300 animate-fade-in ${
                item.status === 'kill' 
                  ? 'bg-red-950/40 border border-red-500/40 glow-red' 
                  : item.status === 'reroute'
                  ? 'bg-amber-950/30 border border-amber-500/30'
                  : 'hover:bg-white/5 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-2 text-slate-300">
                <span className="text-sentry-cyan font-bold">{item.time}</span>
                <span className="text-slate-400">tool:</span>
                <span className={item.status === 'kill' ? 'text-red-300 font-bold' : 'text-slate-200'}>
                  {item.tool}
                </span>
                {item.extra && (
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                    item.status === 'kill' ? 'bg-red-500/30 text-red-200' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    [{item.extra}]
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-500">{item.prob}</span>
                {item.status === 'nominal' && (
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>PASS</span>
                  </span>
                )}
                {item.status === 'warn' && (
                  <span className="text-amber-400 font-bold flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>WARN</span>
                  </span>
                )}
                {item.status === 'reroute' && (
                  <span className="text-sentry-red font-bold flex items-center gap-1">
                    <OctagonAlert className="w-3.5 h-3.5" />
                    <span>REROUTE</span>
                  </span>
                )}
                {item.status === 'kill' && (
                  <span className="text-white bg-red-600 px-2 py-0.5 rounded text-[11px] font-bold flex items-center gap-1 shadow-lg animate-pulse">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>KILL</span>
                  </span>
                )}
              </div>
            </div>
          );
        })}

        {/* Live Cursor Indicator */}
        <div className="flex items-center gap-2 text-slate-500 text-[11px] pt-1">
          <span className="text-sentry-cyan">agentry-sentry</span>
          <span>&gt;</span>
          <span className="text-sentry-emerald animate-blink font-bold">█</span>
          {visibleCount < STREAM_STEPS.length && (
            <span className="text-slate-500 text-[10px] italic">
              evaluating next step with TabPFN in-context prior...
            </span>
          )}
        </div>
      </div>

      {/* Autonomic Healer Ribbon */}
      {showHealer ? (
        <div className="px-5 py-3 bg-gradient-to-r from-emerald-950 via-surface-1 to-cyan-950 border-t border-emerald-500/40 flex items-center justify-between flex-wrap gap-2 text-xs animate-fade-in shadow-inner">
          <div className="flex items-center gap-2 text-sentry-emerald font-semibold">
            <Sparkles className="w-4 h-4 animate-spin" />
            <span>Autonomic Healer Engaged:</span>
            <span className="text-slate-200 font-normal">
              Physical snapshot restored to <strong className="text-white font-mono">t=2</strong> • Injected counterfactual steering directive
            </span>
          </div>
          <div className="font-mono text-[11px] text-sentry-cyan font-bold flex items-center gap-1.5 bg-void/60 px-2.5 py-1 rounded-lg border border-cyan-500/20">
            <Zap className="w-3.5 h-3.5 text-sentry-cyan animate-pulse" />
            <span>Rollback Time: 12ms • Capital Saved: $1.42</span>
          </div>
        </div>
      ) : (
        <div className="px-5 py-2.5 bg-surface-1/90 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>TabPFN-3.5 Multiclass Foundation Model</span>
          <span>Autonomous Circuit-Breaker: ARMED</span>
        </div>
      )}

    </div>
  );
};
