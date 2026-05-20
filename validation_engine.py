"""
PharmaShield - Deterministic Validation Engine
Verifies generated clinical narratives against relational database metrics.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Union, TypedDict

# -------------------------------------------------------------------
# STRONG TYPING INTERFACES
# -------------------------------------------------------------------


class SafetyMetricsPayload(TypedDict):
    """Typed relational metrics payload passed into the validation layer."""

    drug: str
    reaction: str
    total_cases: int
    severe_cases: int
    average_age_years: Union[float, str, None]


@dataclass(frozen=True)
class ValidationResult:
    """Immutable deterministic validation verdict."""

    is_verified: bool
    matched_tokens: int
    drift_detected: bool
    reason: str


# -------------------------------------------------------------------
# INTERNAL VALIDATION HELPERS
# -------------------------------------------------------------------


def extract_numeric_tokens(narrative: str) -> set[str]:
    """
    Extract normalized numeric tokens from generated narrative text.
    """
    return set(re.findall(r"\d+", narrative))


# -------------------------------------------------------------------
# CORE VALIDATION LAYER
# -------------------------------------------------------------------


def verify_narrative_alignment(
    metrics: SafetyMetricsPayload,
    narrative: str,
) -> ValidationResult:
    """
    Cross-reference semantic narrative output against deterministic
    relational database metrics.
    """
    total_cases = metrics.get("total_cases", 0)
    severe_cases = metrics.get("severe_cases", 0)

    # No statistical evidence exists to validate against
    if total_cases == 0:
        return ValidationResult(
            is_verified=True,
            matched_tokens=0,
            drift_detected=False,
            reason="No relational evidence available for validation.",
        )

    required_tokens = {
        str(total_cases),
        str(severe_cases),
    }

    narrative_tokens = extract_numeric_tokens(narrative)
    matched_tokens = len(required_tokens.intersection(narrative_tokens))
    drift_detected = matched_tokens == 0

    if drift_detected:
        return ValidationResult(
            is_verified=False,
            matched_tokens=matched_tokens,
            drift_detected=True,
            reason="Generated narrative omitted deterministic statistical evidence.",
        )

    return ValidationResult(
        is_verified=True,
        matched_tokens=matched_tokens,
        drift_detected=False,
        reason="Narrative aligned with relational evidence layer.",
    )