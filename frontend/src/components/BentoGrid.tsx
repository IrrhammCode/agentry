import React from 'react';
import { Grid, Shuffle, Plug, UserCheck, History, Gauge, FileText } from 'lucide-react';
import { ScrollReveal } from './ScrollReveal.tsx';

const BENTO_ITEMS = [
  {
    icon: <Shuffle className="w-5 h-5 text-sentry-cyan" />,
    iconBg: 'bg-sentry-cyan/10',
    borderHover: 'hover:border-sentry-cyan/40',
    title: 'Zero-Code Reverse Proxy',
    desc: 'Drop-in replacement for OpenAI API. Just set base_url="http://localhost:8787/v1" to automatically guard CrewAI, AutoGen, and LangChain.',
    footer: 'HTTP Reverse Proxy • Port 8787'
  },
  {
    icon: <Plug className="w-5 h-5 text-sentry-emerald" />,
    iconBg: 'bg-sentry-emerald/10',
    borderHover: 'hover:border-sentry-emerald/40',
    title: 'Native MCP Server',
    desc: '13 official Model Context Protocol tools and resources. Connect Cursor, Claude Desktop, or Windsurf directly to inspect health and run audits.',
    footer: 'STDIO & SSE Transport Ready'
  },
  {
    icon: <UserCheck className="w-5 h-5 text-amber-400" />,
    iconBg: 'bg-amber-500/10',
    borderHover: 'hover:border-amber-500/40',
    title: 'HITL Operator War Room',
    desc: 'Escalates borderline decisions to human engineers. Resume, steer counterfactual directives, or abort with full execution context.',
    footer: 'Webhooks & Slack/Discord Alerts'
  },
  {
    icon: <History className="w-5 h-5 text-sentry-violet" />,
    iconBg: 'bg-violet-500/10',
    borderHover: 'hover:border-sentry-violet/40',
    title: 'Physical Disk Time-Machine',
    desc: 'Differential filesystem snapshots track workspace mutations. Reverts corrupted source files and deletes toxic files generated in failure loops.',
    footer: 'Zero Git Clean Hacks'
  },
  {
    icon: <Gauge className="w-5 h-5 text-sentry-red" />,
    iconBg: 'bg-red-500/10',
    borderHover: 'hover:border-sentry-red/40',
    title: '24h Fleet Budget Governor',
    desc: 'Prevents sudden credit card burn. Enforces rolling hourly token spend limits with automatic agent throttling and quarantine.',
    footer: 'Configurable Daily Caps'
  },
  {
    icon: <FileText className="w-5 h-5 text-sentry-blue" />,
    iconBg: 'bg-sentry-blue/10',
    borderHover: 'hover:border-sentry-blue/40',
    title: 'Forensic Post-Mortems',
    desc: 'Generate audit-ready incident reports in Markdown, HTML, and JSON-LD for compliance reviews and internal root cause analyses.',
    footer: 'Export to Slack / Confluence'
  }
];

export const BentoGrid: React.FC = () => {
  return (
    <section id="features" className="py-20 px-4 lg:px-8 border-t border-white/10 bg-surface-1/40">
      <div className="max-w-6xl mx-auto">
        
        {/* Section Header with ScrollReveal */}
        <ScrollReveal animation="fade-up" durationMs={800}>
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sentry-violet/10 border border-sentry-violet/30 text-sentry-violet text-xs font-mono font-medium mb-3">
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
        </ScrollReveal>

        {/* Bento Grid with Cascading Staggered ScrollReveal */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {BENTO_ITEMS.map((item, index) => (
            <ScrollReveal 
              key={index} 
              animation="fade-up" 
              delayMs={index * 120} 
              durationMs={700}
              className="h-full flex"
            >
              <div className={`glass-card rounded-2xl p-6 border border-white/10 ${item.borderHover} hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between w-full`}>
                <div>
                  <div className={`w-10 h-10 rounded-xl ${item.iconBg} flex items-center justify-center mb-4`}>
                    {item.icon}
                  </div>
                  <h3 className="text-base font-bold text-white mb-1">{item.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-white/10 font-mono text-[11px] text-slate-500">
                  {item.footer}
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>

      </div>
    </section>
  );
};
