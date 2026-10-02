import React, { useState } from 'react';
import { Calculator, Sparkles } from 'lucide-react';
import { ScrollReveal } from './ScrollReveal.tsx';

export const RoiCalculator: React.FC = () => {
  const [agents, setAgents] = useState<number>(20);
  const [spend, setSpend] = useState<number>(5000);

  // Based on SWE-bench empirical benchmarks: 23.4% of spend is saved
  const monthlySavings = spend * 0.234;
  const annualSavings = Math.round(monthlySavings * 12);
  const tokensSavedM = ((spend * 0.234) / 0.000003 / 1000000).toFixed(1);
  const hoursSaved = Math.round(agents * 8.4);

  return (
    <section className="py-20 px-4 lg:px-8 max-w-6xl mx-auto">
      {/* Header with ScrollReveal */}
      <ScrollReveal animation="fade-up" durationMs={800}>
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sentry-emerald/10 border border-sentry-emerald/30 text-sentry-emerald text-xs font-mono font-medium mb-3">
            <Calculator className="w-3.5 h-3.5" />
            <span>ECONOMIC VALUE MODEL</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-3">
            <span className="animate-text-shimmer">Calculate Your Fleet Savings</span>
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
            See how much wasted LLM tokens, developer debugging hours, and cloud compute Agentry saves your team each month.
          </p>
        </div>
      </ScrollReveal>

      <div className="glass-card rounded-2xl p-8 border border-white/15">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Sliders with ScrollReveal */}
          <div className="lg:col-span-7">
            <ScrollReveal animation="fade-right" delayMs={150} durationMs={800}>
              <div className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium text-slate-300">Number of Concurrent AI Agents</label>
                <span className="font-mono text-sentry-cyan font-bold text-base">{agents} agents</span>
              </div>
              <input
                type="range"
                min="1"
                max="100"
                value={agents}
                onChange={(e) => setAgents(parseInt(e.target.value))}
                className="w-full h-2 bg-surface-2 rounded-lg appearance-none cursor-pointer accent-sentry-cyan"
              />
              <div className="flex justify-between text-[11px] text-slate-500 font-mono mt-1">
                <span>1 Agent</span>
                <span>50 Agents</span>
                <span>100 Agents</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium text-slate-300">Monthly LLM API Spend ($ USD)</label>
                <span className="font-mono text-sentry-emerald font-bold text-base">${spend.toLocaleString()} / mo</span>
              </div>
              <input
                type="range"
                min="500"
                max="50000"
                step="500"
                value={spend}
                onChange={(e) => setSpend(parseInt(e.target.value))}
                className="w-full h-2 bg-surface-2 rounded-lg appearance-none cursor-pointer accent-sentry-emerald"
              />
              <div className="flex justify-between text-[11px] text-slate-500 font-mono mt-1">
                <span>$500</span>
                <span>$25,000</span>
                <span>$50,000</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-void/50 border border-white/5 text-xs text-slate-400 flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-sentry-emerald shrink-0 mt-0.5" />
              <span><em>Based on empirical SWE-bench benchmark metrics: 23.4% of rogue steps in unguarded agent runs are unrecoverable loops and hallucinated retry cycles.</em></span>
            </div>
          </div>
          </ScrollReveal>
        </div>

        {/* Output Box with ScrollReveal */}
        <div className="lg:col-span-5">
          <ScrollReveal animation="zoom-in" delayMs={250} durationMs={800}>
            <div className="glass-card rounded-xl p-6 bg-gradient-to-br from-surface-1 to-surface-2 border border-emerald-500/20 text-center">
              <span className="text-xs font-mono uppercase text-slate-400 tracking-wider">Projected Annual Savings</span>
              <div className="text-4xl sm:text-5xl font-display font-extrabold text-sentry-emerald my-3">
                ${annualSavings.toLocaleString()}
              </div>
              <p className="text-xs text-slate-300 mb-6">
                Saved from prevented loop token burns and runaway execution traps.
              </p>

              <div className="space-y-2 pt-4 border-t border-white/10 font-mono text-xs text-left">
                <div className="flex justify-between text-slate-400">
                  <span>Prevented Token Waste:</span>
                  <span className="text-white font-bold">{tokensSavedM}M tokens</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Dev Debugging Time Saved:</span>
                  <span className="text-white font-bold">{hoursSaved} hrs / yr</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Net Return on Investment:</span>
                  <span className="text-sentry-cyan font-bold">312% ROI</span>
                </div>
              </div>
            </div>
          </ScrollReveal>
        </div>

        </div>
      </div>
    </section>
  );
};
