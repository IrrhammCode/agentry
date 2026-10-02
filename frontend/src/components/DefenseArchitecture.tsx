import React, { useState } from 'react';
import { 
  Layers, 
  ShieldCheck, 
  Cpu, 
  History, 
  ArrowRight, 
  CheckCircle, 
  AlertTriangle, 
  Lock, 
  Sparkles,
  Zap,
  Terminal,
  RotateCcw,
  ShieldAlert,
  Search,
  Timer
} from 'lucide-react';

interface LayerDetail {
  id: number;
  label: string;
  badge: string;
  badgeColor: string;
  analogy: string;
  analogyIcon: 'shield' | 'brain' | 'clock';
  title: string;
  subtitle: string;
  description: string;
  howItWorks: string[];
  techStack: string[];
  visualMetric: { label: string; value: string };
}

const LAYERS: LayerDetail[] = [
  {
    id: 1,
    label: 'LAYER 1',
    badge: 'INSTANT FILTER (<1ms)',
    badgeColor: 'bg-sentry-cyan/20 text-sentry-cyan border-sentry-cyan/30',
    analogy: 'Front Door Sentry',
    analogyIcon: 'shield',
    title: 'In-Flight Pre-Execution Interception',
    subtitle: 'Deterministic semantic sandbox & data loss prevention executed before shell spawn',
    description: 'Just like a physical security gate at an airport, Layer 1 inspects incoming commands and outbound payloads deterministically before they execute. Destructive shell actions (like rm -rf or DROP DATABASE) and credential leaks (OpenAI tokens, AWS keys) are blocked in under 1 millisecond before the OS shell ever spawns.',
    howItWorks: [
      'Semantic AST & Blast Radius syntax check prior to OS shell execution',
      'In-flight high-entropy secret masking (DLP: AWS, SSH, OpenAI, DB credentials)',
      'Cyclic ping-pong swarm deadlock detection between multi-agent peers'
    ],
    techStack: ['Semantic AST Parser', 'High-Entropy Regex DLP', 'Deterministic Filter'],
    visualMetric: { label: 'Filter Speed', value: '< 0.8 ms' }
  },
  {
    id: 2,
    label: 'LAYER 2',
    badge: 'CORE TABPFN-3.5 BRAIN',
    badgeColor: 'bg-emerald-500/20 text-sentry-emerald border-emerald-500/30 glow-emerald',
    analogy: 'Tabular AI Detective',
    analogyIcon: 'brain',
    title: 'Prior Labs TabPFN-3.5 Tabular Intelligence',
    subtitle: 'Predicts agent anomalies and runaways in 14.8ms with zero prompt transmission',
    description: 'This is Agentry\'s secret weapon. Rather than relying on slow, expensive cloud LLMs that compromise data privacy, Agentry utilizes Prior Labs TabPFN-3.5 foundation model. TabPFN evaluates 16 numerical telemetry metrics (error streaks, repetition entropy, token burn rate, step velocity) to predict whether an agent is failing or trapped in an unproductive loop.',
    howItWorks: [
      'Bayesian in-context prior probability evaluation in 14.8ms (30x faster than an eye blink)',
      '100% Zero-Leakage Privacy: Your code and prompts never leave your local environment',
      '5-Mode Multiclass Failure Classification (Infinite Loop, Tool Hallucination, Cost Runaway, etc.)'
    ],
    techStack: ['TabPFN-3.5 Prior Labs', 'Bayesian In-Context', 'Thinking Mode (10k tokens)'],
    visualMetric: { label: 'Inference Latency', value: '14.8 ms' }
  },
  {
    id: 3,
    label: 'LAYER 3',
    badge: 'AUTONOMIC HEALER',
    badgeColor: 'bg-violet-500/20 text-sentry-violet border-violet-500/30',
    analogy: 'Autonomous Time Machine',
    analogyIcon: 'clock',
    title: 'Closed-Loop Autonomic Self-Healing',
    subtitle: 'Rewinds physical disk state, prunes poisoned memory, and guides rogue agents',
    description: 'When an agent spirals into repeated errors, Agentry does more than just kill it — the system automatically rolls back the filesystem to the last known healthy snapshot, prunes hallucinated turns from the agent\'s memory context, and injects counterfactual steering directives so the agent resumes on a healthy trajectory.',
    howItWorks: [
      'Physical Snapshot Rollback: Restores damaged codebase files to a clean checkpoint',
      'Context Memory Pruning: Strips out repetitive error loops that poison LLM attention',
      'Autonomic Steering Injection: Dispatches corrective directives so agents self-correct and converge'
    ],
    techStack: ['Filesystem Snapshot Engine', 'LLM Trajectory Pruner', 'Autonomic Steering'],
    visualMetric: { label: 'E2E Recovery Rate', value: '100% E2E' }
  }
];

export const DefenseArchitecture: React.FC = () => {
  const [activeLayerId, setActiveLayerId] = useState<number>(2);
  const currentLayer = LAYERS.find(l => l.id === activeLayerId) || LAYERS[1];

  const renderAnalogyIcon = (icon: 'shield' | 'brain' | 'clock') => {
    switch (icon) {
      case 'shield': return <ShieldCheck className="w-4 h-4 text-sentry-cyan" />;
      case 'brain': return <Cpu className="w-4 h-4 text-sentry-emerald" />;
      case 'clock': return <History className="w-4 h-4 text-sentry-violet" />;
    }
  };

  return (
    <section id="architecture" className="py-20 px-4 lg:px-8 border-y border-white/10 bg-surface-1/30 relative">
      <div className="max-w-6xl mx-auto">
        
        {/* Section Header */}
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sentry-emerald/10 border border-sentry-emerald/30 text-sentry-emerald text-xs font-mono font-medium mb-3 animate-pulse-glow">
            <Layers className="w-3.5 h-3.5" />
            <span>DEFENSE-IN-DEPTH ARCHITECTURE</span>
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-display font-bold text-white mb-3">
            <span className="animate-text-shimmer">The 3-Layer Defense-in-Depth Architecture</span>
          </h2>
          <p className="text-slate-300 max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
            Click each layer below to inspect how deterministic zero-latency interceptors, Prior Labs <span className="text-sentry-emerald font-semibold">TabPFN-3.5</span> foundation model, and autonomic self-healing work together to safeguard your agent fleet.
          </p>
        </div>

        {/* ================================================================= */}
        {/* INTERACTIVE 3-TIER LAYER TABS                                     */}
        {/* ================================================================= */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {LAYERS.map((layer) => {
            const isSelected = activeLayerId === layer.id;
            return (
              <button
                key={layer.id}
                onClick={() => setActiveLayerId(layer.id)}
                className={`p-5 rounded-2xl text-left border transition-all duration-300 relative overflow-hidden group ${
                  isSelected
                    ? 'bg-surface-2 border-sentry-emerald shadow-xl glow-emerald scale-[1.02]'
                    : 'glass-card hover:bg-surface-2/80 border-white/10 hover:border-white/20 hover:-translate-y-0.5'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-mono text-xs font-bold text-slate-400 group-hover:text-white transition-colors">
                    {layer.label}
                  </span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border font-bold ${layer.badgeColor}`}>
                    {layer.visualMetric.value}
                  </span>
                </div>

                <div className="text-sm font-mono text-sentry-cyan mb-1 flex items-center gap-1.5">
                  {renderAnalogyIcon(layer.analogyIcon)}
                  <span>"{layer.analogy}"</span>
                </div>

                <h3 className="text-base font-bold text-white mb-2 group-hover:text-sentry-emerald transition-colors">
                  {layer.title}
                </h3>

                <p className="text-xs text-slate-400 line-clamp-2">
                  {layer.subtitle}
                </p>

                {isSelected && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-sentry-cyan via-emerald-400 to-sentry-emerald" />
                )}
              </button>
            );
          })}
        </div>

        {/* ================================================================= */}
        {/* ANIMATED DETAILED BREAKDOWN OF ACTIVE LAYER                       */}
        {/* ================================================================= */}
        <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/15 bg-surface-1/70 shadow-2xl animate-fade-in relative overflow-hidden">
          
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-white/10">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-sentry-cyan mb-2">
                {renderAnalogyIcon(currentLayer.analogyIcon)}
                <span>{currentLayer.label} • {currentLayer.analogy}</span>
              </div>
              <h3 className="text-2xl sm:text-3xl font-display font-bold text-white mb-2">
                {currentLayer.title}
              </h3>
              <p className="text-sm text-sentry-emerald font-mono">
                {currentLayer.subtitle}
              </p>
            </div>

            <div className="flex items-center gap-4 bg-void/80 p-4 rounded-xl border border-white/10 font-mono">
              <div className="text-center px-3 border-r border-white/10">
                <div className="text-[10px] text-slate-400">{currentLayer.visualMetric.label.toUpperCase()}</div>
                <div className="text-xl font-bold text-sentry-emerald">{currentLayer.visualMetric.value}</div>
              </div>
              <div className="text-center px-3">
                <div className="text-[10px] text-slate-400">CIRCUIT STATUS</div>
                <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 justify-center">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  ARMED & ACTIVE
                </div>
              </div>
            </div>
          </div>

          {/* Description & Explanation */}
          <div className="py-6">
            <h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-2">
              How It Works (Plain English):
            </h4>
            <p className="text-sm sm:text-base text-slate-200 leading-relaxed bg-void/50 p-4 sm:p-5 rounded-xl border border-white/5">
              {currentLayer.description}
            </p>
          </div>

          {/* Core Capabilities & Technologies */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div>
              <h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-3">
                Core Capabilities:
              </h4>
              <div className="space-y-2.5">
                {currentLayer.howItWorks.map((item, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-300">
                    <CheckCircle className="w-4 h-4 text-sentry-emerald shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-3">
                Underlying Technologies:
              </h4>
              <div className="flex flex-wrap gap-2">
                {currentLayer.techStack.map((tech, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1.5 rounded-lg bg-surface-2 border border-white/10 text-xs font-mono text-sentry-cyan font-medium flex items-center gap-1.5"
                  >
                    <Zap className="w-3 h-3 text-sentry-emerald" />
                    <span>{tech}</span>
                  </span>
                ))}
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};
