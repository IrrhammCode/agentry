"""
Agentry: The Autonomous Tabular Guardrail & Sentry for AI Agents.
Powered by TabPFN-3.5 and Local-First Intelligence (Qwen 2.5 via Ollama).
"""

__version__ = "0.1.0"
__author__ = "Agentry Team"

from agentry.telemetry import TelemetrySimulator, load_telemetry_data
from agentry.engine import TabPFNGuardrailEngine
from agentry.agent import AgentrySentry, SentryDecision
from agentry.guard import AgentryGuard, AgentHaltException, StepContext
from agentry.integrations import AgentryLangChainCallback, AgentryCrewHook

__all__ = [
    "TelemetrySimulator",
    "load_telemetry_data",
    "TabPFNGuardrailEngine",
    "AgentrySentry",
    "SentryDecision",
    "AgentryGuard",
    "AgentHaltException",
    "StepContext",
    "AgentryLangChainCallback",
    "AgentryCrewHook",
]
