"""
PharmaShield - Shared Type System Enforcements
"""

from __future__ import annotations
from typing import TypedDict, Union


class SafetyMetricsPayload(TypedDict):
    """Typed relational metrics payload passed across engine layers."""

    drug: str
    reaction: str
    total_cases: int
    severe_cases: int
    average_age_years: Union[float, str, None]