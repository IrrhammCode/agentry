import React from 'react';
import { Flame, Repeat, Bomb, EyeOff } from 'lucide-react';

export const FatalTraps: React.FC = () => {
  return (
    <section className="py-20 px-4 lg:px-8 max-w-6xl mx-auto">
      <div className="text-center mb-14">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-sentry-red text-xs font-mono font-medium mb-3">
          <Flame className="w-3.5 h-3.5" />
          <span>WHY STATIC RULES FAIL</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-3">
          The 3 Fatal Traps of Autonomous Agent Fleets
        </h2>
        <p className="text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
          Autonomous agents operate in high-dimensional codebases and APIs. When things go wrong, they spiral catastrophically without a foundation sentry.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Trap 1 */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-amber-500/40 transition-all flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-5">
              <Repeat className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">The $1,000 Infinite Retry Spiral</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              An agent crashes on a test, changes a comment, and runs the same bash test 40 times in a row. Context balloons to 128k tokens, silently burning hundreds of dollars in API credit before morning.
            </p>
          </div>
          <div className="pt-4 border-t border-white/10 font-mono text-xs text-sentry-emerald">
            🛡️ TabPFN detects repetitive multivariate step entropy and halts at step 5.
          </div>
        </div>

        {/* Trap 2 */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-red-500/40 transition-all flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-sentry-red mb-5">
              <Bomb className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Irreversible Blast Radius</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Given a terminal, a hallucinating agent runs cleanup scripts that delete <code className="text-red-400 font-mono">/var</code>, drop database tables, or overwrite production configs with dummy mocks.
            </p>
          </div>
          <div className="pt-4 border-t border-white/10 font-mono text-xs text-sentry-cyan">
            🛡️ Agentry Layer 1 checks blast radius in-flight before the OS executes the call.
          </div>
        </div>

        {/* Trap 3 */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-violet-500/40 transition-all flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-sentry-violet mb-5">
              <EyeOff className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Silent Credential Leaks</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Using commercial cloud LLMs to supervise your agents sends your source code, private SSH keys, and database passwords directly to external third-party servers.
            </p>
          </div>
          <div className="pt-4 border-t border-white/10 font-mono text-xs text-sentry-violet">
            🛡️ 100% Zero-Prompt Transmission: TabPFN runs purely on numeric tabular features.
          </div>
        </div>

      </div>
    </section>
  );
};
