"""
Semantic Blast-Radius & Destructive Action Interceptor for Agentry.
Protects physical filesystems, cloud environments, and databases from irreversible
catastrophic mutations executed by autonomous agents (e.g. `rm -rf /`, `DROP TABLE`,
credential tampering, or unconstrained deletes).
Evaluates action intent and blast radius BEFORE the agent tool executes.
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple

logger = logging.getLogger("agentry.blast_radius")


@dataclass
class BlastRadiusAssessment:
    """Assessment of the destructive potential of an agent action."""
    score: float  # 0.0 (benign) to 1.0 (catastrophic)
    category: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    is_blocked: bool  # True if action must be immediately halted
    recommended_action: str  # PASS, WARN, PAUSE, KILL
    violation_reason: Optional[str] = None
    matched_pattern: Optional[str] = None

    @property
    def is_critical(self) -> bool:
        return self.category == "CRITICAL" or self.is_blocked

    @property
    def severity(self) -> str:
        return self.category

    @property
    def reason(self) -> str:
        return self.violation_reason or ""

    @property
    def remediation(self) -> str:
        return self.violation_reason or "No remediation required."



class BlastRadiusEvaluator:
    """
    Evaluates tool execution commands, SQL statements, and file paths to determine
    the mutation blast radius before execution occurs.
    """

    CRITICAL_PATTERNS: List[Tuple[str, str]] = [
        # Filesystem destruction (Linux/macOS)
        (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f*\s+([/~*]|(\.\./){2,})", "Catastrophic recursive root/home deletion (rm -rf /)"),
        (r"\brm\s+-[a-zA-Z]*f*r[a-zA-Z]*\s+([/~*]|(\.\./){2,})", "Catastrophic recursive root/home deletion (rm -fr /)"),
        (r"\bmkfs(\.[a-z0-9]+)?\s+", "Filesystem format command (mkfs)"),
        (r"\bdd\s+.*of=(/dev/[a-z0-9]+)", "Direct raw disk write overwrite (dd of=/dev/...)"),
        # Filesystem destruction (Windows)
        (r"(?i)\bformat\s+[a-zA-Z]:", "Windows disk drive format"),
        (r"(?i)\bdel\s+/[sfaq]+\s+([a-zA-Z]:\\|\\)", "Windows recursive system root deletion (del /s /q C:\\)"),
        (r"(?i)\bRemove-Item\s+.*-Recurse\s+.*([a-zA-Z]:\\|\\)", "PowerShell recursive root deletion"),
        # Database destruction
        (r"(?i)\bDROP\s+(DATABASE|SCHEMA)\s+", "Irreversible database or schema drop (DROP DATABASE)"),
        (r"(?i)\bDROP\s+TABLE\s+", "Irreversible database table drop (DROP TABLE)"),
        (r"(?i)\bTRUNCATE\s+(TABLE\s+)?[a-zA-Z0-9_.]+", "Table truncation (TRUNCATE TABLE)"),
        (r"(?i)\bDELETE\s+FROM\s+[a-zA-Z0-9_.]+\s*(;|\s*$)", "Unconstrained bulk table deletion without WHERE clause"),
        # Remote Code Execution / Reverse Shell Pipe
        (r"\bcurl\s+[^|]+\|\s*(bash|sh|zsh|python|perl)\b", "Piping unverified remote web payload into shell interpreter"),
        (r"\bwget\s+[^|]+\|\s*(bash|sh|zsh|python|perl)\b", "Piping unverified remote web payload into shell interpreter"),
        (r"\bnc\s+.*-e\s+(/bin/[a-z]+|cmd\.exe|powershell)", "Reverse shell netcat execution (nc -e)"),
    ]

    HIGH_PATTERNS: List[Tuple[str, str]] = [
        (r"\bgit\s+push\s+.*(--force|-f)\b", "Destructive git force push rewriting remote repository history"),
        (r"\bchmod\s+(-[a-zA-Z]*R[a-zA-Z]*\s+)?777\s+", "Dangerous broad file permission grant (chmod 777)"),
        (r"\bchown\s+-[a-zA-Z]*R[a-zA-Z]*\s+root\s+", "Recursive ownership change to root"),
        (r"\b(rm|del)\s+.*\.git\b", "Deletion of version control repository directory (.git)"),
        (r"(?i)\b(rm|del|truncate)\s+.*(id_rsa|\.ssh|credentials|\.env)", "Attempting to destroy or overwrite credential/key files"),
    ]

    MEDIUM_PATTERNS: List[Tuple[str, str]] = [
        (r"\bgit\s+reset\s+--hard\b", "Git hard reset discarding working tree changes"),
        (r"\bkill\s+-9\s+1\b", "Attempting to terminate init / PID 1 process"),
        (r"(?i)\bDROP\s+VIEW\s+", "Dropping database view"),
    ]

    def evaluate(self, tool_name: str, action_input: str, session_id: Optional[str] = None) -> BlastRadiusAssessment:
        """
        Evaluates a prospective tool action input to assess blast radius.
        """
        tool = (tool_name or "").lower().strip()
        text = str(action_input or "").strip()

        # Tools that are inherently read-only have zero blast radius
        if tool in ("read_file", "grep_search", "web_search", "inspect_code", "list_dir"):
            return BlastRadiusAssessment(
                score=0.0,
                category="NONE",
                is_blocked=False,
                recommended_action="PASS"
            )

        # 1. Check for CRITICAL destructive patterns
        for pattern, reason in self.CRITICAL_PATTERNS:
            if re.search(pattern, text):
                logger.critical("BLAST RADIUS CRITICAL: Blocked action '%s' -> %s", tool, reason)
                return BlastRadiusAssessment(
                    score=1.0,
                    category="CRITICAL",
                    is_blocked=True,
                    recommended_action="KILL",
                    violation_reason=f"CRITICAL BLAST RADIUS VIOLATION: {reason}",
                    matched_pattern=pattern
                )

        # 2. Check for HIGH risk patterns
        for pattern, reason in self.HIGH_PATTERNS:
            if re.search(pattern, text):
                logger.warning("BLAST RADIUS HIGH: Quarantining action '%s' -> %s", tool, reason)
                return BlastRadiusAssessment(
                    score=0.75,
                    category="HIGH",
                    is_blocked=False,  # Can be routed to HITL quarantine
                    recommended_action="PAUSE",
                    violation_reason=f"HIGH BLAST RADIUS: {reason}",
                    matched_pattern=pattern
                )

        # 3. Check for MEDIUM risk patterns
        for pattern, reason in self.MEDIUM_PATTERNS:
            if re.search(pattern, text):
                return BlastRadiusAssessment(
                    score=0.40,
                    category="MEDIUM",
                    is_blocked=False,
                    recommended_action="WARN",
                    violation_reason=f"MEDIUM BLAST RADIUS: {reason}",
                    matched_pattern=pattern
                )

        # Nominal safe action
        return BlastRadiusAssessment(
            score=0.05 if tool in ("bash", "write_file", "edit_file") else 0.0,
            category="LOW" if tool in ("bash", "write_file", "edit_file") else "NONE",
            is_blocked=False,
            recommended_action="PASS"
        )


# Global singleton instance
blast_radius_evaluator = BlastRadiusEvaluator()
