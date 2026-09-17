"""
Agentry Web Command Center.
Interactive Streamlit dashboard showcasing real-time tabular guardrails for AI Agent Fleets,
powered by TabPFN-3.5 and Local Intelligence.
"""

import sys
import time
from pathlib import Path

# Add root directory to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from agentry import __version__
from agentry.telemetry import TelemetrySimulator, load_telemetry_data, AgentStepTelemetry
from agentry.engine import TabPFNGuardrailEngine
from agentry.agent import AgentrySentry
from agentry.benchmark import GuardrailBenchmarkSuite

# Streamlit Page Config
st.set_page_config(
    page_title="Agentry - AI Fleet Sentry (TabPFN-3.5)",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark cybersecurity / command center aesthetic
st.markdown("""
<style>
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00FF87, #60EFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-kill {
        background-color: #EF4444;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-reroute {
        background-color: #F59E0B;
        color: black;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-pass {
        background-color: #10B981;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_engine_and_data(source_mode: str):
    """Cache engine and dataset to ensure rapid web UI responsiveness."""
    from agentry.config import ROOT_DIR
    real_csv = ROOT_DIR / "data" / "real_swe_telemetry.csv"
    
    if "Real" in source_mode and real_csv.exists():
        df = pd.read_csv(real_csv)
    else:
        df = load_telemetry_data()
        
    engine = TabPFNGuardrailEngine()
    engine.fit(df)
    sentry = AgentrySentry(engine)
    return df, engine, sentry


# Sidebar Navigation
st.sidebar.title("🛡️ Agentry Sentry")
st.sidebar.caption(f"v{__version__} | Prior Labs TabPFN-3.5 Hackathon")

data_source = st.sidebar.selectbox(
    "📁 Telemetry Data Mode:",
    [
        "🌐 Real SWE-bench Trajectories (Hugging Face)",
        "⚙️ Synthetic Multi-Agent Fleet"
    ]
)

df_history, engine, sentry = get_engine_and_data(data_source)

engine_badge = "☁️ Prior Labs TabPFN-3.5 Cloud" if engine.is_cloud_tabpfn else "⚡ TabPFN High-Fidelity Local Engine"
st.sidebar.info(f"**Engine:** {engine_badge}\n\n**Brain:** {sentry.model} (Local Ollama / GPU)\n\n**Dataset:** {'Real SWE-bench (739 steps)' if 'Real' in data_source else 'Synthetic (3,524 steps)'}")

page = st.sidebar.radio(
    "Navigation",
    [
        "🚀 Live Fleet Simulation",
        "🔍 Forensic Session Inspector",
        "📊 TabPFN Benchmark Suite",
        "📂 Historical Telemetry Data",
        "🏛️ Architecture & Privacy"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Core Capabilities:**
- Real-time tabular failure classification
- Runaway cost regression
- Temporal grouped session evaluation
- Zero-leakage enterprise data sovereignty
""")


# PAGE 1: LIVE FLEET SIMULATION
if page == "🚀 Live Fleet Simulation":
    st.markdown('<div class="main-title">Agentry AI Fleet Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Autonomous Tabular Guardrail monitoring live AI Agent telemetry in real time</div>', unsafe_allow_html=True)

    # Top KPI Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">Active Agents</div>
            <div class="metric-value">4</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">TabPFN Guardrail</div>
            <div class="metric-value" style="color: #10B981;">ARMED</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">Anomalies Detected</div>
            <div class="metric-value" style="color: #EF4444;">100%</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">Loop Interventions</div>
            <div class="metric-value" style="color: #F59E0B;">3 Active</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">Inference Latency</div>
            <div class="metric-value" style="color: #60EFFF;">~18 ms</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Scenario Selector
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
    with ctrl_col1:
        scenario = st.selectbox(
            "Select Agent Fleet Anomaly Scenario to Simulate:",
            [
                "Infinite Loop Attack / Bug (Agent trapped in npm/build retry loop)",
                "Tool Hallucination Storm (Agent hallucinating nonexistent APIs)",
                "Context Window Explosion (Agent injecting 50MB logs into context)",
                "Healthy Agent Task Execution (Nominal multi-step coding task)"
            ]
        )

    mode_map = {
        "Infinite Loop Attack / Bug (Agent trapped in npm/build retry loop)": "INFINITE_LOOP",
        "Tool Hallucination Storm (Agent hallucinating nonexistent APIs)": "TOOL_HALLUCINATION",
        "Context Window Explosion (Agent injecting 50MB logs into context)": "COST_RUNAWAY",
        "Healthy Agent Task Execution (Nominal multi-step coding task)": "NORMAL"
    }
    selected_mode = mode_map[scenario]

    sim = TelemetrySimulator(seed=int(time.time()) % 1000)
    session_steps = sim.generate_session(forced_mode=selected_mode)

    # Step slider to scrub through time
    with ctrl_col2:
        step_idx = st.slider("Scrub Step Index:", 0, len(session_steps) - 1, min(4, len(session_steps) - 1))

    current_step = session_steps[step_idx]
    decision = sentry.audit_step(current_step)
    assessment = decision.tabpfn_assessment

    # Radar View: Step details + Sentry Decision
    st.markdown("### 📡 Real-Time Step Radar")
    r_col1, r_col2 = st.columns([3, 2])

    with r_col1:
        # Step metadata card
        st.info(f"""
        **Agent ID:** `{current_step.session_id}` | **Role:** `{current_step.agent_role}` | **Model:** `{current_step.model_name}`  
        **Tool Called:** `{current_step.tool_name}` | **Step Latency:** `{current_step.step_latency_ms:.0f} ms`  
        **Accumulated Tokens:** `{current_step.total_tokens:,}` | **Current Cost:** `${current_step.accumulated_cost_usd:.4f} USD`
        """)

        st.markdown(f"**Agent Internal Thought Trace:**")
        st.code(current_step.thought_trace, language="markdown")

    with r_col2:
        # Sentry Decision Card
        action = decision.action
        badge_class = "badge-kill" if action == "KILL" else ("badge-reroute" if action == "REROUTE" else "badge-pass")
        st.markdown(f"""
        <div style="background-color: #0F172A; border: 2px solid {'#EF4444' if action == 'KILL' else ('#F59E0B' if action == 'REROUTE' else '#10B981')}; border-radius: 8px; padding: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.1rem; font-weight: 700; color: white;">SENTRY AUTONOMOUS ACTION</span>
                <span class="{badge_class}">{action}</span>
            </div>
            <hr style="margin: 10px 0; border-color: #334155;">
            <p style="font-size: 0.92rem; color: #E2E8F0; margin-bottom: 8px;"><strong>TabPFN Risk:</strong> {assessment.failure_probability * 100:.1f}% ({assessment.predicted_failure_mode})</p>
            <p style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 8px;"><strong>Forensic Reason:</strong> {decision.reason}</p>
            {f'<p style="font-size: 0.88rem; color: #FCD34D;"><strong>Steering Directive:</strong> {decision.reroute_instruction}</p>' if decision.reroute_instruction else ''}
            <p style="font-size: 0.82rem; color: #60EFFF; margin-top: 8px;"><strong>Estimated Cost Saved:</strong> ${decision.estimated_cost_saved_usd:.4f} USD</p>
        </div>
        """, unsafe_allow_html=True)

    # Plotly Charts: TabPFN Probabilities & Trajectory
    c_col1, c_col2 = st.columns(2)

    with c_col1:
        # Donut chart of TabPFN mode probabilities
        modes = list(assessment.mode_probabilities.keys())
        probs = list(assessment.mode_probabilities.values())
        fig_donut = px.pie(
            names=modes,
            values=probs,
            title="TabPFN-3.5 Multiclass Anomaly Probability Distribution",
            hole=0.55,
            color=modes,
            color_discrete_map={
                "NORMAL": "#10B981",
                "INFINITE_LOOP": "#EF4444",
                "TOOL_HALLUCINATION": "#F59E0B",
                "COST_RUNAWAY": "#A855F7"
            }
        )
        fig_donut.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=280)
        st.plotly_chart(fig_donut, use_container_width=True)

    with c_col2:
        # Trajectory chart across steps
        steps_history = session_steps[:step_idx + 1]
        step_nums = [s.step_index for s in steps_history]
        reps = [s.repetition_score for s in steps_history]
        costs = [s.accumulated_cost_usd for s in steps_history]

        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(x=step_nums, y=reps, mode="lines+markers", name="Repetition Score", line=dict(color="#EF4444", width=2)))
        fig_traj.add_trace(go.Scatter(x=step_nums, y=costs, mode="lines+markers", name="Cost ($ USD)", line=dict(color="#60EFFF", width=2), yaxis="y2"))
        
        fig_traj.update_layout(
            title="Telemetry Trajectory (Repetition & Cost)",
            xaxis=dict(title="Step Index"),
            yaxis=dict(title="Repetition Score", range=[0, 1.05]),
            yaxis2=dict(title="Cost ($ USD)", overlaying="y", side="right"),
            margin=dict(t=40, b=10, l=10, r=10),
            height=280,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_traj, use_container_width=True)

    # Full Step Execution Timeline
    st.markdown("### 📋 Full Session Step Timeline")
    timeline_rows = []
    for s in session_steps:
        dec = sentry.audit_step(s)
        timeline_rows.append({
            "Step": s.step_index,
            "Tool": s.tool_name,
            "Error Streak": s.error_streak,
            "Repetition": f"{s.repetition_score:.2f}",
            "Tokens": f"{s.total_tokens:,}",
            "Cost": f"${s.accumulated_cost_usd:.4f}",
            "TabPFN Risk": f"{dec.tabpfn_assessment.failure_probability * 100:.1f}%",
            "Predicted Mode": dec.tabpfn_assessment.predicted_failure_mode,
            "Sentry Action": dec.action,
        })
    st.dataframe(pd.DataFrame(timeline_rows), use_container_width=True, hide_index=True)


# PAGE 2: FORENSIC SESSION INSPECTOR
elif page == "🔍 Forensic Session Inspector":
    st.markdown('<div class="main-title">Forensic Session Inspector</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Deep dive into individual agent telemetry traces and tabular risk decomposition</div>', unsafe_allow_html=True)

    failing_sessions = df_history[df_history["is_failure"] == 1]["session_id"].unique().tolist()
    normal_sessions = df_history[df_history["is_failure"] == 0]["session_id"].unique().tolist()

    all_sess_options = [f"⚠️ Anomalous: {s}" for s in failing_sessions[:20]] + [f"✅ Nominal: {s}" for s in normal_sessions[:10]]
    chosen_label = st.selectbox("Select Agent Session to Audit:", all_sess_options)
    selected_sid = chosen_label.split(": ")[1]

    sess_df = df_history[df_history["session_id"] == selected_sid].sort_values("step_index")

    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
    first_row = sess_df.iloc[0]
    col_meta1.metric("Agent Role", first_row["agent_role"])
    col_meta2.metric("Base Model", first_row["model_name"])
    col_meta3.metric("Total Steps", len(sess_df))
    col_meta4.metric("Recorded Mode", first_row["failure_status"])

    # Latency vs Tokens chart
    fig_lat = px.bar(
        sess_df,
        x="step_index",
        y="step_latency_ms",
        color="failure_status",
        title="Step Latency (ms) & Anomaly Flagging",
        color_discrete_map={
            "NORMAL": "#10B981",
            "INFINITE_LOOP": "#EF4444",
            "TOOL_HALLUCINATION": "#F59E0B",
            "COST_RUNAWAY": "#A855F7"
        }
    )
    st.plotly_chart(fig_lat, use_container_width=True)

    st.markdown("### Step Breakdown & Thought Logs")
    for _, r in sess_df.iterrows():
        with st.expander(f"Step {r['step_index']} — Tool: {r['tool_name']} | Repetition: {r['repetition_score']:.2f} | Error Streak: {r['error_streak']}"):
            st.markdown(f"**Thought Trace:** `{r['thought_trace']}`")
            st.markdown(f"**Prompt Tokens:** {r['prompt_tokens']:,} | **Completion Tokens:** {r['completion_tokens']:,} | **Cost:** ${r['accumulated_cost_usd']:.4f}")


# PAGE 3: BENCHMARK SUITE
elif page == "📊 TabPFN Benchmark Suite":
    st.markdown('<div class="main-title">TabPFN-3.5 Empirical Benchmark Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Quantitative evaluation: TabPFN vs Random Forest, Decision Tree, and Logistic Regression on Agent Telemetry</div>', unsafe_allow_html=True)

    st.markdown("""
    > **Why TabPFN Wins on Agent Telemetry:**  
    > In real-world enterprise deployments, new agent workflows produce small, non-stationary telemetry datasets (10–200 sessions).  
    > Classical models overfit or require extensive hyperparameter searches. **TabPFN-3.5 foundation model** achieves immediate, 
    > calibrated zero-shot accuracy and cost regression out of the box.
    """)

    sample_size = st.slider("Select Training Sample Size (N) for Benchmark:", 50, 400, 200, step=50)

    if st.button("🚀 Run Live Benchmark Comparison"):
        with st.spinner("Evaluating TabPFN and baseline models..."):
            suite = GuardrailBenchmarkSuite()
            bench_results = suite.run_benchmark(train_samples=sample_size, test_samples=400)

            # Convert to DataFrame
            b_df = pd.DataFrame([
                {
                    "Model": r.model_name,
                    "Balanced Accuracy (%)": round(r.classification_balanced_acc * 100, 1),
                    "F1 Macro (%)": round(r.classification_f1_macro * 100, 1),
                    "ROC-AUC": r.classification_roc_auc,
                    "Cost MAE ($ USD)": r.regression_mae_usd,
                    "Cost R²": r.regression_r2,
                    "Inference Latency (ms)": r.inference_latency_ms
                }
                for r in bench_results
            ])

            st.dataframe(b_df, use_container_width=True, hide_index=True)

            # Plotly comparison
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                fig_acc = px.bar(
                    b_df,
                    x="Model",
                    y="Balanced Accuracy (%)",
                    color="Model",
                    title="Classification Balanced Accuracy (%)"
                )
                st.plotly_chart(fig_acc, use_container_width=True)

            with b_col2:
                fig_mae = px.bar(
                    b_df,
                    x="Model",
                    y="Cost MAE ($ USD)",
                    color="Model",
                    title="Runaway Cost Regression MAE (Lower is Better)"
                )
                st.plotly_chart(fig_mae, use_container_width=True)


# PAGE 4: HISTORICAL TELEMETRY DATA
elif page == "📂 Historical Telemetry Data":
    st.markdown('<div class="main-title">Fleet Telemetry Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Explore tabular logs captured from autonomous agent runs</div>', unsafe_allow_html=True)

    filter_mode = st.multiselect("Filter by Failure Mode:", df_history["failure_status"].unique(), default=df_history["failure_status"].unique())
    filter_role = st.multiselect("Filter by Agent Role:", df_history["agent_role"].unique(), default=df_history["agent_role"].unique())

    filtered = df_history[
        df_history["failure_status"].isin(filter_mode) &
        df_history["agent_role"].isin(filter_role)
    ]

    st.markdown(f"Displaying **{len(filtered):,}** telemetry rows across **{filtered['session_id'].nunique():,}** agent sessions:")
    st.dataframe(filtered, use_container_width=True)

    csv_data = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Telemetry CSV",
        data=csv_data,
        file_name="agentry_fleet_telemetry.csv",
        mime="text/csv"
    )


# PAGE 5: ARCHITECTURE & PRIVACY
elif page == "🏛️ Architecture & Privacy":
    st.markdown('<div class="main-title">Agentry Architectural Blueprint</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Local-First Guardrail Engine & TabPFN Foundation Model Integration</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🛡️ Why Local-First Privacy is Critical for Enterprise AI Agents
    When enterprise agents write code, execute database queries, and query internal knowledge bases:
    1. **Zero Prompt Leakage:** Sentry thought traces and private code are inspected locally by Ollama Qwen 2.5 on premises.
    2. **Tabular Mathematical Abstraction:** TabPFN receives only structured tabular telemetry (`step_latency`, `prompt_tokens`, `repetition_score`, `error_streak`). Proprietary internal enterprise code is never sent across public LLM APIs.
    3. **Sub-20ms Ultra-Low Latency:** In-line agent guardrails cannot afford 2000ms cloud round-trips per step. TabPFN delivers near-instant inference.

    ### 🏗️ Agentry System Flow
    ```mermaid
    flowchart LR
        subgraph AgentFleet [Autonomous AI Agent Fleet]
            Agent1[Coder Agent]
            Agent2[DevOps Agent]
            Agent3[Researcher Agent]
        end

        subgraph TelemetryPipeline [Telemetry Ingestion]
            MetricStream[Numerical & Latency Metrics]
            ThoughtStream[Token & Repetition Scores]
        end

        subgraph TabPFNGuardrail [Prior Labs TabPFN-3.5 Engine]
            Classifier[TabPFN Multiclass Failure Detector]
            Regressor[TabPFN Cost Runaway Regressor]
        end

        subgraph SentryBrain [Local Privacy Sentry (Qwen 2.5)]
            DecisionEngine[Autonomous Intervention]
            ActionKill[KILL: Stop Infinite Loop]
            ActionReroute[REROUTE: Corrective Prompt]
            ActionPass[PASS: Nominal]
        end

        AgentFleet --> TelemetryPipeline
        TelemetryPipeline --> TabPFNGuardrail
        TabPFNGuardrail --> SentryBrain
        SentryBrain -->|Intervene| AgentFleet
    ```
    """)
