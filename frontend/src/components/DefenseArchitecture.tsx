import React from 'react';
import { Layers } from 'lucide-react';

export const DefenseArchitecture: React.FC = () => {
  return (
    <section className="py-20 px-4 lg:px-8 border-y border-white/10 bg-surface-1/30">
      <div className="max-w-6xl mx-auto">
        
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sentry-emerald/10 border border-sentry-emerald/30 text-sentry-emerald text-xs font-mono font-medium mb-3">
            <Layers className="w-3.5 h-3.5" />
            <span>DEFENSE-IN-DEPTH</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-3">
            The 3-Layer Defense-in-Depth Architecture
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
            Agentry combines deterministic sub-millisecond filtering with Prior Labs tabular Bayesian inference and autonomic self-healing.
          </p>
        </div>

        <div className="space-y-4">
          
          {/* Layer 1 */}
          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-sentry-cyan hover:bg-surface-2/60 transition-all">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-sentry-cyan/10 border border-sentry-cyan/30 flex items-center justify-center font-mono text-sentry-cyan font-bold text-lg">
                  L1
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">In-Flight Pre-Execution Interception</h3>
                  <p className="text-xs text-slate-300">Deterministic semantic sandbox & data loss prevention executed before tool invocation.</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 text-[11px] font-mono">
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-sentry-cyan">Semantic Blast Radius</span>
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-emerald-300">In-Flight Secret Redaction</span>
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-violet-300">Swarm Deadlock Watchdog</span>
              </div>
            </div>
          </div>

          {/* Layer 2 */}
          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-sentry-emerald hover:bg-surface-2/60 transition-all glow-emerald">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center font-mono text-sentry-emerald font-bold text-lg">
                  L2
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-white">Foundation Model Tabular Sentry</h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald font-bold">CORE SECRET WEAPON</span>
                  </div>
                  <p className="text-xs text-slate-300">Prior Labs TabPFN-3.5 foundation model evaluating 16 multivariate telemetry metrics in 14.8ms.</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 text-[11px] font-mono">
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-sentry-emerald">Bayesian In-Context Prior</span>
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-sentry-cyan">Thinking Mode (10k tokens)</span>
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-amber-300">Multiclass Failure Class</span>
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-blue-300">Runaway Cost Regression</span>
              </div>
            </div>
          </div>

          {/* Layer 3 */}
          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-sentry-violet hover:bg-surface-2/60 transition-all">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center font-mono text-sentry-violet font-bold text-lg">
                  L3
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Closed-Loop Autonomic Self-Healing</h3>
                  <p className="text-xs text-slate-300">Physical filesystem rollback, prompt trajectory pruning, and budget autopilot governance.</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 text-[11px] font-mono">
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-violet-300">Differential Disk Checkpoint</span>
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-sentry-cyan">Inflection Point t* Pruning</span>
                <span className="px-2.5 py-1 rounded bg-surface-2 border border-white/10 text-emerald-300">24h Quota Governor</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};
