import React, { useState } from 'react';
import { 
  Bot, 
  ShieldCheck, 
  BadgeDollarSign, 
  UserCheck, 
  Radio, 
  Power, 
  PieChart, 
  TrendingUp, 
  PauseCircle, 
  Check, 
  Shuffle, 
  XOctagon 
} from 'lucide-react';

export const MissionControl: React.FC = () => {
  const [hitlCount, setHitlCount] = useState<number>(1);
  const [steerModalOpen, setSteerModalOpen] = useState<boolean>(false);
  const [steerDirective, setSteerDirective] = useState<string>('Avoid dropping tables; use non-destructive schema migration.');
  const [notification, setNotification] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 3500);
  };

  const handleApprove = () => {
    setHitlCount(0);
    showToast('✓ Action Approved: Agent devops_db_migration_prod resumed with execution envelope.');
  };

  const handleSteerSubmit = () => {
    setSteerModalOpen(false);
    setHitlCount(0);
    showToast(`🔀 Steering Directive Dispatched: "${steerDirective}"`);
  };

  const handleAbort = () => {
    setHitlCount(0);
    showToast('🛑 Session Aborted: Trajectory killed and disk rolled back to initial commit.');
  };

  const handleEmergencyStop = () => {
    if (window.confirm('🛑 CRITICAL EMERGENCY OVERRIDE:\nAre you sure you want to FREEZE ALL 4 running agent instances immediately?')) {
      showToast('🛑 GLOBAL KILL SWITCH TRIPPED: All 4 agent execution loops suspended.');
    }
  };

  return (
    <div className="flex-grow max-w-7xl mx-auto w-full px-4 lg:px-8 py-8 space-y-8">
      
      {/* Toast Notification */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 glass-card border border-emerald-500/40 bg-surface-1/95 p-4 rounded-xl text-xs font-mono text-sentry-emerald shadow-2xl flex items-center gap-2 glow-emerald">
          <Check className="w-4 h-4 text-sentry-emerald" />
          <span>{notification}</span>
        </div>
      )}

      {/* Top KPI Command Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card rounded-xl p-4 border border-white/10">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>ACTIVE SWARM FLEET</span>
            <Bot className="w-4 h-4 text-sentry-cyan" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">
            4 Agents <span className="text-xs text-emerald-400 font-normal">● Live</span>
          </div>
        </div>

        <div className="glass-card rounded-xl p-4 border border-white/10">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>RISK INTERCEPTION RATE</span>
            <ShieldCheck className="w-4 h-4 text-sentry-emerald" />
          </div>
          <div className="text-2xl font-bold font-mono text-sentry-emerald">
            94.2% <span className="text-xs text-slate-400 font-normal">P(Recall)</span>
          </div>
        </div>

        <div className="glass-card rounded-xl p-4 border border-white/10">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>DOLLARS SALVAGED</span>
            <BadgeDollarSign className="w-4 h-4 text-sentry-cyan" />
          </div>
          <div className="text-2xl font-bold font-mono text-sentry-cyan">
            $124.50 <span className="text-xs text-slate-400 font-normal">Today</span>
          </div>
        </div>

        <div className="glass-card rounded-xl p-4 border border-white/10">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>HITL ESCALATIONS</span>
            <UserCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-400">
            {hitlCount} Pending
          </div>
        </div>
      </div>

      {/* Active 4-Agent Fleet Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-display font-bold text-white flex items-center gap-2">
              <Radio className="w-5 h-5 text-sentry-cyan animate-pulse" />
              Live Fleet Radar & Telemetry Stream
            </h2>
            <p className="text-xs text-slate-400 font-mono">Synchronized 4-Agent Cluster • 15ms TabPFN Sentry Polling</p>
          </div>
          <button 
            onClick={handleEmergencyStop}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-sentry-red border border-red-500/30 text-xs font-mono font-bold transition-all"
          >
            <Power className="w-3.5 h-3.5" />
            <span>GLOBAL KILL SWITCH</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Agent 1: CoderAgent */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 hover:border-emerald-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs font-bold text-white">CoderAgent-01</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald text-[10px] font-mono font-semibold">RUNNING</span>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="relative w-14 h-14 flex items-center justify-center shrink-0">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path className="text-surface-2 stroke-current" strokeWidth="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path className="text-sentry-emerald stroke-current" strokeDasharray="14, 100" strokeWidth="3.5" strokeLinecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                  </svg>
                  <span className="absolute font-mono text-xs font-bold text-sentry-emerald">14%</span>
                </div>
                <div className="font-mono text-[11px] space-y-1">
                  <div className="text-slate-400">Step: <span className="text-white font-bold">12 / 50</span></div>
                  <div className="text-slate-400">Burn: <span className="text-sentry-cyan font-bold">$0.34</span></div>
                  <div className="text-slate-400">Tool: <span className="text-emerald-300">edit_file()</span></div>
                </div>
              </div>
            </div>
            <div className="p-2.5 rounded bg-void/80 font-mono text-[10px] text-slate-400 truncate">
              &gt; refactoring auth_middleware.py tests...
            </div>
          </div>

          {/* Agent 2: DevOps-Sentry */}
          <div className="glass-card rounded-2xl p-5 border border-red-500/30 bg-red-950/10 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs font-bold text-white">DevOps-Sentry</span>
                <span className="px-2 py-0.5 rounded bg-red-500/20 text-sentry-red text-[10px] font-mono font-semibold animate-pulse">INTERCEPTED</span>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="relative w-14 h-14 flex items-center justify-center shrink-0">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path className="text-surface-2 stroke-current" strokeWidth="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path className="text-sentry-red stroke-current" strokeDasharray="96, 100" strokeWidth="3.5" strokeLinecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                  </svg>
                  <span className="absolute font-mono text-xs font-bold text-sentry-red">96%</span>
                </div>
                <div className="font-mono text-[11px] space-y-1">
                  <div className="text-slate-400">Step: <span className="text-white font-bold">5 / 20</span></div>
                  <div className="text-slate-400">Burn: <span className="text-sentry-red font-bold">$1.89</span></div>
                  <div className="text-slate-400">Tool: <span className="text-red-400">rm -rf</span></div>
                </div>
              </div>
            </div>
            <div className="p-2.5 rounded bg-red-950/50 font-mono text-[10px] text-red-300 truncate">
              🛑 Blast radius kill: root cleanup blocked
            </div>
          </div>

          {/* Agent 3: ResearchBot */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 hover:border-amber-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs font-bold text-white">ResearchBot-03</span>
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[10px] font-mono font-semibold">REROUTED</span>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="relative w-14 h-14 flex items-center justify-center shrink-0">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path className="text-surface-2 stroke-current" strokeWidth="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path className="text-amber-400 stroke-current" strokeDasharray="64, 100" strokeWidth="3.5" strokeLinecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                  </svg>
                  <span className="absolute font-mono text-xs font-bold text-amber-400">64%</span>
                </div>
                <div className="font-mono text-[11px] space-y-1">
                  <div className="text-slate-400">Step: <span className="text-white font-bold">18 / 40</span></div>
                  <div className="text-slate-400">Burn: <span className="text-amber-400 font-bold">$0.78</span></div>
                  <div className="text-slate-400">Tool: <span className="text-amber-300">fetch_url()</span></div>
                </div>
              </div>
            </div>
            <div className="p-2.5 rounded bg-void/80 font-mono text-[10px] text-slate-400 truncate">
              &gt; pruned 3 duplicate search steps
            </div>
          </div>

          {/* Agent 4: DataAnalyst */}
          <div className="glass-card rounded-2xl p-5 border border-white/10 hover:border-emerald-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs font-bold text-white">DataAnalyst-04</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald text-[10px] font-mono font-semibold">RUNNING</span>
              </div>
              <div className="flex items-center gap-3 mb-4">
                <div className="relative w-14 h-14 flex items-center justify-center shrink-0">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path className="text-surface-2 stroke-current" strokeWidth="3.5" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path className="text-sentry-emerald stroke-current" strokeDasharray="8, 100" strokeWidth="3.5" strokeLinecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                  </svg>
                  <span className="absolute font-mono text-xs font-bold text-sentry-emerald">8%</span>
                </div>
                <div className="font-mono text-[11px] space-y-1">
                  <div className="text-slate-400">Step: <span className="text-white font-bold">29 / 30</span></div>
                  <div className="text-slate-400">Burn: <span className="text-sentry-cyan font-bold">$1.11</span></div>
                  <div className="text-slate-400">Tool: <span className="text-emerald-300">sql_aggregate()</span></div>
                </div>
              </div>
            </div>
            <div className="p-2.5 rounded bg-void/80 font-mono text-[10px] text-slate-400 truncate">
              &gt; final aggregations validated
            </div>
          </div>

        </div>
      </div>

      {/* Central Charts Row: Multiclass Donut + Cost Trajectory */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Multiclass Donut */}
        <div className="lg:col-span-5 glass-card rounded-2xl p-6 border border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <PieChart className="w-4 h-4 text-sentry-cyan" />
                TabPFN Multiclass Anomaly Distribution
              </h3>
              <span className="font-mono text-[11px] text-sentry-emerald">Bayesian In-Context</span>
            </div>
            
            <div className="h-56 flex items-center justify-center relative">
              <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 42 42">
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#1E293B" strokeWidth="5"></circle>
                {/* Nominal: 78.4% */}
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#00FF87" strokeWidth="5" strokeDasharray="78.4 21.6" strokeDashoffset="0"></circle>
                {/* Infinite Loop: 14.2% */}
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#EF4444" strokeWidth="5" strokeDasharray="14.2 85.8" strokeDashoffset="-78.4"></circle>
                {/* Poisoned Context: 5.1% */}
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#F59E0B" strokeWidth="5" strokeDasharray="5.1 94.9" strokeDashoffset="-92.6"></circle>
                {/* Runaway Cost: 2.3% */}
                <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#8B5CF6" strokeWidth="5" strokeDasharray="2.3 97.7" strokeDashoffset="-97.7"></circle>
              </svg>
              <div className="absolute text-center">
                <span className="text-xl font-bold font-mono text-white">78.4%</span>
                <span className="block text-[10px] text-slate-400 font-mono">NOMINAL</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-white/10 grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400">
            <div>● Nominal: <span className="text-sentry-emerald font-bold">78.4%</span></div>
            <div>● Infinite Loop: <span className="text-sentry-red font-bold">14.2%</span></div>
            <div>● Context Poison: <span className="text-amber-400 font-bold">5.1%</span></div>
            <div>● Cost Runaway: <span className="text-violet-400 font-bold">2.3%</span></div>
          </div>
        </div>

        {/* Cost Regression Trajectory */}
        <div className="lg:col-span-7 glass-card rounded-2xl p-6 border border-white/10 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-sentry-emerald" />
                Runaway Cost Projection (TabPFN vs Actual)
              </h3>
              <span className="font-mono text-[11px] text-sentry-cyan">R² = 0.782 • MAE = $0.0057</span>
            </div>

            <div className="h-56 flex flex-col justify-center">
              <svg className="w-full h-40" viewBox="0 0 500 150">
                {/* Grid Lines */}
                <line x1="40" y1="20" x2="480" y2="20" stroke="rgba(255,255,255,0.05)" />
                <line x1="40" y1="60" x2="480" y2="60" stroke="rgba(255,255,255,0.05)" />
                <line x1="40" y1="100" x2="480" y2="100" stroke="rgba(255,255,255,0.05)" />
                <line x1="40" y1="130" x2="480" y2="130" stroke="rgba(255,255,255,0.1)" />

                {/* Projected Runaway Line (Dashed Red) */}
                <polyline 
                  fill="none" 
                  stroke="#EF4444" 
                  strokeWidth="2.5" 
                  strokeDasharray="6,4" 
                  points="50,130 110,128 170,124 230,115 290,100 350,65 410,35 470,15"
                />

                {/* Actual Controlled Line (Solid Cyan) */}
                <polyline 
                  fill="none" 
                  stroke="#60EFFF" 
                  strokeWidth="3" 
                  points="50,130 110,128 170,124 230,115 290,105"
                />

                {/* Points */}
                <circle cx="50" cy="130" r="3.5" fill="#60EFFF" />
                <circle cx="110" cy="128" r="3.5" fill="#60EFFF" />
                <circle cx="170" cy="124" r="3.5" fill="#60EFFF" />
                <circle cx="230" cy="115" r="3.5" fill="#60EFFF" />
                <circle cx="290" cy="105" r="5" fill="#EF4444" className="animate-ping" />
                <circle cx="290" cy="105" r="4" fill="#EF4444" />

                {/* Text marker */}
                <text x="300" y="100" fill="#EF4444" fontSize="10" fontFamily="monospace" fontWeight="bold">Kill @ t=4</text>
              </svg>
              <div className="flex justify-between text-[10px] text-slate-500 font-mono px-6">
                <span>t=0</span>
                <span>t=1</span>
                <span>t=2</span>
                <span>t=3</span>
                <span>t=4 (Kill)</span>
                <span>t=5 (Proj)</span>
                <span>t=6 (Proj)</span>
                <span>t=7 (Proj)</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-white/10 flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>Inflection Point Detected at Step 4</span>
            <span className="text-sentry-emerald font-bold">Early Kill Saved $4.85</span>
          </div>
        </div>

      </div>

      {/* Human-in-the-Loop (HITL) War Room & Approval Queue */}
      <div className="glass-card rounded-2xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-bold text-white text-lg flex items-center gap-2">
              <PauseCircle className="w-5 h-5 text-amber-400" />
              HITL Operator War Room & Steering Queue
            </h3>
            <p className="text-xs text-slate-400 font-mono">Quarantined Agent Sessions Requiring Supervisor Escalation</p>
          </div>
          <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${
            hitlCount > 0 
              ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' 
              : 'bg-emerald-500/20 text-sentry-emerald border-emerald-500/30'
          }`}>
            {hitlCount > 0 ? `${hitlCount} Active Escalation` : 'All Clear (0 Pending)'}
          </span>
        </div>

        {hitlCount > 0 ? (
          <div className="p-5 rounded-xl bg-surface-2/60 border border-amber-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 font-mono text-xs text-slate-300 mb-1">
                <span className="text-amber-400 font-bold">[ESCALATION #HITL-8941]</span>
                <span>Session: <code className="text-sentry-cyan">devops_db_migration_prod</code></span>
                <span className="text-slate-500">• 2 mins ago</span>
              </div>
              <p className="text-sm font-medium text-white mb-1">
                Agent attempted destructive SQL statement: <code className="text-red-400 font-mono">DROP TABLE audit_events_archive;</code>
              </p>
              <p className="text-xs text-slate-400">
                Blast Radius Score: <strong className="text-sentry-red">88/100</strong> • TabPFN Risk: <strong className="text-amber-400">0.89</strong> • System disk snapshot safely frozen.
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button 
                onClick={handleApprove}
                className="px-3.5 py-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-sentry-emerald border border-emerald-500/30 text-xs font-mono font-bold transition-all flex items-center gap-1.5"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Approve</span>
              </button>
              <button 
                onClick={() => setSteerModalOpen(true)}
                className="px-3.5 py-2 rounded-lg bg-sentry-cyan/20 hover:bg-sentry-cyan/30 text-sentry-cyan border border-sentry-cyan/30 text-xs font-mono font-bold transition-all flex items-center gap-1.5"
              >
                <Shuffle className="w-3.5 h-3.5" />
                <span>Steer Prompt</span>
              </button>
              <button 
                onClick={handleAbort}
                className="px-3.5 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-sentry-red border border-red-500/30 text-xs font-mono font-bold transition-all flex items-center gap-1.5"
              >
                <XOctagon className="w-3.5 h-3.5" />
                <span>Abort & Rollback</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center rounded-xl bg-void/40 border border-white/5 font-mono text-xs text-slate-500">
            ✓ No pending escalations in queue. Autonomous agents operating within safety envelope.
          </div>
        )}
      </div>

      {/* Steer Modal */}
      {steerModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card max-w-lg w-full rounded-2xl p-6 border border-sentry-cyan/40">
            <h3 className="text-base font-bold text-white mb-2">Inject Counterfactual Directive</h3>
            <p className="text-xs text-slate-400 mb-4">
              The agent will resume execution with this directive injected into its immediate reasoning context:
            </p>
            <textarea
              value={steerDirective}
              onChange={(e) => setSteerDirective(e.target.value)}
              rows={4}
              className="w-full bg-void rounded-xl p-3 font-mono text-xs text-sentry-cyan border border-white/10 focus:border-sentry-cyan focus:outline-none resize-none mb-4"
            />
            <div className="flex justify-end gap-2">
              <button 
                onClick={() => setSteerModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-surface-2 text-slate-300 text-xs font-mono"
              >
                Cancel
              </button>
              <button 
                onClick={handleSteerSubmit}
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-sentry-cyan to-sentry-emerald text-void font-bold text-xs font-mono"
              >
                Dispatch Directive
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
