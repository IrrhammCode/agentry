import React, { useState } from 'react';
import { 
  ShieldAlert, 
  Lock, 
  RefreshCw, 
  ArrowRight, 
  CornerDownLeft, 
  Flame, 
  Check, 
  AlertOctagon 
} from 'lucide-react';

export const ActiveDefense: React.FC = () => {
  const [rawText, setRawText] = useState<string>(
    'Connect to AWS RDS using key: AKIAIOSFODNN7EXAMPLE and OpenAI token sk-proj-98214abcdef993214 to sync database postgres://admin:superSecret123@db.prod.internal:5432/main'
  );
  const [maskedText, setMaskedText] = useState<string>(
    'Connect to AWS RDS using key: [REDACTED_AWS_KEY:AKIA...MPLE] and OpenAI token [REDACTED_OPENAI_KEY:sk-p...3214] to sync database [REDACTED_DB_URI:postgres://[REDACTED]@.../main]'
  );

  const [deadlockBroken, setDeadlockBroken] = useState<boolean>(false);
  const [customCmd, setCustomCmd] = useState<string>('rm -rf / --no-preserve-root');
  const [blastScore, setBlastScore] = useState<number>(100);

  const handleMask = () => {
    const masked = rawText
      .replace(/AKIA[0-9A-Z]{16}/g, '[REDACTED_AWS_KEY:AKIA...MPLE]')
      .replace(/sk-proj-[a-zA-Z0-9_-]+/g, '[REDACTED_OPENAI_KEY:sk-p...3214]')
      .replace(/postgres:\/\/[^@]+@/g, 'postgres://[REDACTED_AUTH]@');
    setMaskedText(masked);
  };

  const handleEvalBlast = (cmd: string) => {
    setCustomCmd(cmd);
    if (cmd.includes('rm -rf') || cmd.includes('DROP') || cmd.includes('mkfs')) {
      setBlastScore(98);
    } else if (cmd.includes('chmod') || cmd.includes('chown') || cmd.includes('export')) {
      setBlastScore(65);
    } else if (cmd.includes('pytest') || cmd.includes('python')) {
      setBlastScore(20);
    } else {
      setBlastScore(5);
    }
  };

  return (
    <div className="flex-grow max-w-7xl mx-auto w-full px-4 lg:px-8 py-8 space-y-8">
      
      <div>
        <h2 className="text-2xl font-display font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-sentry-red" />
          <span className="animate-text-shimmer">Active Defense, Blast Radius & In-Flight DLP Inspector</span>
        </h2>
        <p className="text-xs text-slate-400 font-mono">
          Pre-Execution Interception Pillars • Zero Cloud Leakage • Swarm Deadlock Prevention
        </p>
      </div>

      {/* DLP Inspector Split Screen */}
      <div className="glass-card rounded-2xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <Lock className="w-4 h-4 text-sentry-violet" />
              In-Flight DLP Credential Sanitizer
            </h3>
            <p className="text-xs text-slate-400">Zero-leakage secret masking before requests reach LLM or external logs.</p>
          </div>
          <button 
            onClick={handleMask}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-sentry-violet/20 hover:bg-violet-500/30 text-sentry-violet border border-violet-500/30 text-xs font-mono font-bold transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Re-run Sanitizer</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="text-xs font-mono text-slate-400 mb-2 block">RAW INBOUND PROMPT (EXPOSED TOKENS)</span>
            <textarea 
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              rows={6} 
              className="w-full bg-void rounded-xl p-3 font-mono text-xs text-red-300 border border-red-500/30 resize-none focus:outline-none focus:border-red-400"
            />
          </div>

          <div>
            <span className="text-xs font-mono text-slate-400 mb-2 block">SANITIZED OUTBOUND PROMPT (AGENTRY DLP MASKED)</span>
            <textarea 
              value={maskedText}
              readOnly 
              rows={6} 
              className="w-full bg-void rounded-xl p-3 font-mono text-xs text-sentry-emerald border border-emerald-500/30 resize-none focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Swarm Deadlock Visualizer */}
      <div className="glass-card rounded-2xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-sentry-cyan" />
              Multi-Agent Swarm Ping-Pong & Deadlock Watchdog
            </h3>
            <p className="text-xs text-slate-400">Detects cyclical delegation ping-pongs across agent swarms (A ⇆ B ⇆ A).</p>
          </div>
          <button 
            onClick={() => setDeadlockBroken(!deadlockBroken)}
            className="px-3 py-1.5 rounded-lg bg-surface-2 hover:bg-surface-3 text-xs font-mono text-slate-300 border border-white/10"
          >
            {deadlockBroken ? 'Simulate Deadlock' : 'Test Loop Break'}
          </button>
        </div>

        <div className="p-6 rounded-xl bg-void/80 border border-white/5 font-mono text-xs">
          <div className="flex items-center justify-center gap-6 flex-wrap">
            <div className="p-4 rounded-xl bg-surface-2 border border-sentry-cyan text-center">
              <div className="text-sentry-cyan font-bold">CoderAgent-01</div>
              <div className="text-[10px] text-slate-400">Delegates Review</div>
            </div>
            
            <ArrowRight className={`w-6 h-6 ${deadlockBroken ? 'text-emerald-400' : 'text-red-500 animate-pulse'}`} />
            
            <div className="p-4 rounded-xl bg-surface-2 border border-amber-400 text-center">
              <div className="text-amber-400 font-bold">ReviewerAgent-02</div>
              <div className="text-[10px] text-slate-400">{deadlockBroken ? 'Finalizes Task' : 'Re-Delegates Back'}</div>
            </div>

            {!deadlockBroken ? (
              <>
                <CornerDownLeft className="w-6 h-6 text-red-500 animate-pulse" />
                <div className="p-3 rounded-lg bg-red-950/60 border border-red-500 text-red-300 text-center font-bold text-xs flex flex-col items-center gap-1">
                  <span className="flex items-center gap-1.5"><AlertOctagon className="w-4 h-4 text-red-400" /> CYCLE DETECTED (Length: 2)</span>
                  <span className="text-[11px] font-normal text-slate-300">Intervention: Force Terminal Finalizer</span>
                </div>
              </>
            ) : (
              <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-500 text-emerald-300 text-center font-bold text-xs flex flex-col items-center gap-1">
                <span className="flex items-center gap-1.5"><Check className="w-4 h-4 text-sentry-emerald" /> LOOP RESOLVED</span>
                <span className="text-[11px] font-normal text-slate-300">Directed graph resolved with terminal artifact.</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Semantic Blast Radius Sandbox */}
      <div className="glass-card rounded-2xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <Flame className="w-4 h-4 text-sentry-red" />
              Semantic Blast Radius Sandbox
            </h3>
            <p className="text-xs text-slate-400">Evaluates shell command destructive potential before execution.</p>
          </div>
          <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${
            blastScore > 70 
              ? 'bg-red-500/20 text-sentry-red border-red-500/30' 
              : blastScore > 30 
              ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
              : 'bg-emerald-500/20 text-sentry-emerald border-emerald-500/30'
          }`}>
            Danger Score: {blastScore} / 100
          </span>
        </div>

        <div className="space-y-4">
          <input
            type="text"
            value={customCmd}
            onChange={(e) => handleEvalBlast(e.target.value)}
            className="w-full bg-void rounded-xl p-3 font-mono text-xs text-sentry-cyan border border-white/10 focus:border-sentry-cyan focus:outline-none"
            placeholder="Type command e.g. rm -rf /, DROP DATABASE, chmod 777..."
          />

          <div className="flex items-center gap-3">
            <button 
              onClick={() => handleEvalBlast('rm -rf / --no-preserve-root')}
              className="px-2.5 py-1 rounded bg-surface-2 text-[11px] font-mono text-slate-300 hover:text-white"
            >
              rm -rf /
            </button>
            <button 
              onClick={() => handleEvalBlast('DROP DATABASE production CASCADE;')}
              className="px-2.5 py-1 rounded bg-surface-2 text-[11px] font-mono text-slate-300 hover:text-white"
            >
              DROP DATABASE
            </button>
            <button 
              onClick={() => handleEvalBlast('pytest tests/test_auth.py')}
              className="px-2.5 py-1 rounded bg-surface-2 text-[11px] font-mono text-slate-300 hover:text-white"
            >
              pytest tests/
            </button>
          </div>
        </div>
      </div>

    </div>
  );
};
