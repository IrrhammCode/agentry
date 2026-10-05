import React, { useState } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';
import { ScrollReveal } from './ScrollReveal.tsx';

const FAQS = [
  {
    q: 'Why use TabPFN instead of an LLM as a guardrail?',
    a: 'LLMs take 500ms to 3,000ms to respond, cost significant token fees, and suffer from prompt injection attacks. Prior Labs TabPFN-3.5 evaluates multivariate tabular telemetry in tens of milliseconds, protects internal codebases from prompt exposure, and provides calibrated Bayesian probabilities without LLM hallucinations.',
  },
  {
    q: 'Does Agentry send our proprietary code to the cloud?',
    a: 'Agentry operates primarily on structured tabular telemetry (token burn rate, error streaks, latency, repetition entropy, tool counts). In Cloud Mode, TabPFN-3.5 receives these metrics alongside short thought snippets for multimodal in-context evaluation. For strict air-gapped environments, setting TABPFN_OFFLINE_MODE=1 runs local HistGradientBoosting and local Ollama SLMs completely offline with zero outbound network transmission.',
  },
  {
    q: 'Can Agentry recover my agents automatically without human input?',
    a: 'Yes. Layer 3 Closed-Loop Autonomic Self-Healing identifies the exact inflection point (t*) where the trajectory began failing, rolls back the filesystem disk state, prunes poisoned prompt context turns, and injects a counterfactual steering directive.',
  },
  {
    q: 'How does Agentry integrate with existing agent frameworks?',
    a: 'Agentry provides 3 frictionless integration modes: (1) Zero-code HTTP reverse proxy compatible with OpenAI client format, (2) Python decorator @guard.protect for native tool methods, and (3) Native MCP Server for Cursor and Claude Desktop.',
  },
];

export const FaqSection: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggle = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <section className="py-20 px-4 lg:px-8 max-w-4xl mx-auto">
      {/* Header with ScrollReveal */}
      <ScrollReveal animation="fade-up" durationMs={800}>
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sentry-cyan/10 border border-sentry-cyan/30 text-sentry-cyan text-xs font-mono font-medium mb-3">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>CLARITY & ARCHITECTURE</span>
          </div>
          <h2 className="text-3xl font-display font-bold text-white mb-2">Frequently Asked Questions</h2>
          <p className="text-slate-400 text-sm">Everything you need to know about TabPFN-3.5 sentry governance.</p>
        </div>
      </ScrollReveal>

      {/* Accordion List with Staggered ScrollReveal */}
      <div className="space-y-4">
        {FAQS.map((faq, idx) => {
          const isOpen = openIndex === idx;
          return (
            <ScrollReveal 
              key={idx} 
              animation="fade-up" 
              delayMs={idx * 100} 
              durationMs={600}
            >
              <div
                className="glass-card rounded-xl p-5 border border-white/10 cursor-pointer transition-all hover:border-white/20"
                onClick={() => toggle(idx)}
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-white text-sm">{faq.q}</h4>
                  <ChevronDown
                    className={`w-4 h-4 text-slate-400 transition-transform ${
                      isOpen ? 'rotate-180' : ''
                    }`}
                  />
                </div>
                {isOpen && (
                  <div className="mt-3 pt-3 border-t border-white/10 text-xs text-slate-300 leading-relaxed">
                    {faq.a}
                  </div>
                )}
              </div>
            </ScrollReveal>
          );
        })}
      </div>
    </section>
  );
};
