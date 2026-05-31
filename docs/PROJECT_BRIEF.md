# PharmaShield VeriFAERS

> **A Trust-Bounded, Globally-Federated Pharmacovigilance Intelligence System**
>
> *Deterministic ML as the source of truth. The LLM as a bounded interpreter. Every number auditable, every alert explainable, every agent constrained.*

---

## Document Purpose

This is the **canonical vision and strategy artifact** for PharmaShield VeriFAERS. It is written as a high-signal, semantic-continuity document (not a chat transcript) so that any engineer — or any future AI session — can reconstruct the full intent, constraints, and rationale of the project at minimal cost.

Companion document: [`ARCHITECTURE.md`](./ARCHITECTURE.md) holds the technical system design.

| Field | Value |
|---|---|
| **Product name** | PharmaShield VeriFAERS |
| **Category** | Pharmacovigilance intelligence / AI systems engineering |
| **Status** | Design locked, pre-implementation |
| **Primary author goal** | A high-grade, production-shaped portfolio project to secure an AI Systems / MLOps / ML Engineering role |
| **Secondary goal** | Open research artifacts (dataset DOI, preprint, peer-reviewed software paper) |
| **Origin** | Conceived for the Kaggle Gemma hackathon; deliberately broadened into a full production-grade system |

---

## 1. Executive Summary

Post-market drug-safety surveillance is fragmented across national regulators that operate in isolation. When the *same* drug — frequently a generic manufactured in India and exported worldwide — produces a novel adverse-event cluster, the signal can take months to cross-reference between the US FDA, Europe's EMA, the UK's MHRA, and Asia's PMDA. That **latency gap is where preventable harm multiplies.**

PharmaShield attacks this with two principles working together:

1. **A federated truth layer.** Ingest adverse-event data from multiple regulators, normalize it toward the international ICH E2B(R3) standard, and enrich every record with **manufacturer-origin intelligence** — surfacing how Indian-manufactured generics behave across global markets (a lens nobody else publishes).

2. **Asymmetric trust.** Clinical signal detection is done by a **deterministic ML/statistics engine** (Track Alpha) that runs with *zero LLM dependency*. A large language model (Track Beta) is allowed only to *translate* those locked numeric results into readable narratives — and a deterministic **validation engine** intercepts any hallucinated digit before it reaches a human.

The result is an auditable system where **math creates the intelligence and the LLM merely explains it** — with full observability, bounded autonomous agents, and a cloud-first deployment designed to run from a constrained dual-core laptop.

---

## 2. The Problem Statement

### 2.1 The inception thesis (preserved)

> *"Modern post-market pharmaceutical safety surveillance operates across fragmented, siloed, and asynchronous national architectures. When a drug causes a novel adverse event cluster, regulatory bodies operate in geographic isolation, leading to latency gaps where preventable clinical harm multiplies globally before safety signals cross-reference."*

### 2.2 The three structural failures

| Failure | Description |
|---|---|
| **The Latency Trap** | FDA (FAERS), EMA (EudraVigilance), MHRA (Yellow Card), PMDA all collect safety data on identical chemical entities using isolated database substrates and localized schemas. |
| **The Correlation Delay** | A hazardous API (active pharmaceutical ingredient) batch flagged in one region can take months of administrative clearing before another region ingests, formats, and mathematically flags the same systemic risk. |
| **The Black-Box Trust Deficit** | Automated global tools are typically opaque, centralized cloud systems that sovereign health authorities hesitate to trust due to data-privacy law, hardware demands, and the lack of granular mathematical explanation behind alerts. |

### 2.3 The reframing — India as the pharmacy of the world

India supplies a very large share of the world's generic medicines; a substantial fraction of US and EU generic supply originates from Indian manufacturers. Yet adverse-event signals are scattered across regulators and **rarely keyed back to manufacturer origin.** PharmaShield's unique angle:

> **Look at global adverse-event data through a manufacturer-origin lens — making the safety footprint of Indian-exported generics visible across jurisdictions for the first time.**

---

## 3. Vision & Mission

- **Vision:** A world where a safety signal detected by *any* regulator is mathematically cross-referenced against *all* others within hours, not months — with every alert explainable and every manufacturer accountable.
- **Mission (MVP-scoped):** Build a trustworthy, federated, explainable pharmacovigilance intelligence system that demonstrates this vision end-to-end on a curated, India-export-focused dataset — and is honest about what is live vs. roadmap.

---

## 4. The Core Technical Thesis — Asymmetric Trust

This is the intellectual heart of the project and its strongest differentiator.

```
Layer 1  SQL aggregations          ── 100% deterministic   (truth)
Layer 2  Classical statistics      ── PRR/ROR/BCPNN/EBGM    (truth)
Layer 3  Classical ML              ── XGBoost / LightGBM    (reproducible)
Layer 4  Deep learning             ── PyTorch MLP / Prophet (reproducible)
Layer 5  Explainability            ── SHAP feature footprint(deterministic)
─────────────────────────────────────────────────────────────────────────
Layer 6  LLM (Gemma)               ── interprets ONLY       (bounded, stochastic)
Layer 7  Validation engine         ── set-math drift intercept (deterministic)
```

**The LLM never originates a fact.** It receives a locked array of numbers + SHAP vectors and produces a narrative. If the narrative introduces an unverified digit or drops a core statistic, the validation engine catches the discrepancy via token/number intersection and overrides the output.

> Design law: **"Math creates intelligence; engineering sustains intelligence; the LLM only narrates it."**

Track Alpha (deterministic) and Track Beta (generative) are **physically isolated** — you can unplug the LLM entirely and the system still detects, scores, forecasts, and *explains* every signal. That property is the project's credibility anchor.

---

## 5. Business Outcomes & Stakeholder Value

This is **decision-support tooling**, not a diagnostic or a regulator replacement. Framed that way, the value chain is concrete.

| Stakeholder | Pain today | What PharmaShield delivers | Outcome |
|---|---|---|---|
| **Indian pharma exporters** (Sun, Cipla, Dr. Reddy's, Lupin, Aurobindo, Zydus, Torrent, Glenmark, Alkem, Mankind…) | A regulatory import alert / warning letter can freeze exports and crater market cap | Early, explainable warning of AE-signal divergence in export markets *before* a regulator flags it | Avoidance of a single import alert can save very large sums; faster corrective action |
| **Pharmacovigilance teams / CROs** | Manual signal triage is slow and analyst-expensive | Automated disproportionality + ML ranking + SHAP explanation + draft narrative | Reduced triage time; audit-ready output |
| **Importing regulators** (FDA / EMA / MHRA) | Latency between national databases; imported-generic blind spots | Manufacturer-origin cross-jurisdictional signal view | Shorter signal-detection latency on imported drugs |
| **Health systems / formularies** | Risk-adjusted prescribing is guesswork | Transparent, math-grounded risk scores | Better-informed decisions |
| **Researchers / journalists** | No open, manufacturer-keyed AE dataset | Open dataset + reproducible methods | New investigative + academic capability |

**Market context (directional, public-literature figures — verify before citing in a paper):**
- India pharmaceutical exports ≈ **USD 27–28 billion/year**.
- Global pharmacovigilance market ≈ **USD 7–8 billion**, growing at double-digit CAGR.
- Adverse drug reactions are a **leading contributor to hospital admissions** in multiple published studies.

**Business one-liner:** *A single prevented import alert, or one earlier safety signal, pays for the entire system many times over.*

---

## 6. The Moat — Why This Stands in the Top <1%

Most portfolio projects are tutorials in a private repo. The rare ones share six traits; PharmaShield is engineered for all six:

| Signal | This project |
|---|---|
| Real, messy, domain data | ✅ Multi-regulator adverse-event data |
| A genuinely novel **method** | ✅ Asymmetric trust pipeline (ML+SHAP truth → bounded LLM → set-math intercept) |
| Reproducible (anyone can rerun) | ✅ Open dataset + versioned models + pinned seeds |
| Deployed & live | ✅ HF Space + Supabase + live dashboards |
| External validation (DOI / preprint / peer review) | ✅ Zenodo + arXiv/medRxiv + JOSS track |
| Honest about limitations | ✅ Staged data tiers, calibrated metrics, explicit disclaimers |

**The defensible novelty is two-fold:**
1. **Asymmetric trust as a hallucination-interception method** for regulated-domain narrative generation (LLM-safety × pharmacovigilance — timely and under-explored).
2. **Manufacturer-origin cross-jurisdictional signal mapping** (the India-export lens) as an open, reproducible dataset + method.

Everything else (gradient boosting, disproportionality stats) is **table stakes that prove domain fluency** — not the moat.

---

## 7. Career Positioning

The uploaded discussions clarified the target: this is an **AI Systems Engineering / MLOps / Agentic Workflow Engineering** showcase, not a notebook-analytics piece. The headline competencies it demonstrates:

- **Systems-centric thinking** — data movement first, intelligence second.
- **Production engineering** — Postgres, FastAPI, Docker, CI/CD, cloud deployment.
- **MLOps maturity** — model cards, benchmark suites, drift monitoring, reproducibility.
- **Bounded agentic systems** — event-driven, constrained, observable autonomy.
- **Observability discipline** — non-negotiable monitoring layer.
- **Explainable, governed AI** — SHAP-grounded, human-in-the-loop, honest scope.

> Positioning line: *"I build reliable autonomous AI systems for regulated domains — not just models."*

---

## 8. Research & Credibility Track

The publication angle does not change the build; it **raises the rigor bar** (pinned seeds, versioned data, model cards, benchmark suite, tests + docs from line one). Recommended ladder, fastest first:

| Tier | Venue | Artifact | Realism for this build |
|---|---|---|---|
| 1 | **Zenodo** + HF dataset/model cards | Citable dataset + models (DOI) | Hours |
| 2 | **arXiv / medRxiv** | Method preprint (timestamped, citable) | Days–weeks |
| 3 | **JOSS** / SoftwareX | Peer-reviewed software paper | Weeks (needs tests/docs) |
| 4 | ML4Health / Trustworthy-ML / GenAI-safety **workshops** | The trust-pipeline method | Weeks |
| 5 | PLOS ONE / JAMIA Open / Frontiers / Scientific Reports | Full validated study | Months |

**Recommended target:** Tiers **1 + 2 + 3** — a DOI'd dataset, a public preprint, and a peer-reviewed JOSS paper. That trio is achievable off this build and is what very few candidates can show.

**Observability feeds the paper:** validation pass-rate and drift-interception rate over time become the empirical results table — telemetry, not assertion.

---

## 9. Scope — What We Build vs. What We Don't (Honest Tiers)

Honest scope *increases* credibility. Over-claiming live integrations a reviewer knows are closed will destroy it.

### Data sources

| Tier | Sources | Status |
|---|---|---|
| **Tier 1 — Live, real integration** | openFDA (US), Health Canada Vigilance, TGA DAEN (Australia) | ✅ Built — three heterogeneous schemas prove the federated ETL |
| **Tier 2 — Adapter scaffolded + sample/aggregate data** | EMA EudraVigilance, MHRA Yellow Card | 🟡 Functional adapters, limited public data |
| **Tier 3 — Documented roadmap** | PMDA (Japan), WHO VigiBase | 🔴 Interfaces stubbed; no open access |

### Explicitly **not** in the MVP (documented as roadmap)
- Full MedDRA licensed harmonization (MVP uses normalized string mapping toward E2B(R3) core fields).
- Real-time streaming (MVP = scheduled batch).
- Multi-tenant productionization beyond demo roles.
- PySpark distributed ETL (Pandas is correct at curated scale; PySpark is the scaling path).
- Quantum / federated-comms / frontier-math themes from the discussion files — out of scope by design (honoring *"execution > technology collection"*).

### The clinical-use disclaimer (must ship in writing)
PharmaShield is a **signal-support tool**. It does **not** make clinical or regulatory decisions, is **not** diagnostic, and is **not** validated for clinical deployment without further study. Naming this boundary is both ethically correct and a credibility signal.

---

## 10. Honest Metric Commitments

Receipts beat claims. Every model ships a reproducible benchmark + model card. If a target proves infeasible after the Day-1 data audit, it is reported *before* training, not after.

| Module | Metric | Committed | Stretch | Notes |
|---|---|---|---|---|
| Severity regressor (XGBoost) | R² | **≥ 0.85** | 0.90 | Self-reported severity is inherently noisy |
| AE-volume forecast (Prophet) | R² | **≥ 0.90** | 0.95 | Time series is structurally favorable |
| Manufacturer risk score | R² | **≥ 0.90** | 0.95 | Composite engineered target |
| Safety-signal classifier (LightGBM) | AUC-ROC | **≥ 0.90** | 0.94 | R² does **not** apply to classification |
| Drug-drug-interaction MLP (PyTorch) | AUC-PR | **≥ 0.75** | 0.85 | Sparse signal; framed as research module |
| SHAP explainability | Alert coverage | **100%** | — | Every alert carries a feature footprint |
| LLM narrative validation | Pass rate | **≥ 95%** | 99% | The trust contract, measured live |

> **R² > 0.90 is honest only where it is structurally achievable** (forecasting, composite risk). For classification and anomaly tasks, AUC / AUC-PR / precision@K are the correct metrics. Reporting the right metric per task *is* the senior signal.

---

## 11. Engineering Philosophy (Distilled From the Discussion Files)

These principles govern every decision and are treated as non-negotiable.

1. **Data movement first, intelligence second.** The ML model is one layer in a larger ecosystem of pipelines, databases, and orchestration.
2. **Constraint-first engineering.** Toyota-style efficiency-per-resource; intelligence-per-watt over brute force. Constraints (dual-core laptop) force superior architectural discipline.
   - *Frontier vs sustainable AI:* frontier LLM labs are Formula-1 laboratories — they prove what's possible, but civilization runs on efficient, accessible systems. **Peak capability ≠ sustainable operational capability.** PharmaShield optimizes for *useful intelligence per unit of resource*, using hierarchical routing (small models do the bulk, large models reason selectively, frontier is human-invoked only).
   - *Hybrid intelligence ecosystem:* the future is layered (ML + DL + SLMs + selective LLM + retrieval + validators + human supervision), not a single omniscient model. LLMs are the orchestration/explanation layer; ML/DL are the core prediction engines.
3. **Laptop = cockpit, cloud = execution.** Local machine orchestrates and codes; cloud does heavy inference, training, embeddings, and storage.
4. **Bounded autonomy.** *"Think longer, act less, verify everything."* Agents: analyze → constrain → prepare → execute → validate, with a **1–3 iteration hard cap** and safe escalation. No recursive loops, no stochastic fix-spraying.
5. **Few specialized agents, not swarms.** 4–6 focused agents maximum; event-driven, idle-by-default. *Agent-count inflation reflects architectural weakness.*
6. **Token & context economics.** Semantic compression over transcript replay; retrieve minimal relevant context; sparse computation; adaptive inference (small models route, large models reason).
7. **Observability is non-negotiable.** Designed in from line one, never bolted on. Grafana OSS-first; Grafana Cloud optional.
8. **Honesty as strategy.** Calibrated metrics, staged scope, explicit limitations, human-in-the-loop governance.
9. **Execution > technology collection.** Resist tool sprawl; one tool, one job.

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **FAERS** | FDA Adverse Event Reporting System (US post-market safety data). |
| **openFDA** | FDA's public REST API exposing FAERS and related datasets. |
| **EudraVigilance** | EMA's European adverse-event reporting system. |
| **Yellow Card** | UK MHRA's adverse-event reporting scheme. |
| **PMDA** | Japan's Pharmaceuticals and Medical Devices Agency. |
| **VigiBase** | WHO global ADR database (Uppsala Monitoring Centre). |
| **ICH E2B(R3)** | International standard for electronic transmission of individual case safety reports. |
| **MedDRA** | Medical Dictionary for Regulatory Activities — standardized adverse-event terminology. |
| **PRR** | Proportional Reporting Ratio — disproportionality signal metric. |
| **ROR** | Reporting Odds Ratio — disproportionality signal metric. |
| **BCPNN** | Bayesian Confidence Propagation Neural Network — WHO/UMC signal metric. |
| **EBGM / MGPS** | Empirical Bayes Geometric Mean — FDA-style disproportionality metric. |
| **SHAP** | SHapley Additive exPlanations — local feature-attribution explainability. |
| **API (pharma)** | Active Pharmaceutical Ingredient. |
| **Track Alpha** | Deterministic ML/statistics engine (zero LLM dependency). |
| **Track Beta** | Isolated generative LLM layer (interpretation only). |
| **Asymmetric trust** | Architecture where deterministic layers are authoritative and the LLM is bounded and audited. |

---

## 13. Roadmap (Phased)

| Phase | Focus | Key deliverables |
|---|---|---|
| **P0 — Foundation** | Data + DB | Supabase schema (RLS, pgvector, audit chain); Tier-1 federated ETL; curated India-export dataset |
| **P1 — Intelligence** | Track Alpha | PRR/ROR/BCPNN/EBGM; XGBoost severity; LightGBM signal; Prophet forecast; SHAP; trained on Kaggle/Colab |
| **P2 — Trust** | Track Beta + validation | Gemma narrative (bounded), set-math validation engine, audit log, trust verdicts |
| **P3 — Interface** | Frontend + API | FastAPI; React/Lovable OpenAlex-style UI; India Dashboard; trust-verdict cards |
| **P4 — Observability + Agents** | Reliability | Grafana dashboards/alerts; 6 bounded agents; CI/CD; GitHub Projects Kanban |
| **P5 — Credibility** | Research | Zenodo DOI; arXiv/medRxiv preprint; JOSS submission |
| **R — Roadmap** | Scale | EMA/MHRA/PMDA/VigiBase; MedDRA; PySpark; streaming; multi-tenant; post-quantum-safe audit chain |

---

*End of project brief. See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the technical system design.*
