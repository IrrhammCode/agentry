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
import { LiveHeroTerminal } from '../components/LiveHeroTerminal.tsx';
import { LiveTelemetryTicker } from '../components/LiveTelemetryTicker.tsx';

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
            <span className="animate-text-shimmer animate-text-glow">Cloud, Code, and Cash.</span>
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
          {/* ANIMATED LIVE SENTRY HUD RADAR TERMINAL                          */}
          {/* ================================================================= */}
          <LiveHeroTerminal />

        </div>
      </section>

      {/* Real-Time Telemetry Scrolling Marquee Ticker */}
      <LiveTelemetryTicker />

      {/* Interactive Simulator Component */}
      <div id="playground">
        <AttackSimulator />
      </div>

      {/* The 3 Fatal Traps */}
      <div id="traps">
        <FatalTraps />
      </div>

      {/* 3-Layer Defense-in-Depth Architecture */}
      <div id="architecture">
        <DefenseArchitecture />
      </div>

      {/* Empirical Benchmarks Arena */}
      <div id="benchmarks">
        <BenchmarkArena />
      </div>

      {/* Enterprise Bento Grid */}
      <div id="features">
        <BentoGrid />
      </div>

      {/* ROI & Cost Calculator */}
      <div id="calculator">
        <RoiCalculator />
      </div>

      {/* Developer Quickstart */}
      <div id="quickstart">
        <DeveloperQuickstart />
      </div>

      {/* FAQ Section */}
      <div id="faq">
        <FaqSection />
      </div>

    </div>
  );
};
