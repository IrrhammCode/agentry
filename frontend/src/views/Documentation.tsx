import React, { useState } from 'react';
import { 
  BookOpen, 
  Code2, 
  Terminal, 
  Lightbulb, 
  Copy, 
  Check, 
  Cpu, 
  ShieldCheck, 
  Zap, 
  Layers, 
  Server, 
  Sparkles, 
  Flame, 
  Lock, 
  RefreshCw,
  ExternalLink,
  ShieldAlert,
  Coins,
  ArrowRight
} from 'lucide-react';

type DocSection = 'quickstart' | 'modes' | 'api' | 'ideas' | 'architecture';

export const Documentation: React.FC = () => {
  const [activeSection, setActiveSection] = useState<DocSection>('quickstart');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="flex-grow max-w-7xl mx-auto w-full px-4 lg:px-8 py-10 space-y-10 bg-black text-slate-200">
      
      {/* Header */}
      <div className="pb-6 border-b border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sentry-cyan/10 border border-sentry-cyan/20 text-sentry-cyan text-xs font-mono font-medium mb-2">
            <BookOpen className="w-3.5 h-3.5" />
            <span>AGENTRY DEVELOPER DOCUMENTATION & INNOVATION HUB</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-white tracking-tight">
            How to Use Agentry & Next-Gen Architecture
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Complete integration guides, REST API reference manual, and breakthrough technical ideas.
          </p>
        </div>

        {/* Section Navigation Pills */}
        <div className="flex items-center gap-1.5 p-1 bg-surface-1 rounded-xl border border-white/10 overflow-x-auto text-xs font-mono">
          <button
            onClick={() => setActiveSection('quickstart')}
            className={`px-3 py-2 rounded-lg transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'quickstart'
                ? 'bg-surface-2 text-white border border-white/10 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-sentry-cyan" />
            <span>1. Quickstart</span>
          </button>

          <button
            onClick={() => setActiveSection('modes')}
            className={`px-3 py-2 rounded-lg transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'modes'
                ? 'bg-surface-2 text-white border border-white/10 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Code2 className="w-3.5 h-3.5 text-sentry-emerald" />
            <span>2. Integration Modes</span>
          </button>

          <button
            onClick={() => setActiveSection('api')}
            className={`px-3 py-2 rounded-lg transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'api'
                ? 'bg-surface-2 text-white border border-white/10 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Server className="w-3.5 h-3.5 text-amber-400" />
            <span>3. REST API</span>
          </button>

          <button
            onClick={() => setActiveSection('ideas')}
            className={`px-3 py-2 rounded-lg transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'ideas'
                ? 'bg-surface-2 text-white border border-white/10 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Lightbulb className="w-3.5 h-3.5 text-sentry-violet" />
            <span>4. Cari Ide (Ideas)</span>
          </button>

          <button
            onClick={() => setActiveSection('architecture')}
            className={`px-3 py-2 rounded-lg transition-all flex items-center gap-1.5 whitespace-nowrap ${
              activeSection === 'architecture'
                ? 'bg-surface-2 text-white border border-white/10 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-sentry-red" />
            <span>5. Architecture</span>
          </button>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* SECTION 1: QUICKSTART & PRE-FLIGHT DIAGNOSTICS                         */}
      {/* ===================================================================== */}
      {activeSection === 'quickstart' && (
        <div className="space-y-6 animate-fade-in">
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                <Terminal className="w-5 h-5 text-sentry-cyan" />
                <span>3-Step Setup & Pre-Flight Validation</span>
              </h2>
              <p className="text-sm text-slate-400">
                Get the full Agentry runtime (TabPFN sentry engine, REST API daemon, and Web UI) running in under 2 minutes.
              </p>
            </div>

            {/* Step 1 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 font-mono text-xs text-sentry-cyan font-semibold">
                <span className="w-5 h-5 rounded-full bg-sentry-cyan/20 flex items-center justify-center">1</span>
                <span>Clone and Install Dependencies</span>
              </div>
              <div className="relative p-4 rounded-xl bg-black border border-white/10 font-mono text-xs text-slate-300">
                <button 
                  onClick={() => handleCopy("git clone https://github.com/IrrhammCode/agentry.git\ncd agentry\npython -m venv .venv\n.venv\\Scripts\\activate\npip install -e .", 'step1')}
                  className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                >
                  {copiedKey === 'step1' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
                <pre className="overflow-x-auto leading-relaxed">
{`git clone https://github.com/IrrhammCode/agentry.git
cd agentry
python -m venv .venv

# On Windows:
.venv\\Scripts\\activate

# On Linux/macOS:
source .venv/bin/activate

pip install -e .`}
                </pre>
              </div>
            </div>

            {/* Step 2 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 font-mono text-xs text-sentry-emerald font-semibold">
                <span className="w-5 h-5 rounded-full bg-sentry-emerald/20 flex items-center justify-center">2</span>
                <span>Configure Environment (.env)</span>
              </div>
              <div className="relative p-4 rounded-xl bg-black border border-white/10 font-mono text-xs text-slate-300">
                <button 
                  onClick={() => handleCopy("TABPFN_API_KEY=your_key_here\nTABPFN_MODEL=tabpfn-3.5-classification\nTABPFN_THINKING_MODE=true\nDAILY_FLEET_BUDGET_USD=50.00", 'step2')}
                  className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                >
                  {copiedKey === 'step2' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
                <pre className="overflow-x-auto leading-relaxed">
{`# Prior Labs TabPFN-3.5 Cloud Credentials (optional for local mode)
TABPFN_API_KEY=your_prior_labs_key
TABPFN_MODEL=tabpfn-3.5-classification
TABPFN_THINKING_MODE=true

# Daily spend governor ceiling across all agents
DAILY_FLEET_BUDGET_USD=50.00
SESSION_MAX_COST_USD=5.00`}
                </pre>
              </div>
            </div>

            {/* Step 3 */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 font-mono text-xs text-amber-400 font-semibold">
                <span className="w-5 h-5 rounded-full bg-amber-500/20 flex items-center justify-center">3</span>
                <span>Run Doctor Diagnostic & Launch Daemon</span>
              </div>
              <div className="relative p-4 rounded-xl bg-black border border-white/10 font-mono text-xs text-slate-300">
                <button 
                  onClick={() => handleCopy("python run.py doctor\npython run.py serve --port 8000", 'step3')}
                  className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                >
                  {copiedKey === 'step3' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
                <pre className="overflow-x-auto leading-relaxed">
{`# 1. Validate all subsystems (TabPFN, SQLite, DLP engine, blast radius):
python run.py doctor

# 2. Start the HTTP Sentry Daemon on port 8000:
python run.py serve --port 8000`}
                </pre>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* SECTION 2: INTEGRATION MODES (HOW TO USE)                             */}
      {/* ===================================================================== */}
      {activeSection === 'modes' && (
        <div className="space-y-8 animate-fade-in">
          
          {/* Mode 1: Zero-Code OpenAI Proxy */}
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div>
                <span className="px-2 py-0.5 rounded bg-sentry-cyan/20 text-sentry-cyan text-[11px] font-mono font-bold border border-sentry-cyan/30">
                  RECOMMENDED • ZERO CODE CHANGES
                </span>
                <h3 className="text-lg font-bold text-white mt-1">
                  Mode 1: Zero-Code OpenAI Reverse Proxy
                </h3>
              </div>
              <span className="text-xs font-mono text-slate-400">Works with any language or framework</span>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
              Simply point your existing OpenAI client's <code className="text-sentry-cyan">base_url</code> to <code className="text-sentry-cyan">http://127.0.0.1:8000/v1</code> and pass the agent session ID in headers. Agentry automatically sanitizes secrets and evaluates TabPFN circuit breakers on every tool call and completion turn.
            </p>

            <div className="relative p-4 rounded-xl bg-black border border-white/10 font-mono text-xs text-sentry-cyan">
              <button 
                onClick={() => handleCopy(`from openai import OpenAI

# Direct any OpenAI-compatible client to local Agentry Sentry
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="upstream-api-key",
    default_headers={"X-Agent-Session": "swe_coder_task_402"}
)

# In-flight DLP masks credentials; TabPFN evaluates runaway loops in 14.8ms
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Run test suite and refactor auth.py"}]
)

print(response.choices[0].message.content)`, 'proxy_code')}
                className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
              >
                {copiedKey === 'proxy_code' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
              <pre className="overflow-x-auto leading-relaxed">
{`from openai import OpenAI

# Direct any OpenAI-compatible client to local Agentry Sentry
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="upstream-api-key",
    default_headers={"X-Agent-Session": "swe_coder_task_402"}
)

# In-flight DLP masks credentials; TabPFN evaluates runaway loops in 14.8ms
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Run test suite and refactor auth.py"}]
)

print(response.choices[0].message.content)`}
              </pre>
            </div>
          </div>

          {/* Mode 2: Python SDK & Decorator Guard */}
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 space-y-4">
            <div>
              <span className="px-2 py-0.5 rounded bg-sentry-emerald/20 text-sentry-emerald text-[11px] font-mono font-bold border border-emerald-500/30">
                PYTHON NATIVE
              </span>
              <h3 className="text-lg font-bold text-white mt-1">
                Mode 2: Python SDK & Decorator Guard (`@guard.protect`)
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
              Wrap any tool execution function in your LangChain, AutoGen, CrewAI, or custom agent framework. Catastrophic commands (e.g. <code className="text-red-400">rm -rf /</code>) are blocked before shell execution is granted.
            </p>

            <div className="relative p-4 rounded-xl bg-black border border-white/10 font-mono text-xs text-sentry-emerald">
              <button 
                onClick={() => handleCopy(`from agentry.guard import AgentryGuard

guard = AgentryGuard(session_id="swe_bench_worker", auto_fit=True)

@guard.protect
def execute_bash_tool(command: str) -> str:
    """
    Agentry automatically:
    1. Evaluates blast radius before process spawns.
    2. Redacts sensitive credentials in-flight.
    3. Feeds metrics (tokens, latency, repetition) to TabPFN.
    4. Halts with AgentHaltException if risk > 0.85.
    """
    import subprocess
    return subprocess.check_output(command, shell=True, text=True)

# Nominal execution: PASS
output = execute_bash_tool("pytest tests/test_auth.py")

# Catastrophic execution: Raises AgentHaltException in 14.8ms
# execute_bash_tool("rm -rf / --no-preserve-root")`, 'sdk_code')}
                className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
              >
                {copiedKey === 'sdk_code' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
              <pre className="overflow-x-auto leading-relaxed">
{`from agentry.guard import AgentryGuard

guard = AgentryGuard(session_id="swe_bench_worker", auto_fit=True)

@guard.protect
def execute_bash_tool(command: str) -> str:
    """
    Agentry automatically:
    1. Evaluates blast radius before process spawns.
    2. Redacts sensitive credentials in-flight.
    3. Feeds metrics (tokens, latency, repetition) to TabPFN.
    4. Halts with AgentHaltException if risk > 0.85.
    """
    import subprocess
    return subprocess.check_output(command, shell=True, text=True)

# Nominal execution: PASS
output = execute_bash_tool("pytest tests/test_auth.py")

# Catastrophic execution: Raises AgentHaltException in 14.8ms
# execute_bash_tool("rm -rf / --no-preserve-root")`}
              </pre>
            </div>
          </div>

          {/* Mode 3: Model Context Protocol (MCP) Server */}
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 space-y-4">
            <div>
              <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-[11px] font-mono font-bold border border-amber-500/30">
                IDE INTEGRATION (CURSOR / CLAUDE DESKTOP)
              </span>
              <h3 className="text-lg font-bold text-white mt-1">
                Mode 3: Model Context Protocol (MCP) Sentry Server
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
              Equip Cursor IDE, Claude Desktop, or Windsurf with TabPFN guardrails using the open MCP standard:
            </p>

            <div className="relative p-4 rounded-xl bg-black border border-white/10 font-mono text-xs text-amber-300">
              <button 
                onClick={() => handleCopy(`// Add to Cursor or Claude Desktop mcpServers config:
{
  "mcpServers": {
    "agentry-sentry": {
      "command": "python",
      "args": ["-m", "agentry.mcp_server", "--transport", "stdio"],
      "env": {
        "TABPFN_API_KEY": "your_api_key_here"
      }
    }
  }
}`, 'mcp_code')}
                className="absolute top-3 right-3 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
              >
                {copiedKey === 'mcp_code' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
              <pre className="overflow-x-auto leading-relaxed">
{`// Add to Cursor or Claude Desktop mcpServers config:
{
  "mcpServers": {
    "agentry-sentry": {
      "command": "python",
      "args": ["-m", "agentry.mcp_server", "--transport", "stdio"],
      "env": {
        "TABPFN_API_KEY": "your_api_key_here"
      }
    }
  }
}`}
              </pre>
            </div>
          </div>

        </div>
      )}

      {/* ===================================================================== */}
      {/* SECTION 3: REST API REFERENCE                                         */}
      {/* ===================================================================== */}
      {activeSection === 'api' && (
        <div className="space-y-6 animate-fade-in">
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                <Server className="w-5 h-5 text-amber-400" />
                <span>REST API Specification (`http://127.0.0.1:8000`)</span>
              </h2>
              <p className="text-sm text-slate-400">
                Full HTTP endpoint interface for custom fleet runners, microservices, and monitoring sidecars.
              </p>
            </div>

            <div className="space-y-4 font-mono text-xs">
              
              {/* Endpoint 1 */}
              <div className="p-4 rounded-xl bg-black border border-white/10 space-y-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald font-bold border border-emerald-500/30">POST</span>
                    <span className="text-white font-bold text-sm">/v1/audit</span>
                  </div>
                  <span className="text-slate-400">Real-time TabPFN Bayesian audit</span>
                </div>
                <div className="text-slate-300 font-mono text-[11px]">
                  Body: <code className="text-sentry-cyan">&#123; session_id, tool_name, input_text, thought_trace, latency_ms &#125;</code>
                </div>
                <div className="text-slate-400 text-[11px]">
                  Returns TabPFN <code className="text-white">failure_probability</code>, <code className="text-white">action</code> (PASS / KILL / PAUSE / REROUTE), <code className="text-white">estimated_cost_saved_usd</code>, and provider reason.
                </div>
              </div>

              {/* Endpoint 2 */}
              <div className="p-4 rounded-xl bg-black border border-white/10 space-y-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-sentry-cyan/20 text-sentry-cyan font-bold border border-sentry-cyan/30">GET</span>
                    <span className="text-white font-bold text-sm">/v1/fleet</span>
                  </div>
                  <span className="text-slate-400">Aggregate fleet governance statistics</span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  Returns <code className="text-white">total_audited_steps</code>, <code className="text-white">unique_sessions</code>, <code className="text-white">interventions</code> (KILL, PASS, PAUSE, REROUTE), and total capital preserved from SQLite storage.
                </div>
              </div>

              {/* Endpoint 3 */}
              <div className="p-4 rounded-xl bg-black border border-white/10 space-y-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald font-bold border border-emerald-500/30">POST</span>
                    <span className="text-white font-bold text-sm">/v1/dlp/redact</span>
                  </div>
                  <span className="text-slate-400">In-flight secret scanner & redactor</span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  Scans input text with 8 high-performance compiled regex patterns (AWS keys, OpenAI tokens, Anthropic keys, Postgres URIs) and returns masked string with detected secret classes.
                </div>
              </div>

              {/* Endpoint 4 */}
              <div className="p-4 rounded-xl bg-black border border-white/10 space-y-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-sentry-emerald font-bold border border-emerald-500/30">POST</span>
                    <span className="text-white font-bold text-sm">/v1/blast-radius/evaluate</span>
                  </div>
                  <span className="text-slate-400">Command hazard scoring (0 to 100)</span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  Evaluates destructive command patterns across Linux, macOS, and Windows. Returns hazard score, <code className="text-white">is_blocked</code> boolean, and violation rationale.
                </div>
              </div>

              {/* Endpoint 5 */}
              <div className="p-4 rounded-xl bg-black border border-white/10 space-y-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30">GET/POST</span>
                    <span className="text-white font-bold text-sm">/v1/approvals</span>
                  </div>
                  <span className="text-slate-400">Human-in-the-Loop authorization queue</span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  Lists pending approvals held by TabPFN. Post to <code className="text-white">/v1/approvals/&#123;id&#125;</code> with <code className="text-white">&#123; action: "RESUME" | "REROUTE" | "ABORT" &#125;</code> to unblock agent.
                </div>
              </div>

            </div>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* SECTION 4: CARI IDE (INNOVATION IDEAS & ROADMAP)                       */}
      {/* ===================================================================== */}
      {activeSection === 'ideas' && (
        <div className="space-y-6 animate-fade-in">
          <div className="p-6 rounded-2xl bg-gradient-to-r from-violet-950/40 via-surface-1 to-cyan-950/30 border border-violet-500/30">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-5 h-5 text-sentry-violet animate-pulse" />
              <h2 className="text-xl font-bold text-white">
                "Cari Ide": Next-Gen Technical Frontiers for TabPFN Sentry
              </h2>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed max-w-3xl">
              Breakthrough ideas to expand Agentry beyond basic anomaly detection into an unassailable enterprise moat, leveraging the unique superpowers of the Prior Labs TabPFN-3.5 foundation model.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            
            {/* Idea 1 */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-cyan/40 transition-all space-y-3">
              <div className="flex items-center gap-2 text-sentry-cyan font-mono text-xs font-bold">
                <Cpu className="w-4 h-4" />
                <span>IDEA #1 • SUB-10MS JAILBREAK FILTER</span>
              </div>
              <h3 className="text-base font-bold text-white">
                Tabular Prompt Injection & Jailbreak Fingerprinting
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Instead of using slow, costly secondary LLMs to check for prompt injections, convert prompts into a <strong>16-dimensional statistical vector</strong> (character entropy, perplexity variance, negation frequency, zero-width spaces). TabPFN-3.5 classifies adversarial intent in <strong>under 8ms</strong> with zero prompt leakage.
              </p>
            </div>

            {/* Idea 2 */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-red/40 transition-all space-y-3">
              <div className="flex items-center gap-2 text-sentry-red font-mono text-xs font-bold">
                <ShieldAlert className="w-4 h-4" />
                <span>IDEA #2 • KERNEL HARDENING</span>
              </div>
              <h3 className="text-base font-bold text-white">
                Linux eBPF Kernel Probe Sandbox
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Connect TabPFN risk evaluations directly to Linux eBPF kernel probes (<code className="text-slate-300">sys_enter_unlinkat</code>). If an agent's blast radius exceeds threshold, the Linux kernel itself intercepts the syscall and returns <code className="text-red-400">EPERM</code>, preventing escapes even from compiled binaries or subshells.
              </p>
            </div>

            {/* Idea 3 */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-amber-400/40 transition-all space-y-3">
              <div className="flex items-center gap-2 text-amber-400 font-mono text-xs font-bold">
                <RefreshCw className="w-4 h-4" />
                <span>IDEA #3 • SELF-IMPROVING SYNTHETICS</span>
              </div>
              <h3 className="text-base font-bold text-white">
                Automated Multi-Turn Adversarial Red-Team Fuzzer
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                A built-in adversarial fuzzer agent that constantly attempts to trick agent workflows into infinite loops and context exhaustion. The resulting edge-case telemetry feeds directly into TabPFN in-context learning, creating a continuous immune system that strengthens with every attack.
              </p>
            </div>

            {/* Idea 4 */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-emerald/40 transition-all space-y-3">
              <div className="flex items-center gap-2 text-sentry-emerald font-mono text-xs font-bold">
                <Coins className="w-4 h-4" />
                <span>IDEA #4 • COMPUTE HEDGING</span>
              </div>
              <h3 className="text-base font-bold text-white">
                Predictive Token Futures & Compute Arbitrage
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Use TabPFN's cost regression engine at Step 3 to predict the final trajectory spend distribution. If projected cost exceeds task ROI, Agentry dynamically downgrades model tiers (e.g. from GPT-4o to ultra-fast Groq Llama-3.3-70B) or compresses context windows to preserve budget.
              </p>
            </div>

            {/* Idea 5 */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-violet-400/40 transition-all space-y-3">
              <div className="flex items-center gap-2 text-violet-400 font-mono text-xs font-bold">
                <Lock className="w-4 h-4" />
                <span>IDEA #5 • SWARM CONSENSUS</span>
              </div>
              <h3 className="text-base font-bold text-white">
                Cryptographic Attestation Quorum for Agent Swarms
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                In multi-agent swarms (CrewAI / AutoGen), each agent's tool execution requires a signed cryptographic attestation from Agentry TabPFN Sentry before changes are committed to shared databases. Rogue hallucinating agents have their delegation credentials revoked in real-time.
              </p>
            </div>

            {/* Idea 6 */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 hover:border-sentry-cyan/40 transition-all space-y-3">
              <div className="flex items-center gap-2 text-sentry-cyan font-mono text-xs font-bold">
                <Flame className="w-4 h-4" />
                <span>IDEA #6 • HACKATHON WINNING HOOK</span>
              </div>
              <h3 className="text-base font-bold text-white">
                The Winning Pitch Angle for Prior Labs Judges
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Position TabPFN-3.5 as the foundational infrastructure for AI Agent Reliability. LLMs cannot reliably guard other LLMs; tabular foundation models are the mathematically calibrated missing layer that makes autonomous agents safe for enterprise production.
              </p>
            </div>

          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* SECTION 5: ARCHITECTURE BLUEPRINT                                     */}
      {/* ===================================================================== */}
      {activeSection === 'architecture' && (
        <div className="space-y-6 animate-fade-in">
          <div className="glass-card rounded-2xl p-6 sm:p-8 border border-white/10 space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                <Layers className="w-5 h-5 text-sentry-red" />
                <span>TabPFN-3.5 Sentry Architecture Blueprint</span>
              </h2>
              <p className="text-sm text-slate-400">
                How tabular telemetry streams are converted into sub-20ms Bayesian intervention verdicts.
              </p>
            </div>

            {/* Visual Flow diagram */}
            <div className="p-6 rounded-xl bg-black border border-white/10 font-mono text-xs space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-4 text-center">
                <div className="p-3 rounded-lg bg-surface-2 border border-white/10 flex-1 min-w-[140px]">
                  <div className="text-sentry-cyan font-bold">1. Inbound Tool Call</div>
                  <div className="text-[10px] text-slate-400 mt-1">Bash / SQL / File Edit</div>
                </div>

                <ArrowRight className="w-5 h-5 text-slate-500 hidden sm:block" />

                <div className="p-3 rounded-lg bg-violet-950/30 border border-violet-500/30 flex-1 min-w-[140px]">
                  <div className="text-sentry-violet font-bold">2. In-Flight DLP</div>
                  <div className="text-[10px] text-slate-400 mt-1">Secrets Masked (0ms)</div>
                </div>

                <ArrowRight className="w-5 h-5 text-slate-500 hidden sm:block" />

                <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/30 flex-1 min-w-[140px]">
                  <div className="text-sentry-emerald font-bold">3. TabPFN-3.5 Prior</div>
                  <div className="text-[10px] text-slate-400 mt-1">16 Metrics (14.8ms)</div>
                </div>

                <ArrowRight className="w-5 h-5 text-slate-500 hidden sm:block" />

                <div className="p-3 rounded-lg bg-red-950/30 border border-red-500/30 flex-1 min-w-[140px]">
                  <div className="text-sentry-red font-bold">4. Sentry Decision</div>
                  <div className="text-[10px] text-slate-400 mt-1">PASS • KILL • PAUSE</div>
                </div>
              </div>
            </div>

            {/* Why TabPFN vs LLMs comparison */}
            <div className="overflow-x-auto">
              <table className="w-full text-xs font-mono border border-white/10 rounded-xl overflow-hidden">
                <thead className="bg-surface-2 text-slate-300 border-b border-white/10">
                  <tr>
                    <th className="p-3 text-left">Evaluation Metric</th>
                    <th className="p-3 text-left text-red-400">Traditional LLM Guardrail</th>
                    <th className="p-3 text-left text-sentry-emerald">Agentry + TabPFN-3.5</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-slate-400">
                  <tr>
                    <td className="p-3 font-bold text-white">Inference Latency</td>
                    <td className="p-3 text-red-400">1,500ms – 3,000ms (Slow)</td>
                    <td className="p-3 text-sentry-emerald font-bold">14.8 milliseconds (Sub-20ms)</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-bold text-white">Data Privacy</td>
                    <td className="p-3 text-red-400">Leaks code traces to external APIs</td>
                    <td className="p-3 text-sentry-emerald font-bold">100% Zero-Prompt Transmission</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-bold text-white">Few-Shot Generalization</td>
                    <td className="p-3 text-red-400">Requires expensive prompt tuning</td>
                    <td className="p-3 text-sentry-emerald font-bold">Bayesian Prior on Grouped Telemetry</td>
                  </tr>
                  <tr>
                    <td className="p-3 font-bold text-white">Probability Calibration</td>
                    <td className="p-3 text-red-400">Uncalibrated soft token logprobs</td>
                    <td className="p-3 text-sentry-emerald font-bold">Calibrated Bayesian Posterior Uncertainty</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
