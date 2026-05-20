"""
PharmaShield - Bounded Reasoning Engine
Handles localized inference orchestration, model parsing, and semantic typing.
"""

from __future__ import annotations

import re
import ollama
from dataclasses import dataclass
from typing import Union, TypedDict

# -------------------------------------------------------------------
# CUSTOM INFRASTRUCTURE EXCEPTIONS
# -------------------------------------------------------------------


class InferenceEngineError(Exception):
    """Raised when the local inference pipeline encounters a runtime fault."""

    pass


# -------------------------------------------------------------------
# STRONG TYPING INTERFACES
# -------------------------------------------------------------------


class SafetyMetricsPayload(TypedDict):
    """Typed relational metrics payload passed into the reasoning layer."""

    drug: str
    reaction: str
    total_cases: int
    severe_cases: int
    average_age_years: Union[float, str, None]


@dataclass(frozen=True)
class InferenceResult:
    """Immutable bounded semantic interpretation output."""

    reasoning_trace: str
    clinical_narrative: str


# -------------------------------------------------------------------
# PROMPT TEMPLATES
# -------------------------------------------------------------------

CLINICAL_REASONING_PROMPT = """
Analyze these metrics and summarize the clinical risk profile.

Strict rules:
- Only interpret the provided values.
- Do not introduce outside medical knowledge.
- Do not speculate beyond the metrics.

DRUG: {drug}
REACTION: {reaction}
TOTAL_CASES: {total_cases}
SEVERE_CASES: {severe_cases}
MEAN_AGE: {average_age}
"""

SYSTEM_PROMPT = (
    "You are a technical compliance auditor. "
    "Interpret metrics strictly without introducing external context."
)

# -------------------------------------------------------------------
# INTERNAL PARSING HELPERS
# -------------------------------------------------------------------


def extract_reasoning_trace(output_text: str) -> tuple[str, str]:
    """
    Extract optional reasoning traces from local model output.

    Returns:
        tuple[str, str]: (reasoning_trace, cleaned_narrative)
    """
    think_match = re.search(
        r"<think>(.*?)</think>",
        output_text,
        re.DOTALL,
    ) or re.search(
        r"<\|think\|>(.*?)</\|think\|>",
        output_text,
        re.DOTALL,
    )

    if not think_match:
        return (
            "No explicit reasoning trace returned by model.",
            output_text.strip(),
        )

    reasoning_trace = think_match.group(1).strip()
    cleaned_output = output_text.replace(think_match.group(0), "").strip()

    return reasoning_trace, cleaned_output


# -------------------------------------------------------------------
# CORE INFERENCE LAYER
# -------------------------------------------------------------------


def run_inference_tier(
    active_model: str,
    metrics: SafetyMetricsPayload,
) -> InferenceResult:
    """
    Execute bounded local inference using validated relational metrics.
    """
    raw_age = metrics["average_age_years"]

    # Explicitly check for numeric assignment to isolate fallback strings
    average_age = f"{raw_age:.1f}" if isinstance(raw_age, (int, float)) else "N/A"

    prompt = CLINICAL_REASONING_PROMPT.format(
        drug=metrics["drug"],
        reaction=metrics["reaction"],
        total_cases=metrics["total_cases"],
        severe_cases=metrics["severe_cases"],
        average_age=average_age,
    )

    try:
        response = ollama.chat( # type: ignore
            model=active_model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        output_text = response["message"]["content"]
        reasoning_trace, clinical_narrative = extract_reasoning_trace(output_text)

        return InferenceResult(
            reasoning_trace=reasoning_trace,
            clinical_narrative=clinical_narrative,
        )

    except ollama.ResponseError as err:
        raise InferenceEngineError(f"Ollama model execution error: {err}") from err
    except ConnectionError as err:
        raise InferenceEngineError(f"Local inference connection failed: {err}") from err
    except TimeoutError as err:
        raise InferenceEngineError(f"Inference execution exceeded timeout threshold: {err}") from err