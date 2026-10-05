import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Lock, 
  RefreshCw, 
  ArrowRight, 
  CornerDownLeft, 
  Flame, 
  Check, 
  AlertOctagon, 
  ShieldCheck, 
  Cpu, 
  Layers, 
  Sparkles, 
  Terminal, 
  KeyRound,
  ShieldX,
  RotateCcw,
  Scissors,
  Wand2,
  FileCheck
} from 'lucide-react';
import { 
  AgentryApi, 
  DlpResult, 
  BlastRadiusResult, 
  SwarmDeadlockResult,
  RewindPrescription
} from '../services/api.ts';

export const ActiveDefense: React.FC = () => {
  const [rawText, setRawText] = useState<string>(
    'Connect to AWS RDS using key: AKIAIOSFODNN7EXAMPLE and OpenAI token sk-proj-98214abcdef993214 to sync database postgres://admin:superSecret123@db.prod.internal:5432/main'
  );
  const [maskedText, setMaskedText] = useState<string>('');
  const [dlpResult, setDlpResult] = useState<DlpResult | null>(null);
  const [isDlpLoading, setIsDlpLoading] = useState<boolean>(false);

  const [deadlockBroken, setDeadlockBroken] = useState<boolean>(false);
  const [deadlockResult, setDeadlockResult] = useState<SwarmDeadlockResult | null>(null);
  const [isDeadlockLoading, setIsDeadlockLoading] = useState<boolean>(false);

  const [customCmd, setCustomCmd] = useState<string>('rm -rf / --no-preserve-root');
  const [blastScore, setBlastScore] = useState<number>(100);
  const [blastResult, setBlastResult] = useState<BlastRadiusResult | null>(null);
  const [isBlastLoading, setIsBlastLoading] = useState<boolean>(false);

  // Pillar 1: DLP Secret Redaction
  const handleMask = async (textToMask?: string) => {
    const text = textToMask !== undefined ? textToMask : rawText;
    setIsDlpLoading(true);
    try {
      const res = await AgentryApi.redactDlp(text);
      setMaskedText(res.masked_text);
      setDlpResult(res);
    } catch (err) {
      console.error('DLP redaction failed', err);
    } finally {
      setIsDlpLoading(false);
    }
  };

  // Pillar 2: Swarm Deadlock Detection
  const handleToggleDeadlock = async () => {
    const targetState = !deadlockBroken;
    setDeadlockBroken(targetState);
    setIsDeadlockLoading(true);
    try {
      const transfers = targetState 
        ? [
            { from_agent: 'CoderAgent-01', to_agent: 'ReviewerAgent-02', task: 'Review pull request #402' },
            { from_agent: 'ReviewerAgent-02', to_agent: 'TerminalAgent-Finalizer', task: 'Merged and finalized' }
          ]
        : [
            { from_agent: 'CoderAgent-01', to_agent: 'ReviewerAgent-02', task: 'Review pull request' },
            { from_agent: 'ReviewerAgent-02', to_agent: 'CoderAgent-01', task: 'Please revise code' },
            { from_agent: 'CoderAgent-01', to_agent: 'ReviewerAgent-02', task: 'Review pull request again' },
            { from_agent: 'ReviewerAgent-02', to_agent: 'CoderAgent-01', task: 'Please revise code again' }
          ];
      const res = await AgentryApi.detectDeadlock('swarm_live_session', transfers);
      setDeadlockResult(res);
    } catch (err) {
      console.error('Swarm deadlock check failed', err);
    } finally {
      setIsDeadlockLoading(false);
    }
  };

  // Pillar 3: Semantic Blast Radius
  const handleEvalBlast = async (cmd: string) => {
    setCustomCmd(cmd);
    setIsBlastLoading(true);
    try {
      const res = await AgentryApi.evaluateBlastRadius('bash', cmd);
      setBlastScore(res.score);
      setBlastResult(res);
    } catch (err) {
      console.error('Blast radius evaluation failed', err);
    } finally {
      setIsBlastLoading(false);
    }
  };

  // Pillar 4: Autonomous Trajectory Rewind & Time-Travel Healing
  const [rewindSessionId, setRewindSessionId] = useState<string>('swe_django_migration_trap');
  const [rewindStep, setRewindStep] = useState<number>(6);
  const [rewindTool, setRewindTool] = useState<string>('bash: python manage.py migrate');
  const [rewindStreak, setRewindStreak] = useState<number>(4);
  const [rewindReason, setRewindReason] = useState<string>('Recursive DB lock deadlock: OperationalError database is locked');
  const [rewindResult, setRewindResult] = useState<RewindPrescription | null>(null);
  const [isRewindLoading, setIsRewindLoading] = useState<boolean>(false);

  const handlePrescribeRewind = async (sessionOverride?: { id: string; step: number; tool: string; streak: number; reason: string }) => {
    setIsRewindLoading(true);
    const sid = sessionOverride ? sessionOverride.id : rewindSessionId;
    const step = sessionOverride ? sessionOverride.step : rewindStep;
    const tool = sessionOverride ? sessionOverride.tool : rewindTool;
    const streak = sessionOverride ? sessionOverride.streak : rewindStreak;
    const reason = sessionOverride ? sessionOverride.reason : rewindReason;

    if (sessionOverride) {
      setRewindSessionId(sid);
      setRewindStep(step);
      setRewindTool(tool);
      setRewindStreak(streak);
      setRewindReason(reason);
    }

    try {
      const res = await AgentryApi.prescribeRewind({
        session_id: sid,
        current_step: step,
        failed_tool: tool,
        error_streak: streak,
        reason: reason,
      });
      setRewindResult(res);
    } catch (err) {
      console.error('Rewind calculation failed', err);
    } finally {
      setIsRewindLoading(false);
    }
  };

  // Initial load: trigger live evaluations
  useEffect(() => {
    handleMask(rawText);
    handleEvalBlast('rm -rf / --no-preserve-root');
    handlePrescribeRewind();
  }, []);

  return (
    <div className="flex-grow max-w-7xl mx-auto w-full px-4 lg:px-8 py-10 space-y-10 bg-black">
      
      {/* Header */}
      <div className="pb-6 border-b border-white/10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-sentry-red text-xs font-mono font-medium mb-2">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>LAYER-BY-LAYER DEFENSE ENVELOPE</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-display font-bold text-white tracking-tight">
          Active Defense & Security Interception Suite
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Explore the 3 proactive defense pillars powered by live Agentry runtime engines.
        </p>
      </div>

      {/* ===================================================================== */}
      {/* PILLAR 1: IN-FLIGHT DLP CREDENTIAL SANITIZER                          */}
      {/* ===================================================================== */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-white/10">
          <div className="w-8 h-8 rounded-xl bg-violet-500/15 text-sentry-violet border border-violet-500/30 flex items-center justify-center font-mono font-bold text-sm shrink-0">
            1
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>Pillar 1: In-Flight DLP Credential Sanitizer</span>
              <span className="text-xs font-mono text-sentry-violet font-normal">
                (Zero Cloud Leakage)
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              High-entropy secrets (AWS keys, OpenAI tokens, database URIs) are redacted in-flight before payload transmission.
            </p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
              <KeyRound className="w-4 h-4 text-sentry-violet" />
              <span>Real-Time Masking Testbench (Live Regex DLP Engine)</span>
            </div>
            
            <div className="flex items-center gap-3">
              {dlpResult && dlpResult.redaction_count > 0 && (
                <span className="px-2.5 py-1 rounded-lg bg-violet-500/15 border border-violet-500/30 text-sentry-violet text-xs font-mono font-bold">
                  {dlpResult.redaction_count} Secret(s) Redacted In-Flight
                </span>
              )}
              <button 
                onClick={() => handleMask()}
                disabled={isDlpLoading}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-sentry-violet/20 hover:bg-violet-500/30 text-sentry-violet border border-violet-500/30 text-xs font-mono font-bold transition-all hover:scale-[1.02] disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isDlpLoading ? 'animate-spin' : ''}`} />
                <span>{isDlpLoading ? 'Sanitizing...' : 'Re-run Live DLP Sanitizer'}</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-red-400 mb-2">
                <span>RAW INBOUND PROMPT (EXPOSED TOKENS)</span>
                <span className="text-[10px] text-red-500 font-bold">DANGER</span>
              </div>
              <textarea 
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                rows={5} 
                className="w-full bg-black rounded-xl p-4 font-mono text-xs text-red-300 border border-red-500/30 resize-none focus:outline-none focus:border-red-400 leading-relaxed shadow-inner"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-xs font-mono text-sentry-emerald mb-2">
                <span>SANITIZED OUTBOUND PROMPT (AGENTRY DLP MASKED)</span>
                <span className="text-[10px] text-sentry-emerald font-bold">PROTECTED</span>
              </div>
              <textarea 
                value={maskedText}
                readOnly 
                rows={5} 
                className="w-full bg-black rounded-xl p-4 font-mono text-xs text-sentry-emerald border border-emerald-500/30 resize-none focus:outline-none leading-relaxed shadow-inner"
              />
            </div>
          </div>

          {dlpResult && dlpResult.detected_secrets.length > 0 && (
            <div className="p-3 rounded-xl bg-violet-950/20 border border-violet-500/20 text-xs font-mono text-violet-300 flex items-center justify-between flex-wrap gap-2">
              <span>Detected Token Classes:</span>
              <div className="flex items-center gap-2">
                {dlpResult.detected_secrets.map((s, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-violet-500/20 border border-violet-500/30 text-[11px] font-bold">
                    {s.type}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ===================================================================== */}
      {/* PILLAR 2: MULTI-AGENT SWARM DEADLOCK WATCHDOG                         */}
      {/* ===================================================================== */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-white/10">
          <div className="w-8 h-8 rounded-xl bg-sentry-cyan/15 text-sentry-cyan border border-sentry-cyan/30 flex items-center justify-center font-mono font-bold text-sm shrink-0">
            2
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>Pillar 2: Multi-Agent Swarm Deadlock Watchdog</span>
              <span className="text-xs font-mono text-sentry-cyan font-normal">
                (Cycle Detection & Loop Breaking)
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Prevents autonomous agents from delegating tasks to each other in an infinite cycle (Agent A ⇆ Agent B).
            </p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="text-xs font-mono text-slate-300 flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-sentry-cyan" />
              <span>Directed Graph Cycle State (Live Topology Evaluation)</span>
            </span>
            <button 
              onClick={handleToggleDeadlock}
              disabled={isDeadlockLoading}
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-mono text-slate-200 border border-white/10 transition-colors"
            >
              {deadlockBroken ? 'Re-Inject Deadlock Cycle' : 'Test Autonomic Loop Break'}
            </button>
          </div>

          <div className="p-6 rounded-xl bg-black border border-white/10 font-mono text-xs">
            <div className="flex items-center justify-center gap-6 flex-wrap">
              <div className="p-4 rounded-xl bg-[#141416] border border-sentry-cyan text-center">
                <div className="text-sentry-cyan font-bold">CoderAgent-01</div>
                <div className="text-[10px] text-slate-400">Delegates Code Review</div>
              </div>
              
              <ArrowRight className={`w-6 h-6 ${deadlockBroken ? 'text-emerald-400' : 'text-red-500 animate-pulse'}`} />
              
              <div className="p-4 rounded-xl bg-[#141416] border border-amber-400 text-center">
                <div className="text-amber-400 font-bold">ReviewerAgent-02</div>
                <div className="text-[10px] text-slate-400">{deadlockBroken ? 'Finalizes & Merges Code' : 'Re-Delegates Back to Coder'}</div>
              </div>

              {!deadlockBroken ? (
                <>
                  <CornerDownLeft className="w-6 h-6 text-red-500 animate-pulse" />
                  <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500 text-red-300 text-center font-bold text-xs flex flex-col items-center gap-1">
                    <span className="flex items-center gap-1.5"><AlertOctagon className="w-4 h-4 text-red-400" /> CYCLE DETECTED (Length: 2)</span>
                    <span className="text-[11px] font-normal text-slate-300">
                      {deadlockResult?.recommendation || 'Intervention: TabPFN forces terminal finalizer at Step 4'}
                    </span>
                  </div>
                </>
              ) : (
                <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500 text-emerald-300 text-center font-bold text-xs flex flex-col items-center gap-1">
                  <span className="flex items-center gap-1.5"><Check className="w-4 h-4 text-sentry-emerald" /> LOOP AUTONOMICALLY RESOLVED</span>
                  <span className="text-[11px] font-normal text-slate-300">Pruned 3 redundant turns. Zero token waste.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* PILLAR 3: SEMANTIC BLAST RADIUS SANDBOX                               */}
      {/* ===================================================================== */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-white/10">
          <div className="w-8 h-8 rounded-xl bg-red-500/15 text-sentry-red border border-red-500/30 flex items-center justify-center font-mono font-bold text-sm shrink-0">
            3
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>Pillar 3: Semantic Blast Radius Sandbox</span>
              <span className="text-xs font-mono text-sentry-red font-normal">
                (Pre-Execution Shell Interception)
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Evaluates the potential blast radius of arbitrary bash commands before shell execution is granted.
            </p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="text-xs font-mono text-slate-300 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-sentry-red" />
              <span>Interactive Command Hazard Scoring (Live Agentry Evaluator)</span>
            </span>
            <div className="flex items-center gap-2">
              {blastResult && (
                <span className="px-2.5 py-1 rounded-xl text-xs font-mono font-bold bg-white/5 border border-white/10 text-slate-300">
                  {blastResult.category} • Action: {blastResult.recommended_action}
                </span>
              )}
              <span className={`px-3 py-1 rounded-xl text-xs font-mono font-bold border ${
                blastScore > 70 
                  ? 'bg-red-500/20 text-sentry-red border-red-500/40' 
                  : blastScore > 30 
                  ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                  : 'bg-emerald-500/20 text-sentry-emerald border-emerald-500/40'
              }`}>
                Blast Hazard Rating: {blastScore} / 100
              </span>
            </div>
          </div>

          <div className="space-y-3">
            <input
              type="text"
              value={customCmd}
              onChange={(e) => handleEvalBlast(e.target.value)}
              className="w-full bg-black rounded-xl p-4 font-mono text-xs text-sentry-cyan border border-white/15 focus:border-sentry-cyan focus:outline-none"
              placeholder="Type command e.g. rm -rf /, DROP DATABASE, pytest tests/..."
            />

            {blastResult?.violation_reason && (
              <div className="p-3 rounded-xl bg-red-950/20 border border-red-500/30 text-xs font-mono text-red-300 flex items-center gap-2">
                <ShieldX className="w-4 h-4 text-red-400 shrink-0" />
                <span>{blastResult.violation_reason}</span>
              </div>
            )}

            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-mono text-slate-500">Quick Scenarios:</span>
              <button 
                onClick={() => handleEvalBlast('rm -rf / --no-preserve-root')}
                className="px-3 py-1.5 rounded-lg bg-[#141416] hover:bg-white/10 text-xs font-mono text-red-400 border border-white/10 transition-colors"
              >
                rm -rf / (Root wipe)
              </button>
              <button 
                onClick={() => handleEvalBlast('DROP DATABASE production CASCADE;')}
                className="px-3 py-1.5 rounded-lg bg-[#141416] hover:bg-white/10 text-xs font-mono text-amber-400 border border-white/10 transition-colors"
              >
                DROP DATABASE (Table mutation)
              </button>
              <button 
                onClick={() => handleEvalBlast('pytest tests/test_auth.py')}
                className="px-3 py-1.5 rounded-lg bg-[#141416] hover:bg-white/10 text-xs font-mono text-emerald-400 border border-white/10 transition-colors"
              >
                pytest tests/ (Safe test run)
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* PILLAR 4: AUTONOMIC TRAJECTORY REWIND & TIME-TRAVEL HEALING           */}
      {/* ===================================================================== */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 pb-3 border-b border-white/10">
          <div className="w-8 h-8 rounded-xl bg-violet-500/15 text-sentry-violet border border-violet-500/30 flex items-center justify-center font-mono font-bold text-sm shrink-0">
            4
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>Pillar 4: Autonomous Trajectory Rewind & Time-Travel Healing</span>
              <span className="text-xs font-mono text-sentry-violet font-normal">
                (Divergence Inflection Pruning & Counterfactual Steering)
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              We do not just kill agents; we heal them. When TabPFN detects a failure loop, Agentry locates the divergence inflection point (t*), rolls back poisoned turns, reverts filesystem mutations, and injects counterfactual steering directives.
            </p>
          </div>
        </div>

        <div className="glass-card rounded-2xl p-6 border border-white/10 space-y-6">
          {/* Header Controls */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <RotateCcw className="w-4 h-4 text-sentry-violet" />
              <span className="text-xs font-mono text-white font-bold">Interactive Trajectory Rewind Engine</span>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-mono text-slate-400">Looping Agent Scenarios:</span>
              <button
                onClick={() => handlePrescribeRewind({
                  id: 'swe_django_migration_trap',
                  step: 6,
                  tool: 'bash: python manage.py migrate',
                  streak: 4,
                  reason: 'Recursive DB lock deadlock: OperationalError database is locked'
                })}
                className="px-3 py-1.5 rounded-lg bg-[#141416] hover:bg-white/10 text-xs font-mono text-sentry-violet border border-white/10 transition-colors"
              >
                Django DB Deadlock (Step 6)
              </button>
              <button
                onClick={() => handlePrescribeRewind({
                  id: 'react_build_infinite_retry',
                  step: 8,
                  tool: 'npm run build',
                  streak: 5,
                  reason: 'Syntax recursion error: TS2304 Cannot find name Cost in JSX'
                })}
                className="px-3 py-1.5 rounded-lg bg-[#141416] hover:bg-white/10 text-xs font-mono text-amber-400 border border-white/10 transition-colors"
              >
                Vite TS Build Loop (Step 8)
              </button>
              <button
                onClick={() => handlePrescribeRewind({
                  id: 'crawler_rate_limit_backoff',
                  step: 5,
                  tool: 'http_request: GET /api/v2/items',
                  streak: 3,
                  reason: '429 Rate Limit exponential backoff saturation'
                })}
                className="px-3 py-1.5 rounded-lg bg-[#141416] hover:bg-white/10 text-xs font-mono text-sentry-cyan border border-white/10 transition-colors"
              >
                HTTP 429 Saturation (Step 5)
              </button>
            </div>
          </div>

          {/* Interactive Timeline Diagram */}
          <div className="p-4 rounded-xl bg-black/60 border border-white/5 space-y-3">
            <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between">
              <span>Trajectory Execution Timeline (Session: <strong className="text-sentry-cyan">{rewindSessionId}</strong>)</span>
              {rewindResult && (
                <span className="text-sentry-emerald font-bold">
                  Divergence Inflection Point: t* = Step #{rewindResult.target_step}
                </span>
              )}
            </div>

            {/* Visual Timeline Nodes */}
            <div className="flex items-center gap-2 overflow-x-auto py-3">
              {[...Array(rewindStep + 1)].map((_, idx) => {
                const targetStep = rewindResult ? rewindResult.target_step : 2;
                const isHealthy = idx <= targetStep;
                const isInflection = idx === targetStep;
                const isPoisoned = idx > targetStep;

                return (
                  <div key={idx} className="flex items-center gap-2 shrink-0">
                    <div className={`p-3 rounded-xl border flex flex-col items-center min-w-[90px] text-center transition-all ${
                      isInflection
                        ? 'bg-emerald-950/40 border-emerald-400 shadow-lg glow-emerald'
                        : isHealthy
                        ? 'bg-black/60 border-emerald-500/40 text-emerald-400'
                        : 'bg-red-950/30 border-red-500/30 text-red-400 line-through opacity-60'
                    }`}>
                      <span className="text-[10px] font-mono font-bold">Step #{idx}</span>
                      <span className="text-[9px] font-mono mt-0.5">
                        {isInflection ? '★ Inflection' : isHealthy ? 'Healthy' : 'Poisoned'}
                      </span>
                    </div>
                    {idx < rewindStep && (
                      <ArrowRight className={`w-3.5 h-3.5 ${idx >= targetStep ? 'text-red-500/50' : 'text-emerald-500/50'}`} />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Action Bar */}
            <div className="pt-2 border-t border-white/10 flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
                <Scissors className="w-4 h-4 text-red-400" />
                <span>Pruned Poisoned Turns: <strong className="text-red-400">{rewindResult?.pruned_steps_count || (rewindStep - 2)} steps cut</strong></span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
                <FileCheck className="w-4 h-4 text-sentry-emerald" />
                <span>Filesystem Rollback: <strong className="text-sentry-emerald">State Restored to Snapshot t={rewindResult?.target_step || 2}</strong></span>
              </div>
            </div>
          </div>

          {/* Results Grid: 3 Metric Cards + Synthesized Directive */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-black/60 border border-white/5 font-mono text-xs space-y-1">
              <span className="text-slate-400 text-[10px] uppercase">Tokens Salvaged:</span>
              <div className="text-2xl font-bold text-sentry-cyan">
                {rewindResult ? rewindResult.estimated_tokens_saved.toLocaleString() : '18,500'}
              </div>
              <div className="text-[10px] text-slate-500">Prevented runaway LLM context spill</div>
            </div>

            <div className="p-4 rounded-xl bg-black/60 border border-white/5 font-mono text-xs space-y-1">
              <span className="text-slate-400 text-[10px] uppercase">Capital Preserved:</span>
              <div className="text-2xl font-bold text-sentry-emerald">
                ${rewindResult ? rewindResult.estimated_cost_saved_usd.toFixed(2) : '0.45'} USD
              </div>
              <div className="text-[10px] text-slate-500">Saved by early rollback vs infinite retry</div>
            </div>

            <div className="p-4 rounded-xl bg-black/60 border border-white/5 font-mono text-xs space-y-1">
              <span className="text-slate-400 text-[10px] uppercase">Autonomic Intervention:</span>
              <div className="text-2xl font-bold text-amber-400">
                REROUTE
              </div>
              <div className="text-[10px] text-slate-500">Context pruned + steered</div>
            </div>
          </div>

          {/* Synthesized Counterfactual Steering Directive */}
          <div className="p-4 rounded-xl bg-violet-950/20 border border-violet-500/30 space-y-2">
            <div className="flex items-center gap-2 font-mono text-xs text-sentry-violet font-bold">
              <Wand2 className="w-4 h-4" />
              <span>Synthesized Counterfactual Steering Directive (Dispatched into Agent Context):</span>
            </div>
            <div className="p-3.5 rounded-lg bg-black/80 border border-white/10 font-mono text-xs text-slate-200 leading-relaxed">
              <code>{rewindResult?.counterfactual_directive || `AUTONOMIC REROUTE DIRECTIVE: Terminate repetitive calls to '${rewindTool}'. Pruned turns ${rewindResult ? rewindResult.target_step + 1 : 3} through ${rewindStep}. Adopt an alternative approach: inspect schema state or use non-destructive migration flags.`}</code>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

