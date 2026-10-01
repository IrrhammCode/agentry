# 🎨 Agentry Front-End Design & UI/UX Master Specification
### *The Autonomous Tabular Guardrail & Sentry for AI Agent Fleets*
**Powered by Prior Labs TabPFN-3.5 Foundation Model & Local-First Intelligence**

---

## 📌 Document Overview & Purpose

Dokumen ini adalah **Master Prompt & Design Specification** resmi untuk membangun frontend antarmuka pengguna (UI/UX) generasi berikutnya untuk **Agentry**. 

Dokumen ini dirancang secara komprehensif agar dapat digunakan oleh:
1. **Frontend Engineers / UI Designers** untuk mengimplementasikan dashboard web production-grade modern (Next.js 15, React, Tailwind CSS, Shadcn UI, Framer Motion, React Flow).
2. **AI Code Generation Engines** (v0.dev, Cursor IDE, Windsurf, Bolt.new, Claude 3.7 Sonnet) sebagai *mega-prompt* dengan konteks penuh arsitektur, tema visual, komponen, dan interaktivitas.
3. **Product & SecOps Teams** sebagai standar desain antarmuka command center AI safety & fleet governance.

> [!NOTE]
> Untuk spesifikasi dan master prompt pembuatan **Public Landing Page & Marketing Showcase Website**, silakan merujuk pada:
> **[`docs/LANDING_PAGE_DESIGN_PROMPT.md`](file:///C:/Users/Irham/Documents/code/tabfpn/docs/LANDING_PAGE_DESIGN_PROMPT.md)**.


## 🏛️ 1. Executive Vision & Atmosphere (The "Vibe")

### 1.1 Aesthetic Persona: Cyber-Sentry / Defense SOC Mission Control
Agentry bukan sekadar SaaS dashboard biasa dengan tema putih standar. Agentry adalah **Sentry & Circuit-Breaker** untuk armada agen AI otonom perusahaan.
- **Inspirasi Visual:** Palantir Foundry, CrowdStrike Falcon SOC, Linear.app, Vercel Dashboard, SentinelOne, dan sci-fi mission control aesthetic.
- **Mood:** Berwibawa, mission-critical, presisi tinggi, futuristik namun berkelas (sleek dark mode), tidak berantakan, data-dense tapi tetap mudah dipindai secara visual dalam hitungan milidetik.
- **Emotional Reaction:** *"Armada agen AI perusahaan kami berada di bawah pengawasan sentry super-intelijen berkecepatan 15 milidetik yang tidak akan membiarkan loop tak berujung, kebocoran API key, atau perusakan filesystem terjadi."*

---

## 🎨 2. Visual Identity & Design System Tokens

### 2.1 Color Palette (Tailwind HSL / Hex Mappings)

```css
:root {
  /* Background Layers */
  --bg-deep-void: #07090E;       /* Deepest canvas background */
  --bg-surface-1: #0F172A;        /* Cards, panels, container background */
  --bg-surface-2: #1E293B;        /* Secondary panels, hovered rows, active tabs */
  --bg-surface-3: #334155;        /* Modal headers, dropdown surfaces */

  /* Border & Dividers */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.16);
  --border-focus: #60EFFF;

  /* Brand Accents */
  --tabpfn-emerald: #00FF87;      /* TabPFN Foundation Model Brand (Nominal / Success) */
  --sentry-cyan: #60EFFF;         /* Primary brand accent / Telemetry pulse */
  --sentry-violet: #8B5CF6;       /* In-Context Active Learning Exemplars */
  --sentry-amber: #F59E0B;        /* High Risk / REROUTE / Quarantine */
  --sentry-red: #EF4444;          /* CRITICAL / KILL / Circuit-Breaker Trip */
  --sentry-blue: #38BDF8;         /* Informational / Session Tracker */

  /* Text Typography Colors */
  --text-primary: #F8FAFC;        /* High contrast headers & values */
  --text-secondary: #94A3B8;      /* Labels, descriptions, captions */
  --text-muted: #64748B;          /* Placeholders, disabled states */
  --text-code: #E2E8F0;           /* Code, terminal traces */

  /* Glassmorphism & Shadows */
  --glass-bg: rgba(15, 23, 42, 0.75);
  --glass-blur: blur(12px);
  --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  --neon-glow-cyan: 0 0 15px rgba(96, 239, 255, 0.25);
  --neon-glow-red: 0 0 15px rgba(239, 68, 68, 0.35);
  --neon-glow-emerald: 0 0 15px rgba(0, 255, 135, 0.25);
}
```

### 2.2 Typography Hierarchy
- **Header & Brand Font:** `Space Grotesk` atau `Inter Display` (Bold, Modern, Semi-expanded geometry).
- **Body & Controls:** `Inter` atau `Plus Jakarta Sans` (Clean, highly legible on OLED/LCD screens).
- **Telemetry, Metrics & Terminal:** `JetBrains Mono` atau `Fira Code` (Monospaced, tabular numbers `font-variant-numeric: tabular-nums`).

---

## 📐 3. Global Layout & Shell Architecture

```
+----------------------------------------------------------------------------------------------------+
|  TOPBAR: [🛡️ Agentry v0.1.0] [Status: 🟢 ONLINE] [TabPFN Cloud: ⚡ 15ms]  |  [24h Spend: $4.12] [🔔 3 Alerts] [Admin] |
+------------------+---------------------------------------------------------------------------------+
|  SIDEBAR NAV     |  MAIN CONTENT VIEWPORT                                                          |
|                  |                                                                                 |
|  🚀 Fleet Radar  |  +---------------------------------------------------------------------------+  |
|  🛡️ Defense & DLP|  |  HEADER KPI BANNER: 4 Live Agents | 94.2% Risk Intercepted | $124.50 Saved     |  |
|  🧪 What-If Sim  |  +---------------------------------------------------------------------------+  |
|  ⏸️ HITL War Room|                                                                                 |
|  💰 Budget Pilot |  [ TABPANEL / DYNAMIC WORKSPACE COMPONENT ]                                     |
|  🔍 Session Logs |                                                                                 |
|  📊 Benchmarks   |  (Interactive visualizers, real-time graphs, sandboxes, timeline scrubbers)     |
|  🔌 MCP & API    |                                                                                 |
|                  |                                                                                 |
|  [Emergency Stop]|                                                                                 |
+------------------+---------------------------------------------------------------------------------+
```

### 3.1 Persistent Topbar
1. **Brand Identity:** Logo hexagon tameng dengan gradient `#00FF87` ke `#60EFFF`.
2. **Engine Live Health Badge:** 
   - `🟢 TabPFN-3.5 Cloud (Thinking Mode)` dengan ping indikator pulsing.
   - Fallback mode: `⚡ High-Fidelity Local Sentry (Air-Gapped)`.
3. **Fleet Financial Gauge:** Mini-progress bar 24h budget spend (`$3.42 / $25.00 USD`).
4. **Active Notification Bell:** Badge jumlah insiden tertahan di HITL.
5. **Global Quick Actions:** Search bar (`Cmd + K` / `Ctrl + K`) untuk melompat langsung ke `session_id`, nama tool, atau prompt trace.

### 3.2 Navigation Sidebar
Icon-rich collapsible sidebar (Lucide icons):
- `🚀 Live Fleet Simulation`
- `🛡️ Active Defense & DLP` (5 Next-Gen Security Pillars)
- `🧪 What-If Policy Simulator` (Pareto Frontier & Counterfactuals)
- `⏸️ HITL Approval War Room` (Operator Escalations with Live Badges)
- `💰 Fleet Budget Autopilot` (Runaway Quota Governor)
- `🔍 Forensic Session Inspector` (Audit Post-Mortems & Markdown/HTML Exporter)
- `📊 Empirical Benchmark Suite` (TabPFN vs XGBoost / Random Forest on Real SWE-bench)
- `🔌 Model Context Protocol (MCP) & Proxy` (Cursor, Claude Desktop, and OpenAI gateway)
- **Bottom Danger Anchor:** `🛑 EMERGENCY FLEET KILL SWITCH` (Modal konfirmasi beranimasi merah terang untuk membekukan seluruh swarm).

---

## 🖥️ 4. Screen-by-Screen Detailed UI Specifications

---

### Screen 1: 🚀 Live Fleet Command Center (Mission Control)

#### 1.1 Real-Time Agent Fleet Grid (4 Cards)
Menampilkan 4 kartu agen otonom yang sedang berjalan secara paralel:
- **Agents:** `CoderAgent-01` (SWE-bench), `DevOps-Sentry` (CI/CD Deployer), `ResearchBot` (Web Intelligence), `DataAnalyst` (Pipeline Runner).
- **Isi Kartu:**
  - Status Indicator: `RUNNING (🟢)`, `REROUTED (🟡)`, `PAUSED (⏸️)`, `TERMINATED (🔴)`.
  - Current Tool Executing: Chip ikon (misal `bash: git push`, `read_file: auth.py`, `sql_query`).
  - Mini Progress Ring: **TabPFN Failure Probability** ($0\% - 100\%$) dengan gradient color shift (Hijau -> Kuning -> Oranye -> Merah).
  - Step Latency & Token Burn Counter (live ticker yang naik tiap langkah).
  - Terminal preview: 2 baris terakhir `thought_trace` agen dengan animasi typewriter halus.

#### 1.2 The Central Radar & Risk Distribution Visualizer
- **TabPFN Multiclass Donut Chart (Plotly / Recharts):**
  - Segment: `NORMAL (Hijau)`, `INFINITE_LOOP (Merah Terang)`, `TOOL_HALLUCINATION (Oranye)`, `COST_RUNAWAY (Ungu)`.
- **Live Trajectory Cost Regressor Line Chart:**
  - Garis solid: Biaya akumulasi aktual sejauh ini ($C_t$).
  - Garis putus-putus bercahaya (*glow dashed line*): Proyeksi biaya akhir TabPFN ($\hat{C}_{\text{terminal}}$) dengan area ketidakpastian Bayesian (*confidence band*).
- **Inflection Point Marker ($t^*$):** Pin bendera pada grafik yang menandai titik mula agen menyimpang dari jalur normal sebelum looping terjadi.

#### 1.3 Live Event Ticker / Stream Feed
- Feed vertikal yang menampilkan audit event setiap step dalam format nano-cards.
- Klik baris untuk membuka *Forensic Side-Drawer* dengan rincian JSON telemetry lengkap.

---

### Screen 2: 🛡️ Active Defense & Operational Security (The 5 Pillars)

Tab bar horizontal dengan 4 sub-view:

#### Tab A: 💣 Semantic Blast-Radius Sandbox
- **Tujuan:** Menguji dan mendemonstrasikan bagaimana Agentry memblokir aksi berbahaya sebelum filesystem/database tersentuh.
- **Komponen Input:**
  - Dropdown Tool: `bash`, `sql_query`, `python_eval`, `filesystem_rm`.
  - Preset Button Pills: `💣 rm -rf /`, `💣 DROP DATABASE prod`, `💣 Reverse Shell Pipe`, `💣 chmod 777 -R /`, `✅ pytest tests/`, `✅ SELECT * FROM orders`.
  - Code Editor Area (Monaco / Prism.js syntax highlighted) untuk mengetik aksi.
  - Action Button: **"Evaluate Blast Radius"** dengan neon glow effect.
- **Komponen Output (Evaluation Card):**
  - **Large Danger Badge:**
    - `CRITICAL` (Merah menyala + icon peringatan nuklir): "Blocked before execution".
    - `HIGH` (Oranye): "Requires HITL operator sign-off".
    - `MEDIUM` (Kuning): "Warning issued".
    - `NONE / LOW` (Hijau): "Action nominal & safe".
  - **Blast Meter Gauge:** Bar horizontal animasi dari $0.00$ ke $1.00$.
  - **Violation Details Box:** Menampilkan regex pattern yang cocok (misal: `\brm\s+-[a-zA-Z]*r.*([/~*])`) dan penjelasan risiko keamanan bahasa manusia.

#### Tab B: 🔒 In-Flight DLP & Secret Masking
- **Tujuan:** Menunjukkan sanitasi data sensitif secara real-time dari prompt & logs.
- **Fitur Interaktif:**
  - "Load Leak Sample": Tombol cepat untuk mengisi payload contoh (OpenAI Key `sk-proj-...`, Anthropic `sk-ant-...`, AWS `AKIA...`, Postgres DB URI dengan password).
  - Dual Split Viewer:
    - Kiri: **Raw In-Flight Text** (dengan highlight merah pada token sensitif).
    - Kanan: **Sanitized Egress Text** (menampilkan tag proteksi `[REDACTED_OPENAI_KEY]`, `[REDACTED_PASSWORD]`).
  - Counter Badge: `🛡️ 2 Secret(s) Intercepted & Masked`.

#### Tab C: 🔄 Multi-Agent Swarm Watchdog
- **Tujuan:** Visualisasi pencegahan deadlock dan siklus delegasi ping-pong ($A \rightarrow B \rightarrow A \rightarrow B$).
- **Visualizer Node Directed Graph (React Flow / D3.js):**
  - Node mewakili agen (`Planner`, `Coder`, `Reviewer`, `Tester`).
  - Edge bercahaya menunjukkan arah delegasi pesan saat ini.
  - Jika siklus berulang terdeteksi ($A \leftrightarrow B$), edge berubah warna menjadi **Merah Berkedip (*Strobe Pulse*)** dengan teks: `🚨 SWARM DEADLOCK INTERCEPTED (Hop 4: Ping-Pong Loop)`.
  - Tombol interaktif: "Simulate Ping-Pong Deadlock" untuk mendemokan intervensi otomatis.

#### Tab D: 🧠 Active In-Context Learning Exemplars
- **Tujuan:** Menunjukkan bagaimana TabPFN belajar secara real-time dari resolusi insiden tanpa offline fine-tuning.
- **Tabel Exemplar Dinamis:**
  - Kolom: `Timestamp`, `Session ID`, `Failed Tool`, `Error Streak`, `Failure Mode`, `Source` (HITL / Autonomic), `TabPFN Impact Weight`.
  - Indikator Visual: Chip `HITL_OPERATOR` (Biru), `AUTONOMIC_REWIND` (Hijau).
  - Tombol: "Inject Simulated Incident" dan "Clear Buffer".

---

### Screen 3: 🧪 What-If Counterfactual Policy Simulator

- **Dual-Pane Control Dashboard:**
  - Slider 1: TabPFN Risk Threshold ($\theta \in [0.10, 0.95]$) dengan tick default rekomendasi $0.85$.
  - Slider 2: Error Streak Tolerance ($1 - 8$ errors).
  - Slider 3: Repetition Entropy Cutoff ($0.30 - 0.95$).
  - Toggle: "Autonomic Self-Healing Rewind Enabled".
- **Dynamic Pareto Metric Comparison (Side-by-Side):**
  - **Card 1: Status Quo (Tanpa Agentry):** Rata-rata token terbakar $142,000$ tokens per failure, biaya $\$0.284$ per run, $0\%$ task completion pada loop trap.
  - **Card 2: Agentry Governed:** Intersepsi pada langkah ke-5, penghematan $87.4\%$ token burn, $90.6\%$ failure recall, hanya $2.0\%$ false-stop rate.
- **Interactive Step Scrubber Timeline:**
  - Slider langkah horizontal ($0 \dots N$). Saat operator menggeser slider, antarmuka memperlihatkan state prompt, diagnosa TabPFN, dan simulasi intervensi (`PASS`, `REROUTE`, `REWIND`, `KILL`) secara real-time.

---

### Screen 4: ⏸️ Human-in-the-Loop (HITL) War Room

- **Kanban Pipeline Columns:**
  - `🚨 Pending Review` (Kartu agen yang sedang dibekukan / `PAUSE`).
  - `🔄 Rerouted with Steering` (Agen yang melanjutkan dengan instruksi manusia).
  - `✅ Resumed` (Agen yang disetujui tanpa perubahan).
  - `🛑 Aborted & Rolled Back` (Agen yang dibatalkan permanen dan file-nya dikembalikan ke snapshot aman).
- **Incident Escalation Card Details:**
  - Nama Agen, Session ID, Waktu Terhenti.
  - TabPFN Diagnostics: *"High Failure Risk (88.4%) - Predicted Mode: TOOL_HALLUCINATION"*.
  - Root Cause Evidence: *"Repeatedly calling non-existent CLI flag '--force-rebase-all' on git tool"*.
  - Proposal Action Input yang tertahan.
- **Operator Action Drawer:**
  - Textarea: *"Custom Steering Directive for Agent"* (dengan saran otomatis AI: *"Use git rebase -i HEAD~3 instead"*).
  - 3 Tombol Utama:
    1. `🟢 Approve & Resume` (Hijau).
    2. `🟡 Steer & Reroute` (Kuning).
    3. `🔴 Abort & Physical Rollback` (Merah).

---

### Screen 5: 💰 Fleet Financial Governance & Budget Autopilot

- **Speedometer Gauge 24h Spend:**
  - Lingkaran speedometer futuristik dengan penunjuk jarum bercahaya.
  - Tiga zona warna: Hijau ($0 - 70\%$), Kuning Warning ($70 - 90\%$), Merah Hard-Stop ($90 - 100\%$).
- **Role-Based Expenditure Matrix:**
  - Bar chart komparasi biaya antar role (`CoderAgent` vs `DevOps` vs `Researcher`).
- **Dynamic Quota Form:**
  - Input: Max Daily Fleet Budget ($\$$ USD).
  - Input: Max Single-Session Quota ($\$$ USD).
  - Slider: Warning Alert Threshold ($\%$).
  - Tombol: "Update Fleet Governor".

---

### Screen 6: 🔍 Forensic Session Inspector & Report Exporter

- **Session Explorer:**
  - Dropdown filter & pencarian session ID dengan badge status (`COMPLETED`, `HEALED`, `KILLED`).
- **Deep Step-by-Step Chronological Forensic Table:**
  - Kolom: Step #, Tool, Tokens (Prompt/Comp), Cost ($), Latency (ms), TabPFN Score, Mode, Decision, Action Reason.
  - Expandable drawer untuk melihat full JSON prompt telemetry.
- **Executive Report Generator Modal:**
  - Pilih format: `Markdown (.md)`, `Stylized HTML (.html)`, `JSON-LD Audit Trail`.
  - Preview report langsung di browser dengan formatting tabel, metrik penghematan biaya, dan rekomendasi remediation.
  - Tombol: "Download Audit Report".

---

### Screen 7: 📊 Empirical Benchmark Suite (SWE-bench)

- **Benchmark Summary Matrix:**
  - Tabel komparasi 4 arsitektur: Heuristic Rule, Random Forest (50 trees), XGBoost (50 trees), dan **Agentry + TabPFN-3.5 Engine**.
  - Metrik: Failure Recall ($\% \pm \sigma$), False Stop Rate ($\% \pm \sigma$), Cost MAE ($\$$), Cost $R^2$.
- **Key Highlight Banners:**
  - 🏆 *"TabPFN achieves $R^2 = 0.782$ on unseen trajectory cost regression (nearly 4x higher than XGBoost)."*
  - 🎯 *"Agentry's Economic Utility Policy slashes false-stop rate to 2.0% while retaining 90.6% failure recall."*

---

## ⚡ 5. Micro-Interactions, Animation & Component Guidelines

1. **Pulse Beacon Health:**
   - Semua status indikator online/idle menggunakan CSS keyframe animation `pulse` berdurasi 2 detik dengan box-shadow bercahaya.
2. **TabPFN Inference Spinner / Flash:**
   - Ketika step baru diaudit (< 20ms), kartu agen memberikan kilatan halus (*subtle cyan highlight flash*) yang menandakan evaluasi tabular selesai.
3. **Danger Modal Shaking:**
   - Ketika tombol `KILL` ditekan, modal konfirmasi menampilkan border merah dengan animasi subtle shake untuk mencegah ketidaksengajaan operator.
4. **Number Counter Easing:**
   - Angka metrik (Tokens Saved, Dollars Saved) menggunakan animasi easing counter (*count-up*) saat dashboard dibuka.
5. **Toast Notifications:**
   - Gunakan Sonner / Radix Toast di pojok kanan atas untuk event instan (misal: *"Secret Redacted"*, *"HITL Request Enqueued"*, *"Filesystem Restored"*).

---

## 💻 6. Recommended Modern Tech Stack

Jika membangun web frontend dedicated (rekomendasi terbaik di luar Streamlit):

| Layer | Recommended Technology | Alasan Pemilihan |
| :--- | :--- | :--- |
| **Framework** | **Next.js 15 (App Router, React 19)** | Server Components, streaming response, lightning speed |
| **Styling** | **Tailwind CSS v4 + Tailwind Animate** | Utility-first, konsistensi token desain |
| **Component Kit** | **Shadcn UI + Radix Primitives** | Aksesibilitas WCAG AA, full customizability, unstyled core |
| **Iconography** | **Lucide React** | Ikon clean, modern, konsisten |
| **Charts** | **Recharts + Tremor + Plotly.js** | Visualisasi data interaktif finansial & ML |
| **Graph Visualizer** | **React Flow (`@xyflow/react`)** | Visualisasi multi-agent swarm directed DAG yang smooth |
| **Motion** | **Framer Motion** | Animasi perpindahan tab, layout morphing, modal transition |
| **State & API** | **TanStack Query (React Query) + Zustand** | Caching, revalidation, dan polling/SSE synchronization |

---

## 🤖 7. Master AI Prompt Template (Copy-Paste Ready)

*Gunakan prompt di bawah ini untuk menginstruksikan AI generator (v0, Cursor, Claude 3.7) untuk membuat halaman/komponen:*

```markdown
You are an elite Principal Frontend Architect specializing in high-stakes Cyber Defense Command Centers, SOC Dashboards, and Mission Control UI for Autonomous AI Agent Fleets.

Your task is to build the front-end for "Agentry", an autonomous tabular guardrail powered by Prior Labs TabPFN-3.5 foundation model.

### Visual & Technical Requirements:
1. Tech Stack: Next.js 15 (App Router), TypeScript, Tailwind CSS, Shadcn UI, Lucide Icons, Framer Motion, Recharts.
2. Theme: Cyber-Sentry Dark Mode:
   - Backgrounds: Canvas #07090E, Surface #0F172A, Secondary #1E293B.
   - Accents: TabPFN Emerald #00FF87, Sentry Cyan #60EFFF, Alert Amber #F59E0B, Circuit-Breaker Red #EF4444, Active Memory Violet #8B5CF6.
   - Typography: Space Grotesk / Inter for titles, JetBrains Mono for metrics and traces.
3. Top Navigation:
   - Agentry Shield Logo with pulse glow.
   - TabPFN-3.5 Cloud Engine status badge (Thinking Mode active, ~15ms latency).
   - 24h Spend progress gauge ($4.12 / $25.00 USD).
   - Active HITL Alert counter with notification bell.
4. Core Sections:
   - Real-Time Fleet Radar: 4 concurrent agent cards (Coder, DevOps, Research, Analyst) with dynamic risk ring (TabPFN failure prob), latency, tool execution chip, and typewriter thought trace.
   - Active Defense Sandbox:
     a) Semantic Blast-Radius Evaluator with preset test buttons (rm -rf /, DROP TABLE, pytest) and danger gauge.
     b) In-Flight DLP secret masker with split before/after view.
     c) Swarm Deadlock DAG visualizer detecting ping-pong loops (A -> B -> A -> B).
     d) Active In-Context Memory table showing verified incidents.
   - What-If Policy Simulator: Interactive sliders for risk threshold theta, error streak, and repetition cutoff, showing live token/cost savings.
   - HITL Approval War Room: Queue of paused sessions with action buttons (Approve, Steer Directive, Abort & Physical Rollback).
   - Forensic Inspector & Report Exporter: Chronological step timeline with Markdown/HTML audit download modal.

Deliver ultra-clean, accessible, modular, production-ready TypeScript code with realistic mock telemetry and fluid micro-interactions.
```

---

## ✅ 8. Verification & Acceptance Checklist

- [ ] **Data Density:** Dashboard menampilkan metrik teknis tanpa membuat viewport terasa sempit.
- [ ] **Response Time Indication:** Visualisasi memperlihatkan kecepatan inferensi sub-20ms TabPFN.
- [ ] **Safety Transparency:** Alasan intervensi (`KILL`, `REROUTE`, `PAUSE`) selalu memaparkan *root cause* tabular (streak error, repetisi, latensi, atau keyword).
- [ ] **Dual-Layer Defense Visuals:** Pembedaan jelas antara Layer 1 (Deterministik: Blast Radius & DLP) dan Layer 2 (Statistik Tabular: TabPFN-3.5).
- [ ] **100% Zero-Leakage Privacy Banner:** Menegaskan bahwa telemetry dianalisis tanpa mengirim source code sensitif ke cloud umum.
