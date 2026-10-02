import React, { useState } from 'react';
import { 
  Flame, 
  Repeat, 
  Bomb, 
  EyeOff, 
  CheckCircle, 
  XCircle, 
  ArrowRight,
  TrendingDown,
  DollarSign,
  AlertOctagon,
  Sparkles
} from 'lucide-react';

interface Trap {
  id: string;
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  subtitle: string;
  realWorldStory: string;
  damageCost: string;
  agentryFix: string;
}

const TRAPS: Trap[] = [
  {
    id: 'spiral',
    icon: <Repeat className="w-6 h-6 text-amber-400" />,
    iconBg: 'bg-amber-500/10 border-amber-500/20',
    title: 'The $1,000 Infinite Retry Spiral',
    subtitle: 'AI Agents Repeating Crashes 40 Times While You Sleep',
    realWorldStory: 'An AI agent fails a unit test due to a missing comma. Instead of stopping, the agent edits the wrong line and reruns the same test 40 times in a row. Context balloons to 128k tokens, silently burning through your budget.',
    damageCost: 'Cloud bills inflate by $800 - $1,500 overnight with zero working code.',
    agentryFix: 'TabPFN identifies repetitive multivariate step entropy at step 5, breaks the loop, and halts token consumption immediately.'
  },
  {
    id: 'blast',
    icon: <Bomb className="w-6 h-6 text-sentry-red" />,
    iconBg: 'bg-red-500/10 border-red-500/20',
    title: 'Irreversible Blast Radius',
    subtitle: 'Terminal Commands That Wipe Out Production Servers',
    realWorldStory: 'Granted bash terminal access to clear cache, a hallucinating agent runs "rm -rf /" or drops primary database tables. Irreversible data loss strikes before a human operator can hit cancel.',
    damageCost: 'Permanent customer data loss, production service downtime, and catastrophic business impact.',
    agentryFix: 'Agentry Layer 1 halts high-hazard terminal commands in <1ms before the OS shell ever spawns.'
  },
  {
    id: 'leak',
    icon: <EyeOff className="w-6 h-6 text-sentry-violet" />,
    iconBg: 'bg-violet-500/10 border-violet-500/20',
    title: 'Silent Credential Leaks',
    subtitle: 'API Keys & Passwords Leaking to Third-Party Clouds',
    realWorldStory: 'Many agent supervisory tools forward entire conversation logs to commercial third-party LLMs for monitoring. Unbeknownst to you, .env files, private SSH keys, and database tokens leak to external servers.',
    damageCost: 'Stolen credentials, regulatory compliance penalties, and systemic breach vulnerabilities.',
    agentryFix: '100% Zero-Prompt Transmission: TabPFN evaluates purely on 16 numerical telemetry metrics. Your secret code never leaves your local environment.'
  }
];

export const FatalTraps: React.FC = () => {
  const [selectedTrap, setSelectedTrap] = useState<string>('spiral');

  return (
    <section id="traps" className="py-20 px-4 lg:px-8 max-w-6xl mx-auto relative">
      
      {/* Header */}
      <div className="text-center mb-14">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/30 text-sentry-red text-xs font-mono font-medium mb-3 animate-pulse-glow">
          <Flame className="w-3.5 h-3.5" />
          <span>WHY STATIC HEURISTICS ALWAYS FAIL</span>
        </div>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-white mb-3">
          The 3 Fatal Traps of Autonomous Agent Fleets
        </h2>
        <p className="text-slate-300 max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
          Autonomous agents operate at machine speed in high-dimensional codebases and APIs. Without a foundation model tabular sentry, small errors spiral into catastrophic failures.
        </p>
      </div>

      {/* Trap Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {TRAPS.map((trap) => {
          const isSelected = selectedTrap === trap.id;
          return (
            <div 
              key={trap.id}
              onClick={() => setSelectedTrap(trap.id)}
              className={`glass-card rounded-2xl p-6 sm:p-7 border transition-all cursor-pointer flex flex-col justify-between relative overflow-hidden group ${
                isSelected 
                  ? 'bg-surface-2/90 border-white/30 shadow-2xl scale-[1.02]' 
                  : 'hover:bg-surface-2/50 border-white/10 hover:border-white/20'
              }`}
            >
              <div>
                <div className={`w-12 h-12 rounded-xl ${trap.iconBg} border flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                  {trap.icon}
                </div>

                <div className="text-xs font-mono text-sentry-cyan mb-1">
                  {trap.subtitle}
                </div>

                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-sentry-emerald transition-colors">
                  {trap.title}
                </h3>

                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
                  {trap.realWorldStory}
                </p>
              </div>

              <div className="space-y-3 pt-4 border-t border-white/10 text-xs">
                {/* Damage */}
                <div className="p-3 rounded-xl bg-red-950/30 border border-red-500/25 flex items-start gap-2.5">
                  <XCircle className="w-4 h-4 text-sentry-red shrink-0 mt-0.5" />
                  <span className="text-red-200">
                    <strong className="text-white">Financial & System Impact:</strong> {trap.damageCost}
                  </span>
                </div>

                {/* Agentry Fix */}
                <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/25 flex items-start gap-2.5">
                  <CheckCircle className="w-4 h-4 text-sentry-emerald shrink-0 mt-0.5" />
                  <span className="text-emerald-200">
                    <strong className="text-white">Agentry Autonomous Solution:</strong> {trap.agentryFix}
                  </span>
                </div>
              </div>

              {isSelected && (
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-sentry-cyan via-emerald-400 to-sentry-emerald" />
              )}
            </div>
          );
        })}
      </div>

      {/* Bottom Summary Banner */}
      <div className="mt-10 p-5 rounded-2xl glass-card border border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-sentry-emerald animate-pulse" />
          <span className="text-xs sm:text-sm text-slate-200">
            <strong>Key Takeaway:</strong> Agentry is not a brittle set of IF/ELSE rules — it is an autonomous sentry powered by Bayesian tabular priors, defending your codebase, data, and budget without manual oversight.
          </span>
        </div>
        <a 
          href="#playground" 
          className="shrink-0 px-4 py-2 rounded-xl bg-surface-2 hover:bg-surface-3 border border-white/10 text-xs font-mono text-sentry-cyan hover:text-white transition-colors"
        >
          Try in Simulator ↑
        </a>
      </div>

    </section>
  );
};
