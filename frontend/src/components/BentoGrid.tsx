import React from 'react';
import { Grid, Shuffle, Plug, UserCheck, History, Gauge, FileText } from 'lucide-react';

export const BentoGrid: React.FC = () => {
  return (
    <section className="py-20 px-4 lg:px-8 border-t border-white/10 bg-surface-1/40">
      <div className="max-w-6xl mx-auto">
        
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sentry-violet/10 border border-sentry-violet/30 text-sentry-violet text-xs font-mono font-medium mb-3">
            <Grid className="w-3.5 h-3.5" />
            <span>ENTERPRISE-GRADE CAPABILITIES</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-3">
            <span className="animate-text-shimmer">Built for Production Swarms and Coding Fleets</span>
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
            Everything your platform engineering team needs to govern autonomous agents at scale.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Bento 1 */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-cyan/30 transition-all flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-sentry-cyan/10 flex items-center justify-center text-sentry-cyan mb-4">
                <Shuffle className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">Zero-Code Reverse Proxy</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Drop-in replacement for OpenAI API. Just set <code className="text-sentry-cyan font-mono">base_url="http://localhost:8787/v1"</code> to automatically guard CrewAI, AutoGen, and LangChain.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-white/10 font-mono text-[11px] text-slate-500">
              HTTP Reverse Proxy • Port 8787
            </div>
          </div>

          {/* Bento 2 */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-emerald/30 transition-all flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-sentry-emerald/10 flex items-center justify-center text-sentry-emerald mb-4">
                <Plug className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">Native MCP Server</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                13 official Model Context Protocol tools and resources. Connect Cursor, Claude Desktop, or Windsurf directly to inspect health and run audits.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-white/10 font-mono text-[11px] text-slate-500">
              STDIO & SSE Transport Ready
            </div>
          </div>

          {/* Bento 3 */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-amber-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-400 mb-4">
                <UserCheck className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">HITL Operator War Room</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Escalates borderline decisions to human engineers. Resume, steer counterfactual directives, or abort with full execution context.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-white/10 font-mono text-[11px] text-slate-500">
              Webhooks & Slack/Discord Alerts
            </div>
          </div>

          {/* Bento 4 */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-violet/30 transition-all flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center text-sentry-violet mb-4">
                <History className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">Physical Disk Time-Machine</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Differential filesystem snapshots track workspace mutations. Reverts corrupted source files and deletes toxic files generated in failure loops.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-white/10 font-mono text-[11px] text-slate-500">
              Zero Git Clean Hacks
            </div>
          </div>

          {/* Bento 5 */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-red/30 transition-all flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center text-sentry-red mb-4">
                <Gauge className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">24h Fleet Budget Governor</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Prevents sudden credit card burn. Enforces rolling hourly token spend limits with automatic agent throttling and quarantine.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-white/10 font-mono text-[11px] text-slate-500">
              Configurable Daily Caps
            </div>
          </div>

          {/* Bento 6 */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-blue/30 transition-all flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-sentry-blue/10 flex items-center justify-center text-sentry-blue mb-4">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">Forensic Post-Mortems</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generate audit-ready incident reports in Markdown, HTML, and JSON-LD for compliance reviews and internal root cause analyses.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-white/10 font-mono text-[11px] text-slate-500">
              Export to Slack / Confluence
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};
