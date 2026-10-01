"""
In-Flight Data Loss Prevention (DLP) & Secret Masking Engine for Agentry.
Automatically intercepts, detects, and redacts sensitive credentials, API keys,
passwords, and private keys from agent tool inputs, outputs, and audit logs
before they are written to disk or sent to downstream LLMs.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Any, Union

logger = logging.getLogger("agentry.dlp")


@dataclass
class RedactionResult:
    """Structured result from in-flight secret scanning and redaction."""
    masked_text: str
    redaction_count: int
    detected_secrets: List[Dict[str, Any]] = field(default_factory=list)

    def __iter__(self):
        yield self.masked_text
        yield self.redaction_count

    def __getitem__(self, idx: int):
        return (self.masked_text, self.redaction_count)[idx]

    def __len__(self) -> int:
        return 2


class SecretRedactionEngine:
    """
    High-performance compiled regex engine for scanning and redacting secrets in-flight.
    """

    PATTERNS: List[Tuple[str, str, re.Pattern]] = [

        # Anthropic API Keys (must precede generic OpenAI sk- pattern)
        ("ANTHROPIC_KEY", r"sk-ant-[a-zA-Z0-9_\-]{32,}", re.compile(r"sk-ant-[a-zA-Z0-9_\-]{32,}")),
        # OpenAI API Keys
        ("OPENAI_KEY", r"sk-[a-zA-Z0-9_\-]{32,}", re.compile(r"sk-[a-zA-Z0-9_\-]{32,}")),
        # Groq API Keys
        ("GROQ_KEY", r"gsk_[a-zA-Z0-9_\-]{32,}", re.compile(r"gsk_[a-zA-Z0-9_\-]{32,}")),
        # GitHub Personal Access Tokens
        ("GITHUB_PAT", r"(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}", re.compile(r"(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}")),
        ("GITHUB_FINE_GRAINED", r"github_pat_[a-zA-Z0-9_]{40,}", re.compile(r"github_pat_[a-zA-Z0-9_]{40,}")),
        # AWS Access Key IDs
        ("AWS_KEY_ID", r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b", re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b")),
        # Google Cloud / Gemini API Keys
        ("GOOGLE_KEY", r"AIzaSy[0-9A-Za-z\-_]{33}", re.compile(r"AIzaSy[0-9A-Za-z\-_]{33}")),
        # Slack Tokens
        ("SLACK_TOKEN", r"xox[baprs]-[0-9]{10,}-[0-9a-zA-Z]{10,}", re.compile(r"xox[baprs]-[0-9]{10,}-[0-9a-zA-Z]{10,}")),
        # Database Connection Strings with Passwords
        (
            "DB_CONN_STRING",
            r"(postgres(ql)?|mysql|mongodb|redis)://[a-zA-Z0-9_.\-]+:[^@\s]+@[a-zA-Z0-9.\-_]+(:\d+)?/[a-zA-Z0-9_\-]+",
            re.compile(r"(postgres(ql)?|mysql|mongodb|redis)://([a-zA-Z0-9_.\-]+):([^@\s]+)@([a-zA-Z0-9.\-_]+(:\d+)?/[a-zA-Z0-9_\-]+)")
        ),
        # Private Keys
        (
            "PRIVATE_KEY",
            r"-----BEGIN (RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?-----END (RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----",
            re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?-----END (RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")
        ),
    ]

    def redact(self, text: str) -> RedactionResult:
        """
        Redacts all detected sensitive secrets from the input string.
        Returns:
            RedactionResult (supports unpacking as (sanitized_text, count))
        """
        if not text or not isinstance(text, str):
            return RedactionResult(str(text or ""), 0, [])

        # Fast-path check: if text doesn't contain any secret triggers, skip regex scanning
        triggers = ("sk-", "gsk_", "ghp_", "AKIA", "ASIA", "AIza", "xox", "://", "PRIVATE KEY")
        if not any(t in text for t in triggers):
            return RedactionResult(text, 0, [])

        sanitized = text
        total_redacted = 0
        detected = []

        for key_type, _, pattern in self.PATTERNS:
            if key_type == "DB_CONN_STRING":
                # Specially handle DB URLs to only mask password, preserving protocol and host
                def mask_db_pwd(match):
                    nonlocal total_redacted
                    total_redacted += 1
                    proto = match.group(1)
                    user = match.group(3)
                    rest = match.group(5)
                    return f"{proto}://{user}:[REDACTED_PASSWORD]@{rest}"
                sanitized = pattern.sub(mask_db_pwd, sanitized)
                detected.append({"type": key_type, "count": 1})
            else:
                matches = pattern.findall(sanitized)
                if matches:
                    count = len(matches)
                    total_redacted += count
                    detected.append({"type": key_type, "count": count})
                    sanitized = pattern.sub(f"[REDACTED_{key_type}]", sanitized)

        if total_redacted > 0:
            logger.info("DLP Engine: Redacted %d sensitive secret(s) from in-flight payload", total_redacted)

        return RedactionResult(sanitized, total_redacted, detected)

    # Alias for API ergonomics
    redact_secrets = redact



# Global singleton instance
secret_redactor = SecretRedactionEngine()
