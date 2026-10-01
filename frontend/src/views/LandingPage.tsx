import React from 'react';
import { 
  Activity, 
  ArrowRight, 
  ShieldAlert, 
  CheckCircle, 
  Zap, 
  Lock, 
  Cpu, 
  OctagonAlert, 
  Sparkles 
} from 'lucide-react';
import { AttackSimulator } from '../components/AttackSimulator.tsx';
import { FatalTraps } from '../components/FatalTraps.tsx';
import { DefenseArchitecture } from '../components/DefenseArchitecture.tsx';
import { BenchmarkArena } from '../components/BenchmarkArena.tsx';
import { BentoGrid } from '../components/BentoGrid.tsx';
import { RoiCalculator } from '../components/RoiCalculator.tsx';
import { DeveloperQuickstart } from '../components/DeveloperQuickstart.tsx';
import { FaqSection } from '../components/FaqSection.tsx';

interface LandingPageProps {
  onLaunchConsole: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onLaunchConsole }) => {
  return (
    <div className="flex-grow">
      
      {/* Hero Section */}
      <section className="relative pt-16 pb-20 px-4 lg:px-8 overflow-hidden">
        {/* Ambient Backlight Glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-sentry-cyan/15 via-emerald-500/10 to-transparent blur-[120px] pointer-events-none -z-10" />

        <div className="max-w-6xl mx-auto text-center">
          
          {/* Eyebrow Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-sentry-emerald text-xs font-mono font-medium mb-6 animate-pulse-glow">
            <span className="w-2 h-2 rounded-full bg-sentry-emerald animate-ping" />
            <span>PRIOR LABS TABPFN-3.5 GLOBAL HACKATHON 2026</span>
            <span className="text-white/40">•</span>
            <span className="text-sentry-cyan">DEFENSE TRACK</span>
          </div>

          {/* Main H1 Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-display font-extrabold tracking-tight text-white mb-6 leading-[1.1]">
            Stop AI Agents from Burning Your <br className="hidden sm:inline" />
            <span className="text-gradient">Cloud, Code, and Cash.</span>
          </h1>

          {/* Subheadline */}
          <p className="max-w-3xl mx-auto text-lg sm:text-xl text-slate-300 font-normal mb-8 leading-relaxed">
            The first autonomous tabular sentry for AI fleets. Evaluates multimodal telemetry in{' '}
            <span className="text-sentry-cyan font-semibold">14.8 milliseconds</span> using{' '}
            <span className="text-sentry-emerald font-semibold">Prior Labs TabPFN-3.5</span>, 
            intercepts destructive shell commands, redacts credentials in-flight, and autonomically heals rogue loops with{' '}
            <span className="text-white font-medium underline decoration-sentry-cyan/50 underline-offset-4">
              zero code changes
            </span>.
          </p>

          {/* Action Button Cluster */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-10">
            <button 
              onClick={onLaunchConsole}
              className="flex items-center gap-2.5 px-8 py-4 rounded-xl bg-gradient-to-r from-sentry-cyan via-emerald-400 to-sentry-emerald text-void font-bold text-sm tracking-wide glow-cyan hover:scale-[1.03] transition-all"
            >
              <Activity className="w-4 h-4" />
              <span>ENTER MISSION CONTROL</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            
            <a 
              href="#playground" 
              className="flex items-center gap-2 px-6 py-4 rounded-xl glass-card hover:bg-surface-2 border border-white/10 text-white font-semibold text-sm transition-all"
            >
              <ShieldAlert className="w-4 h-4 text-sentry-cyan" />
              <span>Test Attack Simulator</span>
            </a>
          </div>

          {/* Trust Badges */}
          <div className="flex flex-wrap items-center justify-center gap-y-2 gap-x-8 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-sentry-emerald" />
              <span>100% Local Privacy Guarantee</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-sentry-cyan" />
              <span>Sub-20ms Bayesian Inference</span>
            </div>
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-sentry-violet" />
              <span>Zero Prompt Transmission</span>
            </div>
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-400" />
              <span>SWE-bench Validated (1,156 Steps)</span>
            </div>
          </div>

          {/* ================================================================= */}
          {/* FLOATING 3D SENTRY HUD TERMINAL                                   */}
          {/* ================================================================= */}
          <div className="mt-14 max-w-4xl mx-auto glass-card rounded-2xl overflow-hidden border border-white/15 shadow-2xl relative text-left">
            
            {/* Terminal Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-surface-1/90 border-b border-white/10">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 font-mono text-xs text-slate-400">SESSION: swe_bench_fix_auth_regress.jsonl</span>
              </div>
              <div className="flex items-center gap-3 font-mono text-xs">
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald border border-emerald-500/30">
                  AGENT: CoderAgent-01
                </span>
                <span className="text-slate-400 hidden sm:inline">CIRCUIT-BREAKER: ARMED</span>
              </div>
            </div>

            {/* Terminal Telemetry Body */}
            <div className="p-5 font-mono text-xs space-y-3 bg-void/90 min-h-[220px]">
              <div className="flex items-start justify-between text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="text-sentry-cyan">t=1</span>
                  <span>tool: read_file("auth/tokens.py")</span>
                </div>
                <span className="text-emerald-400 font-bold">NOMINAL (P_fail=0.03) • PASS</span>
              </div>
              
              <div className="flex items-start justify-between text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="text-sentry-cyan">t=2</span>
                  <span>tool: replace_code("tokens.py:42", "new_logic")</span>
                </div>
                <span className="text-emerald-400 font-bold">NOMINAL (P_fail=0.07) • PASS</span>
              </div>

              <div className="flex items-start justify-between text-amber-300">
                <div className="flex items-center gap-2">
                  <span className="text-sentry-cyan">t=3</span>
                  <span>tool: run_command("pytest tests/test_auth.py")</span>
                  <span className="text-slate-500">[Exit: 1 Crash]</span>
                </div>
                <span className="text-amber-400 font-bold">ANOMALY_RUNAWAY (P_fail=0.68) • WARN</span>
              </div>

              <div className="flex items-start justify-between text-red-300">
                <div className="flex items-center gap-2">
                  <span className="text-sentry-cyan">t=4</span>
                  <span>tool: run_command("pytest tests/test_auth.py")</span>
                  <span className="text-slate-500">[Repeated Error Loop streak=2]</span>
                </div>
                <span className="text-sentry-red font-bold">CRITICAL_LOOP (P_fail=0.94) • REROUTE</span>
              </div>

              <div className="flex items-start justify-between text-red-400 bg-red-950/40 p-2.5 rounded-lg border border-red-500/30">
                <div className="flex items-center gap-2 font-bold">
                  <OctagonAlert className="w-4 h-4 text-sentry-red animate-pulse" />
                  <span className="text-sentry-red">t=5</span>
                  <span>BLAST RADIUS TRIP: run_command("rm -rf /var/cache/*")</span>
                </div>
                <span className="text-white bg-red-600 px-2 py-0.5 rounded text-[11px] font-bold">
                  🛑 CIRCUIT-BREAKER KILL
                </span>
              </div>
            </div>

            {/* Autonomic Ribbon */}
            <div className="px-5 py-3 bg-gradient-to-r from-emerald-950/80 via-surface-1 to-cyan-950/80 border-t border-emerald-500/30 flex items-center justify-between flex-wrap gap-2 text-xs">
              <div className="flex items-center gap-2 text-sentry-emerald font-semibold">
                <Sparkles className="w-4 h-4 animate-spin" />
                <span>Autonomic Healer Engaged:</span>
                <span className="text-slate-300 font-normal">Physical snapshot rollback to t=2 • Injected counterfactual prompt directive</span>
              </div>
              <div className="font-mono text-[11px] text-sentry-cyan font-bold">
                ⚡ Recovery Time: 12ms • Cost Saved: $1.42
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* Interactive Simulator Component */}
      <AttackSimulator />

      {/* The 3 Fatal Traps */}
      <FatalTraps />

      {/* 3-Layer Defense-in-Depth Architecture */}
      <DefenseArchitecture />

      {/* Empirical Benchmarks Arena */}
      <BenchmarkArena />

      {/* Enterprise Bento Grid */}
      <BentoGrid />

      {/* ROI & Cost Calculator */}
      <RoiCalculator />

      {/* Developer Quickstart */}
      <DeveloperQuickstart />

      {/* FAQ Section */}
      <FaqSection />

    </div>
  );
};
