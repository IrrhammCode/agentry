"""
Defensive type conversion and mathematical sanitization utilities for Agentry.
Protects the TabPFN runtime against NaN, Infinite, None, and adversarial inputs.
"""

import math
from typing import Any, Optional


def safe_int(val: Any, default: int = 0, min_val: Optional[int] = 0) -> int:
    """Safely converts any input into an integer with NaN/Inf protection."""
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            i = default
        else:
            i = int(f)
    except (ValueError, TypeError):
        i = default
    if min_val is not None:
        i = max(min_val, i)
    return i


def safe_float(
    val: Any,
    default: float = 0.0,
    min_val: Optional[float] = 0.0,
    max_val: Optional[float] = None
) -> float:
    """Safely converts any input into a bounded float with NaN/Inf protection."""
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            f = default
    except (ValueError, TypeError):
        f = default
    if min_val is not None:
        f = max(min_val, f)
    if max_val is not None:
        f = min(max_val, f)
    return f


def safe_str(val: Any, default: str = "") -> str:
    """Safely converts any input into a clean string without NoneType exceptions."""
    if val is None:
        return default
    try:
        return str(val)
    except Exception:
        return default
