"""
PharmaShield VeriFAERS - Main User Interface
Pure orchestration layer rendering the tiered trust pipeline framework.
"""

import streamlit as st

from shared_types import SafetyMetricsPayload

from query_engine import (
    fetch_safety_metrics,
    get_available_reactions,
)

from reasoning_engine import (
    run_inference_tier,
    InferenceEngineError,
)

from validation_engine import verify_narrative_alignment

# -------------------------------------------------------------------
# CONFIGURATION PROFILES
# -------------------------------------------------------------------

MODEL_PROFILES = {
    "Fast Interactive Audit (2B)": "gemma4:e2b",
    "Deep Validation Audit (4B)": "gemma4:e4b",
}

# -------------------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# -------------------------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="PharmaShield Console",
)

st.title("🛡️ PharmaShield VeriFAERS Console")

st.caption(
    "Tiered Local Clinical Reasoning Pipeline "
    "// Bounded Deterministic Trust Layer"
)

# -------------------------------------------------------------------
# UI LAYOUT
# -------------------------------------------------------------------

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🔍 Audit Configuration")

    target_drug = st.selectbox(
        "Target Monograph Key",
        ["METFORMIN"],
    )

    target_reaction = st.selectbox(
        "Target Adverse Event (MedDRA PT)",
        get_available_reactions(),
    )

    selected_profile = st.selectbox(
        "Reasoning Profile Tier",
        list(MODEL_PROFILES.keys()),
    )

    active_model = MODEL_PROFILES[selected_profile]

    run_audit = st.button(
        "Execute Safety Audit Pipeline",
        type="primary",
    )

# -------------------------------------------------------------------
# PIPELINE EXECUTION
# -------------------------------------------------------------------

if run_audit:

    # Stage 1: Deterministic relational metric extraction
    raw_metrics = fetch_safety_metrics(
        target_drug,
        target_reaction,
    )

    metrics: SafetyMetricsPayload = {
        "drug": target_drug,
        "reaction": target_reaction,
        "total_cases": int(raw_metrics["total_cases"]),
        "severe_cases": int(raw_metrics["severe_cases"]),
        "average_age_years": raw_metrics["average_age_years"],
    }

    with col2:

        # -----------------------------------------------------------
        # STAGE 1: RELATIONAL METRICS
        # -----------------------------------------------------------

        st.markdown("### 📊 Stage 1: Relational Metrics Output")

        m1, m2, m3 = st.columns(3)

        raw_age = metrics["average_age_years"]

        age_display = (
            f"{raw_age} yrs"
            if isinstance(raw_age, (int, float))
            else "N/A"
        )

        m1.metric(
            "Flagged Signals Count",
            metrics["total_cases"],
        )

        m2.metric(
            "Severe Records",
            metrics["severe_cases"],
        )

        m3.metric(
            "Cohort Mean Age",
            age_display,
        )

        st.markdown("---")

        # -----------------------------------------------------------
        # STAGE 2: BOUNDED REASONING
        # -----------------------------------------------------------

        st.markdown(
            f"### 🧠 Stage 2: Bounded Clinical Reasoning Layer ({active_model})"
        )

        with st.spinner("Running local inference..."):

            try:
                result = run_inference_tier(
                    active_model,
                    metrics,
                )

                with st.expander(
                    "👁️ View Internal Reasoning Rationale Log"
                ):
                    st.code(result.reasoning_trace)

                st.markdown(
                    "#### Clinical Interpretation Narrative"
                )

                st.info(result.clinical_narrative)

                st.markdown("---")

                # ---------------------------------------------------
                # STAGE 3: DETERMINISTIC VALIDATION
                # ---------------------------------------------------

                st.markdown(
                    "### 🛡️ Stage 3: Deterministic Validation Matrix"
                )

                validation_result = verify_narrative_alignment(
                    metrics,
                    result.clinical_narrative,
                )

                if validation_result.is_verified:

                    st.success(
                        "🟢 VERIFIED EVIDENCE — "
                        f"{validation_result.reason} "
                        f"({validation_result.matched_tokens} "
                        "tokens aligned)."
                    )

                else:

                    st.error(
                        "🔴 CORRECTED: "
                        "DETERMINISTIC VALIDATION OVERRIDE — "
                        f"{validation_result.reason} "
                        "Trust the relational metrics layer above."
                    )

            except InferenceEngineError as engine_err:

                st.error(
                    "Inference pipeline unavailable.\n\n"
                    "Verify Ollama background service status.\n\n"
                    f"{engine_err}"
                )