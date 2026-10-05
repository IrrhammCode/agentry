"""
Audit script for identifying mocks, hardcoded data, and technical weaknesses.
"""

import re
from pathlib import Path

def audit():
    print("=" * 70)
    print(">>> CODEBASE WEAKNESS & MOCK AUDIT REPORT")
    print("=" * 70)

    # 1. Audit Frontend Views
    frontend_dir = Path("frontend/src")
    print("\n[1] Auditing Frontend TypeScript/React Code...")

    findings = []
    for p in frontend_dir.rglob("*.tsx"):
        content = p.read_text(encoding="utf-8")
        lines = content.splitlines()

        for idx, line in enumerate(lines):
            # Check for hardcoded fallbacks
            if "??" in line or "||" in line:
                if any(k in line for k in ["1727", "1587", "81", "39", "18", "99.2", "14.8"]):
                    findings.append((p.name, idx + 1, "Hardcoded metric fallback", line.strip()))
            
            # Check for static data arrays
            if re.search(r'const\s+(?:DEFAULT_|MOCK_|SAMPLE_|STATIC_|[A-Z_]*DATA)\w*\s*=\s*\[', line):
                findings.append((p.name, idx + 1, "Static data constant", line.strip()))
            
            # Check for mock or fake keywords
            if re.search(r'\b(mock|fake|dummy)\b', line, re.IGNORECASE):
                findings.append((p.name, idx + 1, "Mock/Fake keyword reference", line.strip()))

    for f in findings:
        print(f"  - [{f[0]}:{f[1]}] {f[2]}: {f[3][:90]}")

    # 2. Audit Backend agentry/
    print("\n[2] Auditing Backend agentry/ Module for Simulated / Fallback Logic...")
    backend_dir = Path("agentry")
    backend_findings = []
    for p in backend_dir.rglob("*.py"):
        content = p.read_text(encoding="utf-8")
        lines = content.splitlines()

        for idx, line in enumerate(lines):
            # Check for mock/fake/simulate
            if re.search(r'\b(mock|fake|dummy|stub)\b', line, re.IGNORECASE) and "test" not in p.name:
                backend_findings.append((p.name, idx + 1, "Mock/Stub reference", line.strip()))
            
            # Check for heuristic fallbacks
            if "fallback" in line.lower() or "heuristic" in line.lower():
                backend_findings.append((p.name, idx + 1, "Fallback/Heuristic mechanism", line.strip()))

    for f in backend_findings[:15]:
        print(f"  - [{f[0]}:{f[1]}] {f[2]}: {f[3][:90]}")

    print("\nAudit completed.")

if __name__ == "__main__":
    audit()
