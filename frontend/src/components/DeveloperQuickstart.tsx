import React, { useState } from 'react';
import { Code2, Copy, Check } from 'lucide-react';

const SNIPPETS = {
  proxy: `# Point any OpenAI-compatible client to the local Agentry proxy
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8787/v1",
    api_key="upstream-api-key",
    default_headers={"X-Agent-Session": "swe_bench_coder_01"}
)

# In-flight DLP redacts secrets; TabPFN evaluates runaway loops in 15ms
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Execute test refactor..."}]
)`,
  sdk: `from agentry.guard import AgentryGuard

guard = AgentryGuard(session_id="agent_worker_prod")

@guard.protect
def execute_agent_tool(tool_name: str, payload: dict):
    # Intercepts catastrophic bash commands and halts infinite retry loops
    return run_tool(tool_name, payload)`,
  mcp: `// Add to Cursor or Claude Desktop mcpServers config:
{
  "mcpServers": {
    "agentry": {
      "command": "python",
      "args": ["-m", "agentry.mcp_server"],
      "env": { "TABPFN_API_KEY": "your-prior-labs-key" }
    }
  }
}`,
  cli: `# Verify your environment and start the mission control console:
python run.py doctor       # Pre-flight environment diagnostics
python run.py serve        # Start OpenAI Reverse Proxy & API
python run.py landing      # Open modern Cyber-Sentry UI`,
};

type TabKey = keyof typeof SNIPPETS;

export const DeveloperQuickstart: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('proxy');
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(SNIPPETS[activeTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="py-20 px-4 lg:px-8 border-t border-white/10 bg-surface-1/40">
      <div className="max-w-5xl mx-auto">
        
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sentry-cyan/10 border border-sentry-cyan/30 text-sentry-cyan text-xs font-mono font-medium mb-3">
            <Code2 className="w-3.5 h-3.5" />
            <span>5-MINUTE INTEGRATION</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-white mb-3">
            <span className="animate-text-shimmer">Start Guarding Your Agents in Minutes</span>
          </h2>
          <p className="text-slate-400 max-w-xl mx-auto text-sm">
            Whether you use raw OpenAI calls, LangChain, CrewAI, AutoGen, or Cursor IDE.
          </p>
        </div>

        <div className="glass-card rounded-2xl overflow-hidden border border-white/15">
          {/* Code Tabs */}
          <div className="flex items-center gap-2 px-4 py-2.5 bg-surface-1 border-b border-white/10 overflow-x-auto font-mono text-xs">
            <button
              onClick={() => setActiveTab('proxy')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'proxy'
                  ? 'bg-surface-2 text-white border border-white/10'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              1. Zero-Code OpenAI Proxy
            </button>
            <button
              onClick={() => setActiveTab('sdk')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'sdk'
                  ? 'bg-surface-2 text-white border border-white/10'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              2. Python SDK Guard
            </button>
            <button
              onClick={() => setActiveTab('mcp')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'mcp'
                  ? 'bg-surface-2 text-white border border-white/10'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              3. Cursor / Claude MCP
            </button>
            <button
              onClick={() => setActiveTab('cli')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'cli'
                  ? 'bg-surface-2 text-white border border-white/10'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              4. CLI & Doctor
            </button>
          </div>

          {/* Code Content */}
          <div className="p-6 bg-void/90 relative">
            <button
              onClick={handleCopy}
              className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-2 hover:bg-surface-3 border border-white/10 text-xs font-mono text-slate-300"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-sentry-emerald" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>

            <pre className="font-mono text-xs text-slate-200 overflow-x-auto leading-relaxed pt-2">
              <code>{SNIPPETS[activeTab]}</code>
            </pre>
          </div>
        </div>

      </div>
    </section>
  );
};
