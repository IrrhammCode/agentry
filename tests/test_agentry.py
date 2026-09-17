"""
Unit and Integration Tests for Agentry.
"""

import pytest
import pandas as pd
import numpy as np

from agentry.telemetry import TelemetrySimulator, load_telemetry_data, AgentStepTelemetry
from agentry.engine import TabPFNGuardrailEngine, StepRiskAssessment
from agentry.agent import AgentrySentry, SentryDecision
from agentry.benchmark import GuardrailBenchmarkSuite


def test_telemetry_simulation():
    """Test synthetic telemetry data generation across failure modes."""
    sim = TelemetrySimulator(seed=123)
    
    # Test normal session
    norm_session = sim.generate_session(forced_mode="NORMAL")
    assert len(norm_session) >= 5
    assert all(isinstance(s, AgentStepTelemetry) for s in norm_session)
    assert all(s.failure_status == "NORMAL" for s in norm_session)
    assert all(s.repetition_score < 0.50 for s in norm_session)

    # Test loop session
    loop_session = sim.generate_session(forced_mode="INFINITE_LOOP")
    assert any(s.failure_status == "INFINITE_LOOP" for s in loop_session)
    failing_steps = [s for s in loop_session if s.failure_status == "INFINITE_LOOP"]
    assert len(failing_steps) > 0
    assert failing_steps[-1].repetition_score > 0.60

    # Test fleet dataset generator
    df = sim.generate_fleet_dataset(num_sessions=10)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 50
    assert "session_id" in df.columns
    assert "failure_status" in df.columns


def test_engine_fit_and_prediction():
    """Test TabPFN Guardrail Engine fitting and inference."""
    sim = TelemetrySimulator(seed=42)
    df = sim.generate_fleet_dataset(num_sessions=20)
    
    engine = TabPFNGuardrailEngine()
    engine.fit(df)
    assert engine.is_fitted is True

    # Test evaluating a single step
    test_step = sim.generate_session(forced_mode="NORMAL")[0]
    assessment = engine.evaluate_step(test_step)

    assert isinstance(assessment, StepRiskAssessment)
    assert 0.0 <= assessment.failure_probability <= 1.0
    assert assessment.predicted_failure_mode in ["NORMAL", "INFINITE_LOOP", "TOOL_HALLUCINATION", "COST_RUNAWAY"]
    assert assessment.projected_final_cost_usd >= 0.0
    assert assessment.uncertainty_score >= 0.0


def test_sentry_interventions():
    """Test Sentry autonomous interventions: PASS, REROUTE, and KILL."""
    sim = TelemetrySimulator(seed=42)
    df = sim.generate_fleet_dataset(num_sessions=20)
    
    engine = TabPFNGuardrailEngine()
    engine.fit(df)
    sentry = AgentrySentry(engine)

    # 1. Normal step should PASS
    normal_step = sim.generate_session(forced_mode="NORMAL")[0]
    dec_pass = sentry.audit_step(normal_step)
    assert dec_pass.action == "PASS"
    assert dec_pass.risk_level in ["NOMINAL", "MEDIUM"]

    # 2. Infinite loop steps should escalate to REROUTE or KILL
    loop_steps = sim.generate_session(forced_mode="INFINITE_LOOP")
    decisions = [sentry.audit_step(s) for s in loop_steps]
    actions = [d.action for d in decisions]

    assert "KILL" in actions or "REROUTE" in actions
    
    # Check that KILL calculates positive saved tokens and costs
    kill_decisions = [d for d in decisions if d.action == "KILL"]
    if kill_decisions:
        first_kill = kill_decisions[0]
        assert first_kill.estimated_tokens_saved >= 0
        assert first_kill.estimated_cost_saved_usd >= 0.0


def test_benchmark_suite_execution():
    """Test that benchmark suite runs and evaluates models without errors."""
    suite = GuardrailBenchmarkSuite()
    results = suite.run_benchmark(train_samples=50, test_samples=100)
    
    assert len(results) >= 3
    model_names = [r.model_name for r in results]
    assert any("Agentry" in name or "TabPFN" in name for name in model_names)
    assert any("Random Forest" in name for name in model_names)

    for r in results:
        assert 0.0 <= r.classification_balanced_acc <= 1.0
        assert r.regression_mae_usd >= 0.0
