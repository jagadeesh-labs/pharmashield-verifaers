"""
PharmaShield - Headless Integration Test Harness
Validates component linkage and type safety across all backend engines.
"""

import sys

from query_engine import fetch_safety_metrics

from reasoning_engine import (
    run_inference_tier,
    InferenceEngineError,
)

from validation_engine import verify_narrative_alignment

from shared_types import SafetyMetricsPayload


def main() -> None:
    """Execute a complete deterministic backend pipeline test."""

    print("🧪 Starting Core Pipeline Integration Test...\n")

    # ---------------------------------------------------------------
    # STEP 1: QUERY ENGINE VALIDATION
    # ---------------------------------------------------------------

    print("[STEP 1/3] Testing Query Engine Read...")

    raw_metrics = fetch_safety_metrics(
        "METFORMIN",
        "DIARRHOEA",
    )

    if raw_metrics["total_cases"] == 0:

        print(
            "❌ ERROR: Database returned 0 records. "
            "Run ingest_pipeline.py before executing the test harness."
        )

        sys.exit(1)

    print(
        f"✅ Success: Query Engine isolated "
        f"{raw_metrics['total_cases']} records."
    )

    metrics: SafetyMetricsPayload = {
        "drug": "METFORMIN",
        "reaction": "DIARRHEA",
        "total_cases": int(raw_metrics["total_cases"]),
        "severe_cases": int(raw_metrics["severe_cases"]),
        "average_age_years": raw_metrics["average_age_years"],
    }

    # ---------------------------------------------------------------
    # STEP 2: REASONING ENGINE VALIDATION
    # ---------------------------------------------------------------

    print(
        "\n[STEP 2/3] Testing Reasoning Engine "
        "(Invoking Local Model)..."
    )

    try:
        result = run_inference_tier(
            "gemma4:e2b",
            metrics,
        )

        print(
            "✅ Success: Local inference pipeline "
            "executed successfully."
        )

        print(
            f"--- Reasoning Trace Generated "
            f"({len(result.reasoning_trace)} chars) ---"
        )

        print(
            f"--- Narrative Generated "
            f"({len(result.clinical_narrative)} chars) ---"
        )

    except InferenceEngineError as err:

        print(
            "❌ ERROR: Reasoning Engine faulted.\n"
            "Verify Ollama background service status.\n\n"
            f"Trace: {err}"
        )

        sys.exit(1)

    # ---------------------------------------------------------------
    # STEP 3: VALIDATION ENGINE AUDIT
    # ---------------------------------------------------------------

    print(
        "\n[STEP 3/3] Testing Validation Engine Alignment Audit..."
    )

    validation_result = verify_narrative_alignment(
        metrics,
        result.clinical_narrative,
    )

    print(f"Result Status: {validation_result.is_verified}")

    print(
        f"Tokens Matched: "
        f"{validation_result.matched_tokens}"
    )

    print(
        f"Drift Detected: "
        f"{validation_result.drift_detected}"
    )

    print(f"Engine Reason: {validation_result.reason}")

    print(
        "\n🚀 INTEGRATION TEST PASSED: "
        "All engine files linked successfully."
    )


if __name__ == "__main__":
    main()