# PharmaShield VeriFAERS — Project Brief

> A trust-bounded pharmacovigilance system: deterministic statistics decide the facts, a language model only explains them, and a separate check rejects any explanation that drifts from the numbers.

## Problem

Post-market drug-safety data is fragmented across national regulators — the US (FAERS), the EU (EudraVigilance), the UK (Yellow Card), Japan (PMDA) and others — each with its own schema and release cadence. The same drug, often a generic exported worldwide, can show an emerging adverse-event signal in one jurisdiction months before the others cross-reference it. That latency is a real safety gap, and it matters disproportionately for widely exported generics.

A second, newer problem compounds it: teams increasingly use LLMs to summarize safety data, but LLMs are unreliable with numbers. In a regulated setting, a single fabricated or dropped statistic is unacceptable.

## Approach — bounded trust

PharmaShield separates two responsibilities that most AI tooling wrongly merges:

- **Deterministic layer (authoritative).** Counts, rates, and disproportionality statistics (PRR, ROR, BCPNN, EBGM) are computed directly from the data. These values are the single source of truth.
- **Generative layer (bounded).** A language model receives the computed numbers and writes a readable summary. It never originates a fact.
- **Validation layer (deterministic).** Every figure in the summary is checked against the computed values; any addition, omission, or mismatch is flagged and the output is withheld or corrected.

The result is auditable — each number in a narrative traces back to a specific computed value — and the generative layer is removable: the system detects, scores, and explains signals without it.

## Contribution

The intended contribution is deliberately narrow and measurable: **a lightweight, deterministic, reproducible method and benchmark for numeric faithfulness in LLM-generated pharmacovigilance narratives**, evaluated against existing faithfulness baselines (LLM-as-judge, NLI, lexical) on both interception quality and compute cost.

This is framed as applied work at the intersection of trustworthy ML and pharmacovigilance — not a new signal-detection method. Machine learning already outperforms classical disproportionality in the literature; that is treated as established baseline, not as novelty.


## Scope

**In scope (initial):**
- openFDA ingestion, with Health Canada and TGA as additional sources to prove multi-source normalization.
- Deterministic statistics, a numeric-faithfulness validation engine, and a bounded LLM summary.
- Honest evaluation against baselines, with reproducible benchmarks.

**Explicit non-goals (for now):**
- Live EMA / MHRA / PMDA / WHO VigiBase integration — interfaces only; public access is restricted.
- Licensed MedDRA harmonization — normalized field mapping is used instead.
- Any claim about manufacturer quality drawn from cross-jurisdictional differences — such differences are most likely reporting-behavior artifacts unless rigorously controlled.
- Real-time streaming, multi-tenancy, and distributed ETL — scaling concerns, not initial concerns.

## Evaluation

Metrics are matched to each task; no single headline number is claimed across all of them.

| Component | Metric | Target |
| --- | --- | --- |
| Severity regression | R² | ≥ 0.85 |
| Volume forecast | R² | ≥ 0.90 |
| Signal classification | AUC-ROC | ≥ 0.90 |
| Numeric-faithfulness check | interception rate + compute cost | reported vs. baselines |
| Narrative validation | pass rate | ≥ 0.95 |

Results are reported with confidence intervals and baselines, include negative results, and are reproducible (pinned seeds, versioned data). Domain credibility is established by recovering known, established drug–event associations before reporting anything new.

## Status & roadmap

Pre-MVP. The current code is an early prototype (SQLite / Streamlit / local Ollama); the target architecture (PostgreSQL via Supabase, FastAPI + React, hosted inference) is documented in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

1. Deploy a vertical slice: one drug, one metric, one bounded summary, one validation check.
2. Recover known signals to establish credibility.
3. Build the faithfulness benchmark, method, and baselines.
4. Add a cross-jurisdictional case study, with reporting-bias caveats stated.
5. Publish a reproducible release.

## Disclaimer

Decision-support tooling only. Not a diagnostic device, not a substitute for professional clinical or regulatory judgment, and not validated for clinical use.

## Key terms

**PRR / ROR / BCPNN / EBGM** — standard disproportionality measures for adverse-event signal detection. **MedDRA** — standardized adverse-event terminology. **openFDA** — public API exposing US FAERS data. **Faithfulness** — whether generated text accurately reflects its source numbers.
