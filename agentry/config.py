"""
Configuration module for Agentry.
Loads environment variables and sets system defaults.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env file from project root if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _parse_groq_keys() -> list[str]:
    raw = os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", ""))
    if not raw:
        return []
    import re
    return [k.strip() for k in re.split(r"[,;\s\n]+", raw) if k.strip()]


class AgentryConfig(BaseModel):
    """Global configuration settings for Agentry."""

    # TabPFN Settings
    tabpfn_token: str = Field(
        default_factory=lambda: os.getenv("TABPFN_TOKEN", os.getenv("PRIORLABS_API_KEY", ""))
    )
    tabpfn_use_thinking: bool = Field(
        default_factory=lambda: os.getenv("TABPFN_THINKING_MODE", "true").lower() in ("true", "1", "yes")
    )
    tabpfn_n_estimators: int = 8

    # Provider Selection ('auto', 'groq', 'ollama', 'rule')
    sentry_provider: str = Field(
        default_factory=lambda: os.getenv("SENTRY_PROVIDER", "auto").lower()
    )

    # Groq Settings (Supports multi-key pool for automatic rotation)
    groq_api_keys: list[str] = Field(default_factory=_parse_groq_keys)
    groq_model: str = Field(
        default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    )
    groq_base_url: str = Field(
        default_factory=lambda: os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    )

    # Local Sentry Brain (Ollama or OpenAI-compatible endpoint)
    ollama_base_url: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    )
    sentry_model: str = Field(
        default_factory=lambda: os.getenv("SENTRY_MODEL", "qwen2.5:3b")
    )
    enable_cloud_llm_fallback: bool = False
    openai_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )

    # Autonomous Guardrail Thresholds
    risk_threshold_pause: float = 0.60   # TabPFN probability >= 60% triggers PAUSE & inspect
    risk_threshold_kill: float = 0.85    # TabPFN probability >= 85% triggers autonomous KILL
    cost_threshold_warning_usd: float = 1.00  # Warn if projected cost exceeds $1.00
    cost_threshold_kill_usd: float = 2.50     # Auto-kill if cost exceeds $2.50
    repetition_score_kill: float = 0.85      # Severe loop detection
    error_streak_kill: int = 5               # 5 consecutive tool failures

    # Data paths
    data_dir: Path = ROOT_DIR / "data"
    real_dataset_path: Path = ROOT_DIR / "data" / "real_swe_telemetry.csv"
    default_dataset_path: Path = Field(
        default_factory=lambda: (
            ROOT_DIR / "data" / "real_swe_telemetry.csv"
            if (ROOT_DIR / "data" / "real_swe_telemetry.csv").exists()
            else ROOT_DIR / "data" / "agent_telemetry.csv"
        )
    )


# Singleton instance
settings = AgentryConfig()
