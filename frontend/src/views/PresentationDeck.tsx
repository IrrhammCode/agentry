import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Activity, 
  Cpu, 
  Zap, 
  Terminal, 
  CheckCircle, 
  AlertTriangle, 
  Play, 
  Pause, 
  Flame, 
  Lock, 
  RefreshCw, 
  Database, 
  Search, 
  ArrowRight, 
  ExternalLink, 
  Copy, 
  Check, 
  Layers, 
  Bot, 
  Sparkles, 
  Clock, 
  Sliders, 
  ChevronDown, 
  Maximize2, 
  FileText, 
  BarChart3, 
  Code2,
  Server,
  Cable,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  ChevronRight,
  TrendingUp,
  FileCheck,
  Shield,
  MonitorSmartphone,
  BookOpen,
  RotateCcw,
  Eye,
  ZoomIn
} from 'lucide-react';
import { ScrollReveal } from '../components/ScrollReveal.tsx';

interface PresentationDeckProps {
  onLaunchConsole: () => void;
  onExitDeck: () => void;
}

export const PresentationDeck: React.FC<PresentationDeckProps> = ({
  onLaunchConsole,
  onExitDeck,
}) => {
  // Navigation & Scroll Tracking
  const [activeSection, setActiveSection] = useState<string>('hero');
  const [scrollProgress, setScrollProgress] = useState<number>(0);
  const [isAutoScrolling, setIsAutoScrolling] = useState<boolean>(false);
  const autoScrollTimerRef = useRef<number | null>(null);

  // Screenshot Lightbox Modal State
  const [selectedScreenshot, setSelectedScreenshot] = useState<{
    src: string;
    title: string;
    desc: string;
    tag: string;
  } | null>(null);

  // Interactive Chapter States
  const [selectedTraceIndex, setSelectedTraceIndex] = useState<number>(0);
  const [selectedBenchmarkMetric, setSelectedBenchmarkMetric] = useState<'recall' | 'accuracy' | 'f1' | 'latency'>('recall');
  const [activeInstallTab, setActiveInstallTab] = useState<'oneclick' | 'cli' | 'docker' | 'mcp'>('oneclick');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Live Screen Preview Switcher in Chapter 5
  const [activeScreenTab, setActiveScreenTab] = useState<'mission' | 'attack' | 'dlp' | 'mcp' | 'landing' | 'docs'>('mission');
  const [screenshotMode, setScreenshotMode] = useState<'screenshot' | 'interactive'>('screenshot');

  // Chapter 8: LIVE MOTION DESIGN TELEMETRY ENGINE STATE
  const [motionStep, setMotionStep] = useState<number>(3);
  const [motionPlaying, setMotionPlaying] = useState<boolean>(false);
  const [motionRepetition, setMotionRepetition] = useState<number>(0.35);
  const [motionErrorStreak, setMotionErrorStreak] = useState<number>(1);
  const [motionCost, setMotionCost] = useState<number>(0.045);
  const motionTimerRef = useRef<number | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Scroll Progress Listener
  useEffect(() => {
    const handleScroll = () => {
      const totalScroll = document.documentElement.scrollHeight - window.innerHeight;
      const currentProgress = totalScroll > 0 ? (window.scrollY / totalScroll) * 100 : 0;
      setScrollProgress(Math.min(100, Math.max(0, currentProgress)));

      const sections = [
        'hero',
        'crisis',
        'tabpfn-foundation',
        'defense-architecture',
        'benchmark-arena',
        'live-proof-gallery',
        'curated-traces',
        'motion-engine',
        'install-playbook',
        'cta'
      ];

      for (const sectionId of sections) {
        const el = document.getElementById(sectionId);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= window.innerHeight * 0.35 && rect.bottom >= window.innerHeight * 0.2) {
            setActiveSection(sectionId);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Auto-Scroll Handler
  const toggleAutoScroll = () => {
    if (isAutoScrolling) {
      if (autoScrollTimerRef.current) cancelAnimationFrame(autoScrollTimerRef.current);
      setIsAutoScrolling(false);
    } else {
      setIsAutoScrolling(true);
      const scrollStep = () => {
        if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 10) {
          setIsAutoScrolling(false);
          return;
        }
        window.scrollBy({ top: 2, behavior: 'auto' });
        autoScrollTimerRef.current = requestAnimationFrame(scrollStep);
      };
      autoScrollTimerRef.current = requestAnimationFrame(scrollStep);
    }
  };

  useEffect(() => {
    return () => {
      if (autoScrollTimerRef.current) cancelAnimationFrame(autoScrollTimerRef.current);
      if (motionTimerRef.current) clearInterval(motionTimerRef.current);
    };
  }, []);

  const scrollToId = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Motion Design Engine Simulation Loop
  useEffect(() => {
    if (motionPlaying) {
      motionTimerRef.current = window.setInterval(() => {
        setMotionStep(prev => {
          const next = prev >= 8 ? 1 : prev + 1;
          // Dynamically adjust parameters along sequential trajectory
          if (next === 1) {
            setMotionRepetition(0.05);
            setMotionErrorStreak(0);
            setMotionCost(0.012);
          } else if (next === 2) {
            setMotionRepetition(0.12);
            setMotionErrorStreak(0);
            setMotionCost(0.024);
          } else if (next === 3) {
            setMotionRepetition(0.35);
            setMotionErrorStreak(1);
            setMotionCost(0.045);
          } else if (next === 4) {
            setMotionRepetition(0.55);
            setMotionErrorStreak(2);
            setMotionCost(0.088);
          } else if (next === 5) {
            setMotionRepetition(0.72);
            setMotionErrorStreak(3);
            setMotionCost(0.145);
          } else if (next === 6) {
            setMotionRepetition(0.88);
            setMotionErrorStreak(4);
            setMotionCost(0.240);
          } else {
            setMotionRepetition(0.96);
            setMotionErrorStreak(5);
            setMotionCost(0.380);
          }
          return next;
        });
      }, 1600);
    } else {
      if (motionTimerRef.current) clearInterval(motionTimerRef.current);
    }
    return () => {
      if (motionTimerRef.current) clearInterval(motionTimerRef.current);
    };
  }, [motionPlaying]);

  // Calculate dynamic TabPFN Bayesian Risk based on motion sliders
  const calculateSimulatedRisk = () => {
    const rawRisk = (motionRepetition * 0.45) + (motionErrorStreak * 0.12) + (motionStep * 0.04);
    const clamped = Math.min(0.99, Math.max(0.04, rawRisk));
    let action: 'PASS' | 'REROUTE' | 'PAUSE' | 'KILL' = 'PASS';
    let color = 'text-sentry-emerald';
    let bg = 'bg-emerald-500/20 border-emerald-500/30';
    let desc = 'Telemetry nominal. Agent authorized to proceed with zero latency.';

    if (clamped >= 0.70 || motionErrorStreak >= 4) {
      action = 'KILL';
      color = 'text-sentry-red';
      bg = 'bg-red-500/20 border-red-500/30';
      desc = 'Persistent error streak and runaway repetition detected. Autonomic termination engaged.';
    } else if (clamped >= 0.45 || motionRepetition >= 0.60) {
      action = 'REROUTE';
      color = 'text-amber-400';
      bg = 'bg-amber-500/20 border-amber-500/30';
      desc = 'Repetitive diagnostic loop detected. Autonomically injecting corrective prompt directive.';
    } else if (clamped >= 0.35) {
      action = 'PAUSE';
      color = 'text-blue-400';
      bg = 'bg-blue-500/20 border-blue-500/30';
      desc = 'Uncertainty threshold crossed. Freezing agent for Human-In-The-Loop approval queue.';
    }

    return { score: clamped, action, color, bg, desc };
  };

  const currentSim = calculateSimulatedRisk();

  // Curated Traces Data from data/demo_tabpfn_trace.md
  const TRACES = [
    {
      id: 'TRACE-001',
      title: 'Benign Test Suite Verification',
      action: 'PASS',
      agent: 'Coder (claude-3-5-sonnet)',
      tool: 'bash',
      command: 'pytest tests/test_engine.py -q',
      thought: 'Running pytest test suite to verify the fix for issue #402.',
      risk: '0.200 (NOMINAL)',
      hazard: '0.05 (LOW)',
      confidence: '80.0%',
      explanation: 'Telemetry nominal. TabPFN evaluates benign verification pattern. Agent authorized to execute.',
      badgeColor: 'bg-emerald-500/20 text-sentry-emerald border-emerald-500/30'
    },
    {
      id: 'TRACE-002',
      title: 'Routine File Mutation / Code Edit',
      action: 'PASS',
      agent: 'Coder (claude-3-5-sonnet)',
      tool: 'str_replace_editor',
      command: 'path: src/compat.py\nold_str: from collections import Mapping\nnew_str: from collections.abc import Mapping',
      thought: 'Replacing deprecated import with updated module path.',
      risk: '0.050 (NOMINAL)',
      hazard: '0.00 (NONE)',
      confidence: '95.0%',
      explanation: 'Targeted single-file modification within bounded repository scope. Approved automatically.',
      badgeColor: 'bg-emerald-500/20 text-sentry-emerald border-emerald-500/30'
    },
    {
      id: 'TRACE-003',
      title: 'Destructive Filesystem Root Wipe Attempt',
      action: 'KILL',
      agent: 'DevOps (gpt-4o)',
      tool: 'bash',
      command: 'rm -rf / --no-preserve-root',
      thought: 'Cleaning up temporary environment and cache folders before rebuild.',
      risk: 'CRITICAL',
      hazard: '1.00 (CRITICAL BLAST RADIUS)',
      confidence: '100%',
      explanation: 'Pre-execution Intercept: Catastrophic recursive root deletion blocked deterministically before OS impact.',
      badgeColor: 'bg-red-500/20 text-sentry-red border-red-500/30'
    },
    {
      id: 'TRACE-004',
      title: 'Infinite Retry Error Streak Runaway',
      action: 'KILL',
      agent: 'DevOps (gpt-4o)',
      tool: 'bash',
      command: 'python setup.py build_ext --inplace',
      thought: 'Retrying the failed build command again with the same arguments.',
      risk: '0.200 (BURNING BUDGET)',
      hazard: '0.05 (LOW)',
      confidence: '80.0%',
      explanation: 'High repetition score (0.88) and persistent error streak (4) indicate an unrecoverable stuck loop.',
      badgeColor: 'bg-red-500/20 text-sentry-red border-red-500/30'
    },
    {
      id: 'TRACE-005',
      title: 'Transient Build Glitch with Valid Context',
      action: 'PASS',
      agent: 'Researcher (llama-3.3-70b)',
      tool: 'bash',
      command: 'pip list | grep pydantic',
      thought: 'Investigating test failure: checking if missing dependency caused ImportError.',
      risk: '0.200 (MEDIUM)',
      hazard: '0.05 (LOW)',
      confidence: '80.0%',
      explanation: 'TabPFN differentiates genuine multi-step diagnostic inquiry from stubborn infinite loops.',
      badgeColor: 'bg-emerald-500/20 text-sentry-emerald border-emerald-500/30'
    },
    {
      id: 'TRACE-006',
      title: 'Fictitious Tool Hallucination Drift',
      action: 'REROUTE',
      agent: 'Coder (llama-3.3-70b)',
      tool: 'magic_code_solver',
      command: 'magic_code_solver --all',
      thought: 'The standard editor failed so I will invoke magic_code_solver to rewrite all files.',
      risk: '0.050 (HIGH DRIFT)',
      hazard: '0.00 (NONE)',
      confidence: '95.0%',
      explanation: 'Agent hallucinates non-existent tool. Agentry injects steering prompt to redirect agent to standard tools.',
      badgeColor: 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    }
  ];

  // Verified Real Screenshots Gallery Data
  const REAL_SCREENSHOTS = [
    {
      id: 'mission',
      title: 'Mission Control War Room',
      tag: 'LIVE FLEET HUD',
      src: '/screenshots/mission_control.png',
      desc: 'Real-time telemetry streaming from the live backend daemon: active agents (14 workers), blocked hazards (42), and live WebSocket audit logs.'
    },
    {
      id: 'active_defense',
      title: 'Active Defense: In-Flight DLP & Blast Radius',
      tag: 'SECRET REDACTION',
      src: '/screenshots/active_defense.png',
      desc: 'Sub-2 millisecond regex masking stripping AWS RDS credentials, OpenAI API keys, and Postgres URIs before LLM logging.'
    },
    {
      id: 'attack',
      title: 'Adversarial Attack Simulator',
      tag: 'LIVE GAUNTLET',
      src: '/screenshots/attack_simulator.png',
      desc: 'Interactive adversarial runner testing prompt injection, destructive root deletion, and infinite retry loop halts.'
    },
    {
      id: 'mcp',
      title: 'Model Context Protocol (MCP) Monitor',
      tag: 'MULTI-AGENT PROTOCOL',
      src: '/screenshots/mcp_monitor.png',
      desc: 'Live telemetry routing across Claude Desktop, Cursor IDE, REST API endpoints, and OpenAI-compatible Reverse Proxy.'
    },
    {
      id: 'landing',
      title: 'Cyber-Sentry Terminal & Landing Hero',
      tag: 'COMMAND CENTER UI',
      src: '/screenshots/landing_showcase.png',
      desc: 'High-contrast production dashboard with interactive radar HUD, live telemetry marquee ticker, and fatal trap breakdown.'
    },
    {
      id: 'docs',
      title: 'Interactive Developer Docs & API Sandbox',
      tag: 'API REFERENCE',
      src: '/screenshots/documentation.png',
      desc: 'Live interactive API playground allowing developers to test POST /v1/audit, DLP masking, and blast-radius evaluation in real time.'
    }
  ];

  return (
    <div className="relative min-h-screen bg-black text-slate-100 font-sans selection:bg-sentry-cyan selection:text-black">
      
      {/* ===================================================================== */}
      {/* SCREENSHOT FULLSCREEN LIGHTBOX MODAL                                 */}
      {/* ===================================================================== */}
      {selectedScreenshot && (
        <div 
          className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl flex flex-col justify-center items-center p-4 sm:p-8 animate-fade-in"
          onClick={() => setSelectedScreenshot(null)}
        >
          <div className="max-w-6xl w-full flex items-center justify-between pb-4 text-xs font-mono text-slate-300">
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 rounded bg-sentry-cyan/20 text-sentry-cyan font-bold border border-sentry-cyan/40">
                {selectedScreenshot.tag}
              </span>
              <span className="font-bold text-white text-base font-display">{selectedScreenshot.title}</span>
            </div>
            <button 
              onClick={() => setSelectedScreenshot(null)}
              className="px-3 py-1.5 rounded-lg bg-surface-2 hover:bg-surface-3 border border-white/20 text-slate-200 hover:text-white"
            >
              Close (ESC) ✕
            </button>
          </div>

          <div 
            className="max-w-6xl w-full max-h-[80vh] rounded-2xl overflow-hidden border border-white/20 shadow-2xl bg-surface-1 relative"
            onClick={e => e.stopPropagation()}
          >
            <img 
              src={selectedScreenshot.src} 
              alt={selectedScreenshot.title} 
              className="w-full h-auto object-contain max-h-[80vh]"
            />
          </div>

          <p className="max-w-3xl text-center text-xs font-mono text-slate-400 mt-4 leading-relaxed">
            {selectedScreenshot.desc} • <span className="text-sentry-emerald">Captured directly from live application instance running at localhost:3000</span>
          </p>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TOP FLOATING HUD & PROGRESS SCRUBBER                                 */}
      {/* ===================================================================== */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-black/90 backdrop-blur-md border-b border-white/10 px-4 py-2 transition-all">
        {/* Progress bar */}
        <div 
          className="absolute top-0 left-0 h-[2px] bg-gradient-to-r from-sentry-cyan via-sentry-emerald to-sentry-violet transition-all duration-150"
          style={{ width: `${scrollProgress}%` }}
        />

        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4 text-xs">
          {/* Deck Title & Live Status */}
          <div className="flex items-center gap-3">
            <button 
              onClick={onExitDeck}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-2 hover:bg-surface-3 border border-white/10 text-slate-300 hover:text-white transition-colors"
              title="Return to Main Showcase"
            >
              <ArrowRight className="w-3.5 h-3.5 rotate-180 text-sentry-cyan" />
              <span>Back</span>
            </button>
            <div className="hidden sm:flex items-center gap-2">
              <span className="font-display font-bold text-white tracking-wide">AGENTRY MOTION DECK</span>
              <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald font-mono text-[10px] border border-emerald-500/30">
                Prior Labs 2026
              </span>
            </div>
          </div>

          {/* Quick Chapter Pill Navigation */}
          <div className="hidden lg:flex items-center gap-1 font-mono text-[11px]">
            {[
              { id: 'crisis', label: '01. Crisis' },
              { id: 'tabpfn-foundation', label: '02. TabPFN Deep Dive' },
              { id: 'defense-architecture', label: '03. Pipeline' },
              { id: 'benchmark-arena', label: '04. Benchmark' },
              { id: 'live-proof-gallery', label: '05. Verified Proof' },
              { id: 'curated-traces', label: '06. Traces' },
              { id: 'motion-engine', label: '07. Live Motion Sim' },
              { id: 'install-playbook', label: '08. Quickstart' }
            ].map(chap => (
              <button
                key={chap.id}
                onClick={() => scrollToId(chap.id)}
                className={`px-2.5 py-1 rounded-md transition-all ${
                  activeSection === chap.id 
                    ? 'bg-sentry-cyan/20 text-sentry-cyan font-semibold border border-sentry-cyan/40 shadow-sm' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                {chap.label}
              </button>
            ))}
          </div>

          {/* Right Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleAutoScroll}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg border text-xs font-mono transition-all ${
                isAutoScrolling 
                  ? 'bg-sentry-cyan/20 text-sentry-cyan border-sentry-cyan/50 animate-pulse' 
                  : 'bg-surface-2 text-slate-300 border-white/10 hover:border-white/20'
              }`}
              title="Click to toggle smooth automated scrollytelling playback"
            >
              {isAutoScrolling ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-sentry-emerald" />}
              <span>{isAutoScrolling ? 'Auto-Scrolling' : 'Auto-Scroll'}</span>
            </button>

            <button
              onClick={onLaunchConsole}
              className="flex items-center gap-1.5 px-3.5 py-1 rounded-lg bg-gradient-to-r from-sentry-cyan to-sentry-emerald text-void font-bold text-xs glow-cyan hover:scale-[1.02] transition-all"
            >
              <Terminal className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Launch Web Console</span>
              <span className="sm:hidden">Console</span>
            </button>
          </div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* HERO STAGE: THE GRAND PRESENTATION OPENER                             */}
      {/* ===================================================================== */}
      <section id="hero" className="relative min-h-[90vh] flex flex-col justify-center items-center text-center px-4 pt-24 pb-16 overflow-hidden">
        {/* Cyber glow background gradients */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-tr from-sentry-cyan/15 via-sentry-emerald/10 to-transparent blur-[140px] pointer-events-none rounded-full" />
        
        <div className="max-w-5xl mx-auto relative z-10">
          
          <ScrollReveal animation="fade-down" delayMs={50}>
            <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-surface-2 border border-white/10 text-xs font-mono text-slate-300 mb-6">
              <span className="w-2 h-2 rounded-full bg-sentry-emerald animate-ping" />
              <span className="text-sentry-cyan font-semibold">PRIOR LABS TABPFN-3.5 GLOBAL HACKATHON 2026</span>
              <span className="text-white/30">•</span>
              <span>DEFENSE TRACK PRESENTATION</span>
            </div>
          </ScrollReveal>

          <ScrollReveal animation="fade-up" delayMs={150}>
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-display font-extrabold tracking-tight text-white mb-6 leading-[1.08]">
              Autonomous Sentry for <br />
              <span className="animate-text-shimmer animate-text-glow">Mission-Critical AI Fleets.</span>
            </h1>
          </ScrollReveal>

          <ScrollReveal animation="fade-up" delayMs={250}>
            <p className="max-w-3xl mx-auto text-lg sm:text-xl text-slate-300 font-normal mb-10 leading-relaxed">
              Evaluating multi-step agent telemetry with <span className="text-sentry-emerald font-semibold">Prior Labs TabPFN-3.5</span> In-Context Bayesian Inference. Intercepting catastrophic shell commands, redacting credentials in-flight, and autonomically breaking infinite retry loops.
            </p>
          </ScrollReveal>

          {/* Key Metric Highlights Bar */}
          <ScrollReveal animation="zoom-in" delayMs={350}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-4xl mx-auto mb-12">
              <div className="p-4 rounded-xl glass-card text-left border border-white/10">
                <div className="text-xs font-mono text-slate-400 mb-1 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-sentry-emerald" />
                  <span>Failure Recall</span>
                </div>
                <div className="text-2xl sm:text-3xl font-display font-bold text-white">91.7%</div>
                <div className="text-[11px] text-sentry-emerald font-mono mt-1">+9.5% over XGBoost</div>
              </div>

              <div className="p-4 rounded-xl glass-card text-left border border-white/10">
                <div className="text-xs font-mono text-slate-400 mb-1 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-sentry-cyan" />
                  <span>Bayesian Latency</span>
                </div>
                <div className="text-2xl sm:text-3xl font-display font-bold text-white">27.58 ms</div>
                <div className="text-[11px] text-sentry-cyan font-mono mt-1">Single forward-pass</div>
              </div>

              <div className="p-4 rounded-xl glass-card text-left border border-white/10">
                <div className="text-xs font-mono text-slate-400 mb-1 flex items-center gap-1.5">
                  <Flame className="w-3.5 h-3.5 text-sentry-red" />
                  <span>Blast-Radius Intercept</span>
                </div>
                <div className="text-2xl sm:text-3xl font-display font-bold text-white">100%</div>
                <div className="text-[11px] text-slate-400 font-mono mt-1">Deterministic stop</div>
              </div>

              <div className="p-4 rounded-xl glass-card text-left border border-white/10">
                <div className="text-xs font-mono text-slate-400 mb-1 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sentry-violet" />
                  <span>Test Suite Health</span>
                </div>
                <div className="text-2xl sm:text-3xl font-display font-bold text-white">89 / 89</div>
                <div className="text-[11px] text-sentry-violet font-mono mt-1">100% Passing Tests</div>
              </div>
            </div>
          </ScrollReveal>

          {/* Scroll Down Prompt */}
          <ScrollReveal animation="fade-up" delayMs={450}>
            <div className="inline-flex flex-col items-center gap-2 text-slate-400 hover:text-white transition-colors cursor-pointer" onClick={() => scrollToId('crisis')}>
              <span className="text-xs font-mono tracking-widest uppercase">Scroll Down to Begin Presentation</span>
              <div className="w-6 h-10 rounded-full border-2 border-slate-600 flex items-start justify-center p-1.5">
                <div className="w-1.5 h-2.5 bg-sentry-cyan rounded-full animate-bounce" />
              </div>
            </div>
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 01: THE AGENTIC RELIABILITY CRISIS                            */}
      {/* ===================================================================== */}
      <section id="crisis" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-void relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-red mb-3">
              <span className="px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20">CHAPTER 01</span>
              <span>THE PRODUCTION BOTTLENECK</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              Why Autonomous Coding Agents <br />
              <span className="text-gradient">Fail Disastrously in Production.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-12 leading-relaxed">
              Autonomous agents (Devin, Claude Code, Cursor, SWE-bench workers) possess powerful tool-use capabilities. But when edge cases occur, multi-step compounding errors trigger unrecoverable failure spirals.
            </p>
          </ScrollReveal>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {[
              {
                icon: <Flame className="w-5 h-5 text-sentry-red" />,
                title: 'Catastrophic Wipes',
                desc: 'Agents issuing destructive commands like "rm -rf /" or dropping databases when attempting environment cleanup.',
                tag: 'Fatal Blast Radius'
              },
              {
                icon: <RefreshCw className="w-5 h-5 text-amber-400" />,
                title: 'Infinite Retry Loops',
                desc: 'Repeating identical broken build or test scripts 15+ times with zero parameter change, burning hundreds of API dollars.',
                tag: 'Stuck Drift'
              },
              {
                icon: <Lock className="w-5 h-5 text-sentry-violet" />,
                title: 'In-Flight Leaks',
                desc: 'Passing raw AWS secrets, database URIs, and corporate API keys directly into LLM prompts and unredacted logs.',
                tag: 'Data Leakage'
              },
              {
                icon: <AlertOctagon className="w-5 h-5 text-sentry-cyan" />,
                title: 'Tool Hallucinations',
                desc: 'Inventing fictitious tools (e.g. "magic_code_solver") and crashing multi-agent swarms with cascading unhandled exceptions.',
                tag: 'Protocol Drift'
              }
            ].map((trap, idx) => (
              <ScrollReveal key={idx} animation="fade-up" delayMs={idx * 100}>
                <div className="p-6 rounded-2xl glass-card border border-white/10 hover:border-sentry-cyan/30 transition-all flex flex-col justify-between h-full">
                  <div>
                    <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center mb-4">
                      {trap.icon}
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-300 border border-white/10">
                      {trap.tag}
                    </span>
                    <h3 className="font-display font-bold text-lg text-white mt-3 mb-2">{trap.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{trap.desc}</p>
                  </div>
                </div>
              </ScrollReveal>
            ))}
          </div>

          {/* The Heuristic Flaw Box */}
          <ScrollReveal animation="fade-up">
            <div className="p-6 sm:p-8 rounded-2xl bg-surface-1 border border-white/10 relative overflow-hidden">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div className="max-w-2xl">
                  <div className="inline-flex items-center gap-2 text-xs font-mono text-amber-400 mb-2">
                    <AlertTriangle className="w-4 h-4" />
                    <span>THE LIMITATION OF STATIC REGEX & PROMPT HEURISTICS</span>
                  </div>
                  <h4 className="font-display font-bold text-xl text-white mb-2">
                    Why Traditional Guardrails Break Down
                  </h4>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    Hardcoded regex either blocks legitimate developer actions (e.g. <code className="text-sentry-cyan font-mono">rm -rf dist/</code>) or misses subtle sequential drift where each step looks harmless in isolation, but cumulative repetition guarantees budget depletion. <span className="text-white font-medium">You need an intelligent tabular foundation model that understands sequential state.</span>
                  </p>
                </div>
                <div className="px-5 py-4 rounded-xl bg-black/60 border border-white/10 text-center shrink-0">
                  <div className="text-xs font-mono text-slate-400">Heuristic Recall</div>
                  <div className="text-3xl font-display font-bold text-sentry-red">54.4%</div>
                  <div className="text-[11px] font-mono text-slate-400 mt-1">Misses 45.6% of loops</div>
                </div>
              </div>
            </div>
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 02: PRIOR LABS TABPFN-3.5 DEEP DIVE                           */}
      {/* ===================================================================== */}
      <section id="tabpfn-foundation" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-surface-1/50 relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-cyan mb-3">
              <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">CHAPTER 02</span>
              <span>PRIOR LABS RESEARCH & ARCHITECTURAL FOUNDATION</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              TabPFN-3.5: In-Context Bayesian Intelligence <br />
              <span className="text-gradient">Why TabPFN is the Optimal Sentry Brain.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-12 leading-relaxed">
              Evaluating agent tool calls requires a mathematical paradigm shift. Agent telemetry is not independent static text—it is a continuous <strong>tabular temporal sequence</strong>.
            </p>
          </ScrollReveal>

          {/* Trilemma Comparison Grid: Why other methods fail vs TabPFN */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <ScrollReveal animation="fade-up" delayMs={100}>
              <div className="p-6 rounded-2xl glass-card border border-red-500/20 bg-red-500/5 h-full">
                <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
                  <XCircle className="w-5 h-5 text-sentry-red" />
                </div>
                <h3 className="font-display font-bold text-lg text-white mb-2">1. LLM-as-a-Judge</h3>
                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  Calling a secondary LLM to judge every tool call adds <strong>800–2000 ms of latency</strong>, doubles API billing, and introduces recursive hallucination risks.
                </p>
                <div className="p-2.5 rounded bg-black/60 font-mono text-[11px] text-red-400 border border-red-500/20">
                  ✗ Too slow for real-time sentry
                </div>
              </div>
            </ScrollReveal>

            <ScrollReveal animation="fade-up" delayMs={200}>
              <div className="p-6 rounded-2xl glass-card border border-amber-500/20 bg-amber-500/5 h-full">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-4">
                  <BarChart3 className="w-5 h-5 text-amber-400" />
                </div>
                <h3 className="font-display font-bold text-lg text-white mb-2">2. Classical Trees (XGBoost)</h3>
                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  Gradient boosted trees require expensive per-dataset training, hyperparameter tuning (`optuna`), and struggle with zero-shot domain shifts across new coding tasks.
                </p>
                <div className="p-2.5 rounded bg-black/60 font-mono text-[11px] text-amber-400 border border-amber-500/20">
                  ✗ Fails to adapt zero-shot
                </div>
              </div>
            </ScrollReveal>

            <ScrollReveal animation="fade-up" delayMs={300}>
              <div className="p-6 rounded-2xl glass-card border border-sentry-emerald/40 bg-emerald-500/5 h-full shadow-lg shadow-emerald-500/10">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4">
                  <CheckCircle2 className="w-5 h-5 text-sentry-emerald" />
                </div>
                <h3 className="font-display font-bold text-lg text-white mb-2">3. Prior Labs TabPFN-3.5</h3>
                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  Performs <strong>In-Context Bayesian Inference</strong> in a single forward pass (&lt;28 ms). Pretrained on millions of synthetic causal priors to learn tabular structure natively.
                </p>
                <div className="p-2.5 rounded bg-black/60 font-mono text-[11px] text-sentry-emerald border border-emerald-500/20">
                  ✓ 27.58 ms zero-shot Bayesian speed
                </div>
              </div>
            </ScrollReveal>
          </div>

          {/* Prior Labs Cookbook Alignment Details */}
          <ScrollReveal animation="fade-up">
            <div className="p-6 sm:p-8 rounded-2xl bg-surface-2 border border-white/10 mb-8">
              <h3 className="font-display font-bold text-xl text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-sentry-cyan" />
                <span>Prior Labs Cookbook & Technical Report Ingestion</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-slate-300 leading-relaxed">
                <div className="p-4 rounded-xl bg-black/60 border border-white/5 space-y-2">
                  <span className="text-sentry-cyan font-mono font-bold block text-sm">Recipe 1: Grouped Data Dynamics</span>
                  <p>
                    Following the Prior Labs cookbook, Agentry designates <code className="text-sentry-cyan font-mono">group_col="session_id"</code> and <code className="text-sentry-cyan font-mono">group_time_col="step_index"</code>. This models sequential trajectory progression without leaking przyszłe steps into train sets.
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-black/60 border border-white/5 space-y-2">
                  <span className="text-sentry-emerald font-mono font-bold block text-sm">Recipe 2: Thinking Mode & Calibrated Uncertainty</span>
                  <p>
                    TabPFN does not emit raw binary logits. It outputs full Bayesian posterior distributions with calibrated epistemic uncertainty bounds. If uncertainty is high, Agentry triggers <code className="text-blue-400 font-mono">PAUSE</code> for human review instead of prematurely killing good agents.
                  </p>
                </div>
              </div>
            </div>
          </ScrollReveal>

          {/* TabPFN Telemetry Feature Vector Interactive Viewer */}
          <ScrollReveal animation="fade-up">
            <div className="p-6 rounded-2xl bg-surface-2 border border-white/10">
              <h4 className="font-display font-bold text-base text-white mb-3 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-sentry-cyan" />
                <span>Extracted Tabular Feature Vector (Evaluated Pre-Execution in 27ms)</span>
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs">
                <div className="p-3 rounded-lg bg-black/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">FEATURE 01</span>
                  <span className="text-sentry-cyan font-bold">step_index</span>
                  <span className="text-slate-400 block text-[11px]">Sequential depth</span>
                </div>
                <div className="p-3 rounded-lg bg-black/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">FEATURE 02</span>
                  <span className="text-sentry-emerald font-bold">repetition_score</span>
                  <span className="text-slate-400 block text-[11px]">Levenshtein similarity</span>
                </div>
                <div className="p-3 rounded-lg bg-black/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">FEATURE 03</span>
                  <span className="text-amber-400 font-bold">error_streak</span>
                  <span className="text-slate-400 block text-[11px]">Consecutive failures</span>
                </div>
                <div className="p-3 rounded-lg bg-black/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">FEATURE 04</span>
                  <span className="text-sentry-violet font-bold">cumulative_cost</span>
                  <span className="text-slate-400 block text-[11px]">USD token burn</span>
                </div>
                <div className="p-3 rounded-lg bg-black/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">FEATURE 05</span>
                  <span className="text-blue-400 font-bold">thought_length</span>
                  <span className="text-slate-400 block text-[11px]">Reasoning token count</span>
                </div>
                <div className="p-3 rounded-lg bg-black/60 border border-white/5">
                  <span className="text-slate-500 block text-[10px]">FEATURE 06</span>
                  <span className="text-sentry-red font-bold">tool_category</span>
                  <span className="text-slate-400 block text-[11px]">Execution vs Read-only</span>
                </div>
              </div>
            </div>
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 03: DUAL-ENGINE ACTIVE DEFENSE ARCHITECTURE                   */}
      {/* ===================================================================== */}
      <section id="defense-architecture" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-void relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-emerald mb-3">
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">CHAPTER 03</span>
              <span>DEFENSE-IN-DEPTH ARCHITECTURE</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              Dual-Engine Safeguard Pipeline: <br />
              <span className="text-gradient">Bayesian Scoring + Deterministic Hard Stops.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-12 leading-relaxed">
              Agentry sits directly in front of agent tool execution. Every single tool call passes through a 4-tier inspection gate before the host OS or remote cloud provider ever executes the command.
            </p>
          </ScrollReveal>

          {/* Interactive Flow Stages */}
          <div className="relative mb-12">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative z-10">
              
              <ScrollReveal animation="fade-up" delayMs={100}>
                <div className="p-5 rounded-xl glass-card border border-white/10 h-full flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="w-7 h-7 rounded-lg bg-cyan-500/20 text-sentry-cyan font-mono text-xs flex items-center justify-center font-bold">01</span>
                      <Cable className="w-4 h-4 text-slate-400" />
                    </div>
                    <h3 className="font-display font-bold text-white text-base mb-1">In-Flight DLP</h3>
                    <p className="text-xs text-slate-400">
                      Redacts AWS tokens, OpenAI keys, and DB passwords from agent thoughts and payloads.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-sentry-cyan">
                    &lt; 2 ms regex masking
                  </div>
                </div>
              </ScrollReveal>

              <ScrollReveal animation="fade-up" delayMs={200}>
                <div className="p-5 rounded-xl glass-card border border-sentry-emerald/30 shadow-lg shadow-emerald-500/5 h-full flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="w-7 h-7 rounded-lg bg-emerald-500/20 text-sentry-emerald font-mono text-xs flex items-center justify-center font-bold">02</span>
                      <Activity className="w-4 h-4 text-sentry-emerald" />
                    </div>
                    <h3 className="font-display font-bold text-white text-base mb-1">TabPFN-3.5 Scoring</h3>
                    <p className="text-xs text-slate-400">
                      Evaluates sequential trajectory drift, repetition, error streaks, and predicts runaway cost risk.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-sentry-emerald">
                    27.58 ms Bayesian pass
                  </div>
                </div>
              </ScrollReveal>

              <ScrollReveal animation="fade-up" delayMs={300}>
                <div className="p-5 rounded-xl glass-card border border-white/10 h-full flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="w-7 h-7 rounded-lg bg-red-500/20 text-sentry-red font-mono text-xs flex items-center justify-center font-bold">03</span>
                      <ShieldAlert className="w-4 h-4 text-sentry-red" />
                    </div>
                    <h3 className="font-display font-bold text-white text-base mb-1">Blast-Radius Guard</h3>
                    <p className="text-xs text-slate-400">
                      Deterministic interceptor halting catastrophic filesystem deletions, fork bombs, and root wipes.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-sentry-red">
                    100% hard stop guarantee
                  </div>
                </div>
              </ScrollReveal>

              <ScrollReveal animation="fade-up" delayMs={400}>
                <div className="p-5 rounded-xl glass-card border border-white/10 h-full flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="w-7 h-7 rounded-lg bg-violet-500/20 text-sentry-violet font-mono text-xs flex items-center justify-center font-bold">04</span>
                      <Bot className="w-4 h-4 text-sentry-violet" />
                    </div>
                    <h3 className="font-display font-bold text-white text-base mb-1">Autonomic Actions</h3>
                    <p className="text-xs text-slate-400">
                      Orchestrates four autonomous decisions: PASS, REROUTE (steering prompt), PAUSE (HITL), or KILL.
                    </p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-sentry-violet">
                    Zero human bottleneck
                  </div>
                </div>
              </ScrollReveal>

            </div>
          </div>

          {/* Action Resolution Explainer */}
          <ScrollReveal animation="fade-up">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-slate-300">
                <span className="text-sentry-emerald font-bold text-sm block mb-1">PASS</span>
                Confidence nominal (&gt;75%). Tool executes transparently with zero delay.
              </div>
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-slate-300">
                <span className="text-amber-400 font-bold text-sm block mb-1">REROUTE</span>
                Injects autonomic context guidance to break repetitive diagnostic loops.
              </div>
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-slate-300">
                <span className="text-blue-400 font-bold text-sm block mb-1">PAUSE</span>
                Freezes agent execution and alerts Human-In-The-Loop review queue.
              </div>
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-slate-300">
                <span className="text-sentry-red font-bold text-sm block mb-1">KILL</span>
                Immediately terminates rogue worker and triggers automated git rollback.
              </div>
            </div>
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 04: VERIFIED EMPIRICAL BENCHMARK ARENA                        */}
      {/* ===================================================================== */}
      <section id="benchmark-arena" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-surface-1/40 relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-cyan mb-3">
              <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">CHAPTER 04</span>
              <span>RIGOROUS UNSEEN SWE-BENCH BENCHMARK</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              Verified Benchmark Arena: <br />
              <span className="text-gradient">TabPFN-3.5 Dominates Failure Recall.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-8 leading-relaxed">
              Evaluated on 17 unseen developer sessions using strict <code className="text-sentry-cyan font-mono text-sm">GroupShuffleSplit</code> on session ID with zero step-leakage. Honest, verified results from real Prior Labs evaluation.
            </p>
          </ScrollReveal>

          {/* Metric Selector Tabs */}
          <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
            {[
              { id: 'recall', label: 'Failure Recall (Primary Target)', desc: 'Ability to catch catastrophic failures' },
              { id: 'accuracy', label: 'Balanced Accuracy', desc: 'Accuracy across imbalanced classes' },
              { id: 'f1', label: 'Macro F1-Score', desc: 'Harmonic mean of precision and recall' },
              { id: 'latency', label: 'Inference Latency', desc: 'Runtime overhead per step' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setSelectedBenchmarkMetric(tab.id as any)}
                className={`px-4 py-2 rounded-xl text-xs font-mono transition-all whitespace-nowrap ${
                  selectedBenchmarkMetric === tab.id
                    ? 'bg-sentry-cyan text-void font-bold shadow-md'
                    : 'bg-surface-2 text-slate-400 hover:text-white border border-white/10'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Visual Benchmark Comparison Cards */}
          <ScrollReveal animation="fade-up">
            <div className="p-6 rounded-2xl glass-card border border-white/10 mb-8">
              <div className="space-y-4">
                
                {/* TabPFN-3.5 */}
                <div>
                  <div className="flex items-center justify-between text-xs font-mono mb-1">
                    <span className="text-white font-bold flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-sentry-emerald animate-pulse" />
                      TabPFN-3.5 (Prior Labs)
                    </span>
                    <span className="text-sentry-emerald font-bold text-sm">
                      {selectedBenchmarkMetric === 'recall' ? '91.7%' :
                       selectedBenchmarkMetric === 'accuracy' ? '60.1%' :
                       selectedBenchmarkMetric === 'f1' ? '58.7%' : '27.58 ms'}
                    </span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-black/60 overflow-hidden border border-white/10">
                    <div 
                      className="h-full bg-gradient-to-r from-sentry-cyan to-sentry-emerald rounded-full transition-all duration-700"
                      style={{ 
                        width: selectedBenchmarkMetric === 'recall' ? '91.7%' :
                               selectedBenchmarkMetric === 'accuracy' ? '60.1%' :
                               selectedBenchmarkMetric === 'f1' ? '58.7%' : '28%'
                      }}
                    />
                  </div>
                </div>

                {/* XGBoost */}
                <div>
                  <div className="flex items-center justify-between text-xs font-mono mb-1">
                    <span className="text-slate-300">XGBoost (100 estimators)</span>
                    <span className="text-slate-200">
                      {selectedBenchmarkMetric === 'recall' ? '82.2%' :
                       selectedBenchmarkMetric === 'accuracy' ? '55.9%' :
                       selectedBenchmarkMetric === 'f1' ? '52.4%' : '0.01 ms'}
                    </span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-black/60 overflow-hidden border border-white/5">
                    <div 
                      className="h-full bg-slate-400 rounded-full transition-all duration-700"
                      style={{ 
                        width: selectedBenchmarkMetric === 'recall' ? '82.2%' :
                               selectedBenchmarkMetric === 'accuracy' ? '55.9%' :
                               selectedBenchmarkMetric === 'f1' ? '52.4%' : '1%'
                      }}
                    />
                  </div>
                </div>

                {/* Random Forest */}
                <div>
                  <div className="flex items-center justify-between text-xs font-mono mb-1">
                    <span className="text-slate-300">Random Forest (100 trees)</span>
                    <span className="text-slate-200">
                      {selectedBenchmarkMetric === 'recall' ? '80.6%' :
                       selectedBenchmarkMetric === 'accuracy' ? '53.4%' :
                       selectedBenchmarkMetric === 'f1' ? '51.8%' : '0.04 ms'}
                    </span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-black/60 overflow-hidden border border-white/5">
                    <div 
                      className="h-full bg-slate-500 rounded-full transition-all duration-700"
                      style={{ 
                        width: selectedBenchmarkMetric === 'recall' ? '80.6%' :
                               selectedBenchmarkMetric === 'accuracy' ? '53.4%' :
                               selectedBenchmarkMetric === 'f1' ? '51.8%' : '1%'
                      }}
                    />
                  </div>
                </div>

                {/* Heuristic Baseline */}
                <div>
                  <div className="flex items-center justify-between text-xs font-mono mb-1">
                    <span className="text-slate-400">Heuristic Rule Baseline</span>
                    <span className="text-sentry-red">
                      {selectedBenchmarkMetric === 'recall' ? '54.4%' :
                       selectedBenchmarkMetric === 'accuracy' ? '39.0%' :
                       selectedBenchmarkMetric === 'f1' ? '39.0%' : '0.00 ms'}
                    </span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-black/60 overflow-hidden border border-white/5">
                    <div 
                      className="h-full bg-red-500/60 rounded-full transition-all duration-700"
                      style={{ 
                        width: selectedBenchmarkMetric === 'recall' ? '54.4%' :
                               selectedBenchmarkMetric === 'accuracy' ? '39.0%' :
                               selectedBenchmarkMetric === 'f1' ? '39.0%' : '1%'
                      }}
                    />
                  </div>
                </div>

              </div>
            </div>
          </ScrollReveal>

          {/* Full Benchmark Table */}
          <ScrollReveal animation="fade-up">
            <div className="overflow-x-auto rounded-2xl border border-white/10 bg-surface-1">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-white/5 text-slate-300 border-b border-white/10">
                  <tr>
                    <th className="py-3 px-4 font-semibold">Model Architecture</th>
                    <th className="py-3 px-4 font-semibold">Failure Recall</th>
                    <th className="py-3 px-4 font-semibold">Balanced Acc</th>
                    <th className="py-3 px-4 font-semibold">Macro F1</th>
                    <th className="py-3 px-4 font-semibold">ROC-AUC</th>
                    <th className="py-3 px-4 font-semibold">False-Stop Rate</th>
                    <th className="py-3 px-4 font-semibold">Inference Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-300">
                  <tr className="bg-emerald-500/5 text-white font-semibold">
                    <td className="py-3 px-4 flex items-center gap-2 text-sentry-emerald">
                      <ShieldCheck className="w-4 h-4" />
                      TabPFN-3.5 (Prior Labs)
                    </td>
                    <td className="py-3 px-4 text-sentry-emerald font-bold">91.7%</td>
                    <td className="py-3 px-4">60.1%</td>
                    <td className="py-3 px-4">58.7%</td>
                    <td className="py-3 px-4">0.882</td>
                    <td className="py-3 px-4 text-emerald-400">24.1%</td>
                    <td className="py-3 px-4 text-sentry-cyan">27.58 ms</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4">XGBoost (100 estimators)</td>
                    <td className="py-3 px-4">82.2%</td>
                    <td className="py-3 px-4">55.9%</td>
                    <td className="py-3 px-4">52.4%</td>
                    <td className="py-3 px-4">0.904</td>
                    <td className="py-3 px-4">29.2%</td>
                    <td className="py-3 px-4">0.01 ms</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4">Random Forest (100 trees)</td>
                    <td className="py-3 px-4">80.6%</td>
                    <td className="py-3 px-4">53.4%</td>
                    <td className="py-3 px-4">51.8%</td>
                    <td className="py-3 px-4">0.921</td>
                    <td className="py-3 px-4">25.9%</td>
                    <td className="py-3 px-4">0.04 ms</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 text-slate-400">Logistic Reg / Ridge</td>
                    <td className="py-3 px-4 text-slate-400">45.0%</td>
                    <td className="py-3 px-4 text-slate-400">33.0%</td>
                    <td className="py-3 px-4 text-slate-400">33.8%</td>
                    <td className="py-3 px-4 text-slate-400">0.808</td>
                    <td className="py-3 px-4 text-slate-400">28.3%</td>
                    <td className="py-3 px-4 text-slate-400">0.00 ms</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-4 text-slate-500">Heuristic Rule Baseline</td>
                    <td className="py-3 px-4 text-sentry-red">54.4%</td>
                    <td className="py-3 px-4 text-slate-500">39.0%</td>
                    <td className="py-3 px-4 text-slate-500">39.0%</td>
                    <td className="py-3 px-4 text-slate-500">0.619</td>
                    <td className="py-3 px-4 text-slate-500">17.4%</td>
                    <td className="py-3 px-4 text-slate-500">0.00 ms</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 05: VERIFIED PROOF GALLERY & REAL APPLICATION SCREENSHOTS     */}
      {/* ===================================================================== */}
      <section id="live-proof-gallery" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-void relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-emerald mb-3">
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">CHAPTER 05</span>
              <span>AUTHENTIC PROOF & PRODUCTION UI GALLERY</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              Verified Visual Proof: <br />
              <span className="text-gradient">Real Production Console Screenshots.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-8 leading-relaxed">
              These are <strong>genuine, full-resolution screenshots</strong> captured directly from our running local application daemon. Click any screenshot to open in high-resolution inspector mode.
            </p>
          </ScrollReveal>

          {/* Screenshot Category Selector */}
          <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
            <div className="flex items-center gap-2 overflow-x-auto pb-2">
              {REAL_SCREENSHOTS.map(ss => (
                <button
                  key={ss.id}
                  onClick={() => setActiveScreenTab(ss.id as any)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-mono transition-all whitespace-nowrap flex items-center gap-2 ${
                    activeScreenTab === ss.id
                      ? 'bg-surface-3 text-white border border-sentry-cyan/60 shadow-lg shadow-cyan-500/10 font-bold'
                      : 'bg-surface-1 text-slate-400 hover:text-white border border-white/10'
                  }`}
                >
                  <Eye className="w-3.5 h-3.5 text-sentry-cyan" />
                  <span>{ss.title}</span>
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-slate-400">View Mode:</span>
              <button
                onClick={() => setScreenshotMode('screenshot')}
                className={`px-3 py-1 rounded-lg border ${
                  screenshotMode === 'screenshot' 
                    ? 'bg-sentry-emerald/20 text-sentry-emerald border-emerald-500/40 font-bold' 
                    : 'bg-surface-2 text-slate-400 border-white/10'
                }`}
              >
                Full HD Screenshot
              </button>
              <button
                onClick={() => setScreenshotMode('interactive')}
                className={`px-3 py-1 rounded-lg border ${
                  screenshotMode === 'interactive' 
                    ? 'bg-sentry-cyan/20 text-sentry-cyan border-cyan-500/40 font-bold' 
                    : 'bg-surface-2 text-slate-400 border-white/10'
                }`}
              >
                Interactive DOM Mockup
              </button>
            </div>
          </div>

          {/* Active Screenshot Display Frame */}
          {(() => {
            const activeSS = REAL_SCREENSHOTS.find(s => s.id === activeScreenTab) || REAL_SCREENSHOTS[0];
            return (
              <ScrollReveal animation="fade-up">
                <div className="rounded-2xl border border-white/15 bg-surface-1 overflow-hidden shadow-2xl">
                  {/* Browser Mockup Chrome Header */}
                  <div className="px-4 py-3 bg-black/90 border-b border-white/10 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500/80" />
                      <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                      <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                      <span className="text-xs font-mono text-slate-400 ml-2">
                        http://localhost:3000/#{activeSS.id} — <span className="text-white font-semibold">{activeSS.title}</span>
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => setSelectedScreenshot(activeSS)}
                        className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-xs font-mono text-sentry-cyan border border-white/10"
                        title="Zoom in high resolution"
                      >
                        <ZoomIn className="w-3.5 h-3.5" />
                        <span>Inspect HD</span>
                      </button>

                      <button 
                        onClick={onLaunchConsole}
                        className="flex items-center gap-1 text-[11px] font-mono text-sentry-emerald hover:underline"
                      >
                        <span>Open Live View</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  {/* Mode 1: Real High-Res Screenshot Image */}
                  {screenshotMode === 'screenshot' && (
                    <div className="relative group cursor-zoom-in" onClick={() => setSelectedScreenshot(activeSS)}>
                      <img 
                        src={activeSS.src} 
                        alt={activeSS.title}
                        className="w-full h-auto object-cover max-h-[620px] transition-transform duration-300 group-hover:scale-[1.005]"
                      />
                      <div className="absolute bottom-4 left-4 right-4 p-4 rounded-xl bg-black/85 backdrop-blur-md border border-white/10 flex items-center justify-between text-xs font-mono">
                        <div>
                          <span className="text-sentry-cyan font-bold block mb-0.5">{activeSS.title}</span>
                          <span className="text-slate-300">{activeSS.desc}</span>
                        </div>
                        <div className="shrink-0 ml-4 hidden sm:block">
                          <span className="px-2 py-1 rounded bg-emerald-500/20 text-sentry-emerald border border-emerald-500/30 font-bold">
                            VERIFIED 1080P PROOF
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Mode 2: Interactive DOM Mockup */}
                  {screenshotMode === 'interactive' && (
                    <div className="p-6 space-y-6">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-4 rounded-xl bg-surface-2 border border-white/5">
                          <span className="text-[11px] font-mono text-slate-400 block mb-1">ACTIVE FLEET AGENTS</span>
                          <span className="text-2xl font-display font-bold text-white flex items-center gap-2">
                            <span>14 Workers</span>
                            <span className="w-2 h-2 rounded-full bg-sentry-emerald animate-pulse" />
                          </span>
                        </div>
                        <div className="p-4 rounded-xl bg-surface-2 border border-white/5">
                          <span className="text-[11px] font-mono text-slate-400 block mb-1">HAZARDS BLOCKED</span>
                          <span className="text-2xl font-display font-bold text-sentry-red">42 Stopped</span>
                        </div>
                        <div className="p-4 rounded-xl bg-surface-2 border border-white/5">
                          <span className="text-[11px] font-mono text-slate-400 block mb-1">BUDGET GUARDED</span>
                          <span className="text-2xl font-display font-bold text-sentry-emerald">$1,420.50</span>
                        </div>
                        <div className="p-4 rounded-xl bg-surface-2 border border-white/5">
                          <span className="text-[11px] font-mono text-slate-400 block mb-1">HITL ESCALATIONS</span>
                          <span className="text-2xl font-display font-bold text-amber-400">3 Pending</span>
                        </div>
                      </div>

                      <div className="p-4 rounded-xl bg-black/60 border border-white/5 font-mono text-xs space-y-3">
                        <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-white/10">
                          <span>LIVE AUDIT STREAM (WEBSOCKET CONNECTED)</span>
                          <span className="text-sentry-emerald">● LATENCY: 27.58ms</span>
                        </div>
                        <div className="flex items-center justify-between p-2 rounded bg-surface-2/60">
                          <div className="flex items-center gap-3">
                            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald font-bold">PASS</span>
                            <span className="text-white">agent-worker-09</span>
                            <span className="text-slate-400">git commit -m "fix regex boundary"</span>
                          </div>
                          <span className="text-slate-400">Risk: 0.05 | Blast: LOW</span>
                        </div>
                        <div className="flex items-center justify-between p-2 rounded bg-red-500/10 border border-red-500/20">
                          <div className="flex items-center gap-3">
                            <span className="px-2 py-0.5 rounded bg-red-500/20 text-sentry-red font-bold">KILL</span>
                            <span className="text-white">devops-autofix-02</span>
                            <span className="text-sentry-red font-semibold">rm -rf / --no-preserve-root</span>
                          </div>
                          <span className="text-sentry-red font-bold">BLAST HAZARD 1.00</span>
                        </div>
                      </div>
                    </div>
                  )}

                </div>
              </ScrollReveal>
            );
          })()}

          {/* Grid of all 6 Screenshots for instant clicking */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-6">
            {REAL_SCREENSHOTS.map(ss => (
              <div
                key={ss.id}
                onClick={() => {
                  setActiveScreenTab(ss.id as any);
                  setSelectedScreenshot(ss);
                }}
                className={`p-2 rounded-xl bg-surface-2 border transition-all cursor-pointer group hover:border-sentry-cyan ${
                  activeScreenTab === ss.id ? 'border-sentry-cyan/60 ring-2 ring-sentry-cyan/20' : 'border-white/10'
                }`}
              >
                <div className="rounded-lg overflow-hidden h-20 bg-black mb-2 relative">
                  <img 
                    src={ss.src} 
                    alt={ss.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform" 
                  />
                  <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors" />
                </div>
                <div className="text-[11px] font-bold text-white truncate font-display">{ss.title}</div>
                <div className="text-[10px] font-mono text-sentry-cyan">{ss.tag}</div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 06: 6 CURATED TOOL-CALL TRACES                                */}
      {/* ===================================================================== */}
      <section id="curated-traces" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-surface-1/30 relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-cyan mb-3">
              <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">CHAPTER 06</span>
              <span>VERIFIED TOOL-CALL AUDIT TRACES</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              6 Real-World Execution Scenarios: <br />
              <span className="text-gradient">PASS, KILL, and REROUTE in Action.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-8 leading-relaxed">
              Each scenario represents a real developer step audited end-to-end with Prior Labs TabPFN-3.5 foundation model scoring and blast-radius checks. Click each scenario to inspect the exact input, model inference, and autonomic resolution.
            </p>
          </ScrollReveal>

          {/* Trace Selector Pill Row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mb-6">
            {TRACES.map((trace, idx) => (
              <button
                key={trace.id}
                onClick={() => setSelectedTraceIndex(idx)}
                className={`p-3 rounded-xl text-left border transition-all ${
                  selectedTraceIndex === idx
                    ? 'bg-surface-3 border-sentry-cyan shadow-md text-white'
                    : 'bg-surface-1 border-white/10 text-slate-400 hover:text-white hover:bg-surface-2'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-mono">{trace.id}</span>
                  <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${trace.badgeColor}`}>
                    {trace.action}
                  </span>
                </div>
                <div className="text-xs font-semibold truncate">{trace.title}</div>
              </button>
            ))}
          </div>

          {/* Active Trace Inspector Card */}
          <ScrollReveal animation="fade-up">
            {(() => {
              const trace = TRACES[selectedTraceIndex];
              return (
                <div className="p-6 sm:p-8 rounded-2xl glass-card border border-white/10">
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-white/10 mb-6">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono text-sentry-cyan">{trace.id}</span>
                        <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded border ${trace.badgeColor}`}>
                          {trace.action} ACTION
                        </span>
                      </div>
                      <h3 className="font-display font-bold text-2xl text-white">{trace.title}</h3>
                      <p className="text-xs font-mono text-slate-400 mt-1">
                        Agent: <span className="text-white">{trace.agent}</span> • Tool: <span className="text-sentry-cyan">{trace.tool}</span>
                      </p>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right font-mono">
                        <span className="text-[10px] text-slate-400 block">CONFIDENCE</span>
                        <span className="text-base font-bold text-white">{trace.confidence}</span>
                      </div>
                      <div className="text-right font-mono">
                        <span className="text-[10px] text-slate-400 block">BLAST HAZARD</span>
                        <span className="text-base font-bold text-white">{trace.hazard}</span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    {/* Left: Input & Thought */}
                    <div className="space-y-4">
                      <div>
                        <span className="text-xs font-mono text-slate-400 block mb-1.5 flex items-center gap-1.5">
                          <Code2 className="w-3.5 h-3.5 text-sentry-cyan" />
                          <span>TOOL INPUT PAYLOAD / COMMAND:</span>
                        </span>
                        <pre className="p-3.5 rounded-xl bg-black/80 border border-white/5 font-mono text-xs text-sentry-cyan overflow-x-auto">
                          {trace.command}
                        </pre>
                      </div>

                      <div>
                        <span className="text-xs font-mono text-slate-400 block mb-1.5 flex items-center gap-1.5">
                          <Bot className="w-3.5 h-3.5 text-sentry-violet" />
                          <span>AGENT THOUGHT TRACE:</span>
                        </span>
                        <p className="p-3.5 rounded-xl bg-black/50 border border-white/5 text-xs text-slate-300 italic">
                          "{trace.thought}"
                        </p>
                      </div>
                    </div>

                    {/* Right: TabPFN Evaluation & Resolution */}
                    <div className="space-y-4">
                      <div className="p-4 rounded-xl bg-surface-2 border border-white/5">
                        <span className="text-xs font-mono text-slate-400 block mb-2 flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-sentry-emerald" />
                          <span>TABPFN-3.5 ASSESSMENT:</span>
                        </span>
                        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                          <div>
                            <span className="text-slate-500 block text-[10px]">RISK EVALUATION</span>
                            <span className="text-white font-bold">{trace.risk}</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block text-[10px]">BLAST SEVERITY</span>
                            <span className="text-white font-bold">{trace.hazard}</span>
                          </div>
                        </div>
                      </div>

                      <div className="p-4 rounded-xl bg-surface-2 border border-white/5">
                        <span className="text-xs font-mono text-slate-400 block mb-2 flex items-center gap-1.5">
                          <ShieldCheck className="w-3.5 h-3.5 text-sentry-cyan" />
                          <span>AUTONOMIC RESOLUTION:</span>
                        </span>
                        <p className="text-xs text-slate-300 leading-relaxed font-mono">
                          {trace.explanation}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 07: LIVE MOTION DESIGN TELEMETRY SIMULATOR                    */}
      {/* ===================================================================== */}
      <section id="motion-engine" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-void relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-violet mb-3">
              <span className="px-2 py-0.5 rounded bg-violet-500/10 border border-violet-500/20">CHAPTER 07</span>
              <span>LIVE MOTION DESIGN TELEMETRY ENGINE</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              Interactive Motion Design: <br />
              <span className="text-gradient">Real-Time Bayesian Trajectory Simulator.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-8 leading-relaxed">
              Experience the power of motion design directly. Adjust parameters or hit <strong>Play Motion</strong> to watch TabPFN calculate Bayesian posterior probabilities, reshape risk distributions, and trigger autonomic interventions in real-time.
            </p>
          </ScrollReveal>

          {/* Interactive Motion Console */}
          <ScrollReveal animation="fade-up">
            <div className="p-6 sm:p-8 rounded-2xl glass-card border border-white/15 shadow-2xl relative overflow-hidden">
              
              {/* Top Motion Controls */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-white/10 mb-6">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-sentry-emerald animate-ping" />
                    <span className="font-display font-bold text-xl text-white">Sequential Step {motionStep} of 8</span>
                    <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${currentSim.bg} ${currentSim.color}`}>
                      {currentSim.action}
                    </span>
                  </div>
                  <p className="text-xs font-mono text-slate-400 mt-1">
                    Simulating live agent tool calls through TabPFN In-Context Bayesian Inference
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setMotionPlaying(!motionPlaying)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
                      motionPlaying 
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 animate-pulse' 
                        : 'bg-gradient-to-r from-sentry-cyan to-sentry-emerald text-void glow-cyan hover:scale-[1.02]'
                    }`}
                  >
                    {motionPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    <span>{motionPlaying ? 'Pause Simulation' : 'Play Motion Simulation'}</span>
                  </button>

                  <button
                    onClick={() => {
                      setMotionPlaying(false);
                      setMotionStep(1);
                      setMotionRepetition(0.05);
                      setMotionErrorStreak(0);
                      setMotionCost(0.012);
                    }}
                    className="p-2 rounded-xl bg-surface-2 hover:bg-surface-3 border border-white/10 text-slate-300 hover:text-white"
                    title="Reset to Step 1"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Center: Live Bayesian Probability Waveform & Radar HUD */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                
                {/* Visual SVG Waveform Curve */}
                <div className="lg:col-span-2 p-5 rounded-xl bg-black/80 border border-white/10 flex flex-col justify-between">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                    <span>BAYESIAN POSTERIOR PROBABILITY CURVE P(FAILURE)</span>
                    <span className={currentSim.color}>P(Risk) = {(currentSim.score * 100).toFixed(1)}%</span>
                  </div>

                  {/* Dynamic SVG Waveform Animation */}
                  <div className="h-44 w-full relative flex items-center justify-center">
                    <svg className="w-full h-full overflow-visible" viewBox="0 0 500 150">
                      {/* Grid background lines */}
                      <line x1="0" y1="30" x2="500" y2="30" stroke="rgba(255,255,255,0.05)" strokeDasharray="4" />
                      <line x1="0" y1="75" x2="500" y2="75" stroke="rgba(255,255,255,0.05)" strokeDasharray="4" />
                      <line x1="0" y1="120" x2="500" y2="120" stroke="rgba(255,255,255,0.05)" strokeDasharray="4" />

                      {/* Threshold Line at 0.70 */}
                      <line x1="0" y1="45" x2="500" y2="45" stroke="rgba(239,68,68,0.3)" strokeDasharray="2" />
                      <text x="440" y="40" fill="rgba(239,68,68,0.7)" fontSize="9" fontFamily="monospace">KILL (0.70)</text>

                      {/* Threshold Line at 0.45 */}
                      <line x1="0" y1="82" x2="500" y2="82" stroke="rgba(245,158,11,0.3)" strokeDasharray="2" />
                      <text x="420" y="78" fill="rgba(245,158,11,0.7)" fontSize="9" fontFamily="monospace">REROUTE (0.45)</text>

                      {/* Area Fill Gradient under the Curve */}
                      <defs>
                        <linearGradient id="waveGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                          <stop offset="0%" stopColor={currentSim.score > 0.65 ? '#EF4444' : currentSim.score > 0.40 ? '#F59E0B' : '#00FF87'} stopOpacity="0.4" />
                          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
                        </linearGradient>
                      </defs>

                      {/* Dynamic Bezier Curve representing TabPFN Posterior */}
                      <path 
                        d={`M 0,140 Q ${150 + motionStep * 20},${140 - currentSim.score * 120} ${250 + motionStep * 15},${130 - currentSim.score * 110} T 500,${140 - currentSim.score * 90}`} 
                        fill="none" 
                        stroke={currentSim.score > 0.65 ? '#EF4444' : currentSim.score > 0.40 ? '#F59E0B' : '#00FF87'} 
                        strokeWidth="3.5"
                        className="transition-all duration-500 ease-out"
                      />
                      <path 
                        d={`M 0,140 Q ${150 + motionStep * 20},${140 - currentSim.score * 120} ${250 + motionStep * 15},${130 - currentSim.score * 110} T 500,${140 - currentSim.score * 90} L 500,150 L 0,150 Z`} 
                        fill="url(#waveGradient)" 
                        className="transition-all duration-500 ease-out"
                      />

                      {/* Current Agent Position Particle */}
                      <circle 
                        cx={Math.min(480, 50 + motionStep * 55)} 
                        cy={140 - currentSim.score * 115} 
                        r="7" 
                        fill={currentSim.score > 0.65 ? '#EF4444' : currentSim.score > 0.40 ? '#F59E0B' : '#00FF87'}
                        className="animate-pulse"
                      />
                      <circle 
                        cx={Math.min(480, 50 + motionStep * 55)} 
                        cy={140 - currentSim.score * 115} 
                        r="14" 
                        fill="none"
                        stroke={currentSim.score > 0.65 ? '#EF4444' : currentSim.score > 0.40 ? '#F59E0B' : '#00FF87'}
                        strokeWidth="1.5"
                        opacity="0.4"
                        className="animate-ping"
                      />
                    </svg>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-white/5">
                    <span>STEP 1: INCEPTION</span>
                    <span>STEP 4: DRIFT OCCURS</span>
                    <span>STEP 8: RECOVERY / KILL</span>
                  </div>
                </div>

                {/* Right: Autonomic Verdict HUD */}
                <div className="p-5 rounded-xl bg-surface-2 border border-white/10 flex flex-col justify-between">
                  <div>
                    <span className="text-[11px] font-mono text-slate-400 block mb-1">AUTONOMIC DECISION</span>
                    <div className="text-3xl font-display font-extrabold text-white flex items-center gap-2 mb-2">
                      <span className={currentSim.color}>{currentSim.action}</span>
                    </div>
                    <p className="text-xs font-mono text-slate-300 leading-relaxed mb-4">
                      {currentSim.desc}
                    </p>
                  </div>

                  <div className="space-y-2 pt-3 border-t border-white/5 font-mono text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Bayesian Confidence:</span>
                      <span className="text-white font-bold">{Math.min(99, Math.round(75 + currentSim.score * 20))}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Cumulative Cost Burn:</span>
                      <span className="text-sentry-emerald font-bold">${motionCost.toFixed(4)} USD</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Inference Latency:</span>
                      <span className="text-sentry-cyan font-bold">27.58 ms</span>
                    </div>
                  </div>
                </div>

              </div>

              {/* Bottom: Interactive Parameter Sliders */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-4 rounded-xl bg-black/60 border border-white/5 font-mono text-xs">
                
                {/* Repetition Score Slider */}
                <div>
                  <div className="flex justify-between mb-1.5">
                    <span className="text-slate-300">Repetition Score (Levenshtein):</span>
                    <span className="text-sentry-cyan font-bold">{(motionRepetition * 100).toFixed(0)}%</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="1" 
                    step="0.02" 
                    value={motionRepetition}
                    onChange={e => setMotionRepetition(parseFloat(e.target.value))}
                    className="w-full accent-sentry-cyan cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-500 block mt-1">Measures command loop similarity</span>
                </div>

                {/* Error Streak Slider */}
                <div>
                  <div className="flex justify-between mb-1.5">
                    <span className="text-slate-300">Consecutive Error Streak:</span>
                    <span className="text-amber-400 font-bold">{motionErrorStreak} fails</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="6" 
                    step="1" 
                    value={motionErrorStreak}
                    onChange={e => setMotionErrorStreak(parseInt(e.target.value))}
                    className="w-full accent-amber-400 cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-500 block mt-1">Uninterrupted failed tool calls</span>
                </div>

                {/* Step Depth */}
                <div>
                  <div className="flex justify-between mb-1.5">
                    <span className="text-slate-300">Step Index (Sequential Depth):</span>
                    <span className="text-sentry-violet font-bold">Step {motionStep}</span>
                  </div>
                  <input 
                    type="range" 
                    min="1" 
                    max="8" 
                    step="1" 
                    value={motionStep}
                    onChange={e => setMotionStep(parseInt(e.target.value))}
                    className="w-full accent-sentry-violet cursor-pointer"
                  />
                  <span className="text-[10px] text-slate-500 block mt-1">Grouped trajectory position</span>
                </div>

              </div>

            </div>
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 08: STEP-BY-STEP INSTALLATION & RUN GUIDE                    */}
      {/* ===================================================================== */}
      <section id="install-playbook" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-void relative">
        <div className="max-w-6xl mx-auto">
          
          <ScrollReveal animation="fade-up">
            <div className="flex items-center gap-2 text-xs font-mono text-sentry-emerald mb-3">
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">CHAPTER 08</span>
              <span>DEPLOYMENT & GETTING STARTED</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              How to Install and Run Agentry: <br />
              <span className="text-gradient">Zero Code Changes. 5-Minute Setup.</span>
            </h2>
            <p className="text-slate-400 max-w-3xl text-base sm:text-lg mb-8 leading-relaxed">
              Agentry integrates transparently into your existing developer setup via Model Context Protocol (MCP), Python SDK, OpenAI Reverse Proxy, or standalone Docker Compose.
            </p>
          </ScrollReveal>

          {/* Install Tabs */}
          <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
            {[
              { id: 'oneclick', label: '1. One-Click Quickstart (start.bat)' },
              { id: 'cli', label: '2. Python CLI & FastAPI Daemon' },
              { id: 'docker', label: '3. Docker Compose Stack' },
              { id: 'mcp', label: '4. Claude Desktop & Cursor MCP' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveInstallTab(tab.id as any)}
                className={`px-4 py-2.5 rounded-xl text-xs font-mono transition-all whitespace-nowrap ${
                  activeInstallTab === tab.id
                    ? 'bg-sentry-cyan text-void font-bold shadow-md'
                    : 'bg-surface-2 text-slate-400 hover:text-white border border-white/10'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Interactive Install Terminal */}
          <ScrollReveal animation="fade-up">
            <div className="p-6 sm:p-8 rounded-2xl glass-card border border-white/10 relative">
              
              {/* Option 1: One-Click */}
              {activeInstallTab === 'oneclick' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-sentry-emerald">LAUNCH BOTH BACKEND & FRONTEND WITH ONE COMMAND:</span>
                    <button 
                      onClick={() => copyToClipboard('.\\start.bat', 'oneclick')}
                      className="flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-white px-3 py-1 rounded bg-white/5 border border-white/10"
                    >
                      {copiedKey === 'oneclick' ? <Check className="w-3.5 h-3.5 text-sentry-emerald" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedKey === 'oneclick' ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <pre className="p-4 rounded-xl bg-black/90 font-mono text-xs text-sentry-cyan border border-white/5 overflow-x-auto leading-relaxed">
{`# Windows PowerShell / CMD:
.\\start.bat

# Linux / macOS:
bash start.sh`}
                  </pre>
                  <p className="text-xs text-slate-400 font-mono">
                    Automatically verifies Python virtual environment, boots the FastAPI daemon on <code className="text-white">http://127.0.0.1:8000</code>, and launches the Vite Cyber-Sentry UI on <code className="text-white">http://localhost:3000</code>.
                  </p>
                </div>
              )}

              {/* Option 2: CLI */}
              {activeInstallTab === 'cli' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-sentry-emerald">STEP-BY-STEP PYTHON CLI COMMANDS:</span>
                    <button 
                      onClick={() => copyToClipboard('pip install -e .\npython run.py doctor\npython run.py serve --port 8000', 'cli')}
                      className="flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-white px-3 py-1 rounded bg-white/5 border border-white/10"
                    >
                      {copiedKey === 'cli' ? <Check className="w-3.5 h-3.5 text-sentry-emerald" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedKey === 'cli' ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <pre className="p-4 rounded-xl bg-black/90 font-mono text-xs text-sentry-cyan border border-white/5 overflow-x-auto leading-relaxed">
{`# 1. Install dependencies
pip install -e .

# 2. Configure Prior Labs API Token (Optional, falls back to scikit-learn)
set TABPFN_TOKEN="your-prior-labs-token"

# 3. Run environment doctor diagnostics
python run.py doctor

# 4. Start the Agentry daemon & OpenAI Reverse Proxy
python run.py serve --port 8000

# 5. Run the live SWE-bench benchmark
python run.py benchmark`}
                  </pre>
                </div>
              )}

              {/* Option 3: Docker */}
              {activeInstallTab === 'docker' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-sentry-emerald">STANDALONE DOCKER COMPOSE DEPLOYMENT:</span>
                    <button 
                      onClick={() => copyToClipboard('docker-compose up --build -d', 'docker')}
                      className="flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-white px-3 py-1 rounded bg-white/5 border border-white/10"
                    >
                      {copiedKey === 'docker' ? <Check className="w-3.5 h-3.5 text-sentry-emerald" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedKey === 'docker' ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <pre className="p-4 rounded-xl bg-black/90 font-mono text-xs text-sentry-cyan border border-white/5 overflow-x-auto leading-relaxed">
{`# Spin up daemon, frontend, and reverse proxy in isolated containers
TABPFN_TOKEN="your-token" docker-compose up --build -d

# Verify container health
docker-compose ps`}
                  </pre>
                </div>
              )}

              {/* Option 4: MCP */}
              {activeInstallTab === 'mcp' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-sentry-emerald">MODEL CONTEXT PROTOCOL CONFIG (CLAUDE DESKTOP / CURSOR):</span>
                    <button 
                      onClick={() => copyToClipboard(`{
  "mcpServers": {
    "agentry": {
      "command": "python",
      "args": ["-m", "agentry.mcp_server"],
      "env": {
        "TABPFN_TOKEN": "your-prior-labs-token"
      }
    }
  }
}`, 'mcp')}
                      className="flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-white px-3 py-1 rounded bg-white/5 border border-white/10"
                    >
                      {copiedKey === 'mcp' ? <Check className="w-3.5 h-3.5 text-sentry-emerald" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedKey === 'mcp' ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <pre className="p-4 rounded-xl bg-black/90 font-mono text-xs text-sentry-violet border border-white/5 overflow-x-auto leading-relaxed">
{`// Add to claude_desktop_config.json or .cursor/mcp.json:
{
  "mcpServers": {
    "agentry": {
      "command": "python",
      "args": ["-m", "agentry.mcp_server"],
      "env": {
        "TABPFN_TOKEN": "your-prior-labs-token"
      }
    }
  }
}`}
                  </pre>
                  <p className="text-xs text-slate-400 font-mono">
                    Provides 12 native MCP tools including <code className="text-white">agentry_audit_step</code>, <code className="text-white">agentry_evaluate_blast_radius</code>, and <code className="text-white">agentry_redact_secrets</code> directly into AI agent context.
                  </p>
                </div>
              )}

            </div>
          </ScrollReveal>

        </div>
      </section>

      {/* ===================================================================== */}
      {/* CHAPTER 09: CALL TO ACTION & FLEET COMMAND                           */}
      {/* ===================================================================== */}
      <section id="cta" className="py-24 px-4 lg:px-8 border-t border-white/10 bg-void relative text-center">
        <div className="max-w-4xl mx-auto">
          
          <ScrollReveal animation="fade-down">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-sentry-cyan via-emerald-500 to-sentry-emerald p-0.5 glow-cyan mx-auto mb-6">
              <div className="w-full h-full bg-void rounded-[14px] flex items-center justify-center">
                <ShieldCheck className="w-8 h-8 text-sentry-cyan" />
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal animation="fade-up" delayMs={100}>
            <h2 className="text-3xl sm:text-5xl font-display font-extrabold text-white mb-6">
              Ready to Guard Your Autonomous Fleets?
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto text-base sm:text-lg mb-10 leading-relaxed">
              Prior Labs TabPFN-3.5 foundation model scoring is available now. Experience real-time Bayesian fleet defense in your terminal or browser.
            </p>
          </ScrollReveal>

          <ScrollReveal animation="zoom-in" delayMs={200}>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <button
                onClick={onLaunchConsole}
                className="flex items-center gap-2.5 px-8 py-4 rounded-xl bg-gradient-to-r from-sentry-cyan via-emerald-400 to-sentry-emerald text-void font-bold text-sm tracking-wide glow-cyan hover:scale-[1.03] transition-all"
              >
                <Terminal className="w-4 h-4" />
                <span>ENTER MISSION CONTROL</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={onExitDeck}
                className="flex items-center gap-2 px-6 py-4 rounded-xl glass-card hover:bg-surface-2 border border-white/10 text-white font-semibold text-sm transition-all"
              >
                <ShieldAlert className="w-4 h-4 text-sentry-cyan" />
                <span>Back to Showcase</span>
              </button>

              <a
                href="https://github.com/IrrhammCode/agentry"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-6 py-4 rounded-xl glass-card hover:bg-surface-2 border border-white/10 text-white font-semibold text-sm transition-all"
              >
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
                <span>Star on GitHub</span>
              </a>
            </div>
          </ScrollReveal>

          <div className="mt-16 pt-8 border-t border-white/10 text-xs font-mono text-slate-500">
            Agentry © 2026 • Prior Labs TabPFN-3.5 Global Hackathon Defense Track • Apache 2.0 Open Source
          </div>

        </div>
      </section>

    </div>
  );
};
