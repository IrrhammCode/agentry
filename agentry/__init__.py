"""
Agentry: The Autonomous Tabular Guardrail & Sentry for AI Agents.
Powered by TabPFN-3.5 and Local-First Intelligence (Qwen 2.5 via Ollama).
"""

__version__ = "0.1.0"
__author__ = "Agentry Team"

from agentry.telemetry import TelemetrySimulator, load_telemetry_data
from agentry.engine import TabPFNGuardrailEngine, StepRiskAssessment
from agentry.agent import AgentrySentry, SentryDecision
from agentry.guard import AgentryGuard, AgentHaltException, StepContext
from agentry.healing import TrajectoryHealer, RewindPrescription, trajectory_healer
from agentry.checkpoint import StateCheckpointer, state_checkpointer, physical_checkpointer
from agentry.blast_radius import BlastRadiusEvaluator, blast_radius_evaluator, BlastRadiusAssessment
from agentry.dlp import SecretRedactionEngine, secret_redactor, RedactionResult
from agentry.swarm import SwarmDeadlockDetector, swarm_detector, swarm_deadlock_detector, SwarmDeadlockAlert

from agentry.active_memory import ActiveExemplarBuffer, active_exemplar_memory, VerifiedIncidentExemplar
from agentry.integrations import AgentryLangChainCallback, AgentryCrewHook

__all__ = [
    "TelemetrySimulator",
    "load_telemetry_data",
    "TabPFNGuardrailEngine",
    "StepRiskAssessment",
    "AgentrySentry",
    "SentryDecision",
    "AgentryGuard",
    "AgentHaltException",
    "StepContext",
    "TrajectoryHealer",
    "RewindPrescription",
    "trajectory_healer",
    "StateCheckpointer",
    "state_checkpointer",
    "physical_checkpointer",
    "BlastRadiusEvaluator",
    "blast_radius_evaluator",
    "BlastRadiusAssessment",
    "SecretRedactionEngine",
    "secret_redactor",
    "SwarmDeadlockDetector",
    "swarm_detector",
    "swarm_deadlock_detector",
    "SwarmDeadlockAlert",
    "ActiveExemplarBuffer",
    "active_exemplar_memory",
    "VerifiedIncidentExemplar",
    "AgentryLangChainCallback",
    "AgentryCrewHook",
]

