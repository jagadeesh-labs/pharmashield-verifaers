# PharmaShield VeriFAERS — System Architecture

> Technical system design. Companion to [`PROJECT_BRIEF.md`](./PROJECT_BRIEF.md) (vision, business, research, scope).
>
> This document is written as a dense, retrieval-friendly architecture-state artifact: high signal, layer-clustered, low fluff.

---

## 0. Design Principles (Binding Constraints)

Every decision below is justified against these. If a choice violates one, it is wrong.

| # | Principle | Architectural consequence |
|---|---|---|
| P1 | **Data movement first, intelligence second** | The ETL + DB backbone is built and hardened before any model. |
| P2 | **Asymmetric trust** | Deterministic layers are authoritative; the LLM is bounded and audited. |
| P3 | **Laptop = cockpit, cloud = execution** | Nothing heavy runs locally; train on Kaggle/Colab, serve on HF Spaces, DB on Supabase. |
| P4 | **Constraint-first / intelligence-per-watt** | Sparse computation, adaptive model routing, no always-on inference. |
| P5 | **Bounded autonomy** | Agents: analyze→constrain→prepare→execute→validate, 1–3 iteration cap, escalate. |
| P6 | **Observability is non-negotiable** | Every service is instrumented from line one (OpenTelemetry → Grafana). |
| P7 | **Pluggable, no lock-in** | DB, LLM backend, and monitoring target are swappable via config. |
| P8 | **Honest scope** | Tiered data sources; calibrated metrics; explicit disclaimers. |
| P9 | **Execution > technology collection** | One tool, one job; resist sprawl. |

**Target environment (the constraint we design around):** HP Pavilion 15-au627tx — dual-core i7-7500U, 16 GB RAM, NVIDIA 940MX 4 GB, SATA SSD. Too weak for DL training or local LLM serving → all heavy compute is offloaded to free cloud tiers.

---

## 1. System Overview

```
 TRAIN (Kaggle / Colab, free CPU/GPU)             ARTIFACTS (Hugging Face Hub)
   │ pull curated data from Supabase                 ▲ push .joblib / .pt + model cards
   └──────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  L1 DATA — Supabase (Postgres 15 + Auth + RLS + pgvector)                  │
│  Curated India-export AE dataset · materialized signal_ratios · audit chain │
└───────────────┬──────────────────────────────────────────┬────────────────┘
                │ (auto REST/GraphQL: read-heavy browse)     │ (ML + trust: FastAPI)
                ▼                                            ▼
   ┌──────────────────────┐          ┌───────────────────────────────────────┐
   │  L9 FRONTEND          │  JSON    │  L8 API — FastAPI (HF Docker Space)   │
   │  React + Tailwind     │◄────────►│                                       │
   │  (Lovable, OpenAlex   │          │  L3 TRACK ALPHA (deterministic)       │
   │   design language)    │          │   PRR/ROR/BCPNN/EBGM · XGBoost ·       │
   │  Supabase Auth login  │          │   LightGBM · PyTorch MLP · Prophet ·   │
   └──────────────────────┘          │   SHAP   (models loaded from HF Hub)   │
                                      │            │                          │
                                      │            ▼ (locked numeric arrays)  │
                                      │  L4 TRACK BETA (generative, caged)    │
                                      │   Gemma via HF / Ollama Cloud / AIStudio│
                                      │            │                          │
                                      │            ▼                          │
                                      │  L5 VALIDATION — set-math intercept   │
                                      │            │                          │
                                      │            ▼                          │
                                      │   TRUST VERDICT (green/amber/red)     │
                                      └─────────────────┬─────────────────────┘
                                                        │ OTel metrics/logs/traces
                                                        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  L7 OBSERVABILITY (non-negotiable) — Grafana OSS primary / Cloud optional │
   │  Prometheus · Loki · Tempo · Grafana · dashboards · alerts                 │
   └────────────────────────────────────────────────────────────────────────┘

   L6 AGENTS (event-driven, idle-by-default): Orchestrator · Debug · Review ·
              Tracking · Deployment · Context/Retrieval   (1–3 iteration cap)
   L10 WORKFLOW/CI-CD: GitHub Projects (Kanban) · GitHub Actions · Docker
```

---

## 2. L1 — Data Layer (Supabase / Postgres)

### 2.1 Why Supabase
Postgres + built-in Auth + Row-Level Security + `pgvector` + auto-generated APIs, open-source and self-hostable (preserves the sovereignty story). Offloads DB compute from the laptop. Chosen over Neon because **built-in Auth + RLS directly satisfy the "safe authenticated database" requirement** without hand-rolling auth.

### 2.2 Performance & integrity
- Connection pooling via Supabase Supavisor / pgBouncer.
- **Covering indexes** for hot query paths; **partial indexes** for the `is_indian_export` lens; expression indexes for normalized name lookups.
- **Materialized views** for precomputed disproportionality (`signal_ratios`), refreshed post-ingest.
- All writes in explicit transactions; **idempotent UPSERT** keyed on `(regulator, source_id)`.
- Foreign keys + CHECK constraints enforced.
- Encryption at rest + TLS in transit (platform-managed).
- Data-access behind a **repository abstraction** → swappable to Neon / self-hosted Postgres / local Docker / SQLite-offline without touching business logic.

### 2.3 Schema (Postgres dialect, E2B(R3)-aligned)

```sql
-- Dimensions
regulators        (id, code, name, country, source_type, last_synced_at)
manufacturers     (id, canonical_name, country, india_parent_company,
                   cdsco_license, ndc_labeler_codes JSONB, atc_classes JSONB)
drugs             (id, generic_name, brand_names JSONB, atc_code,
                   therapeutic_class, is_generic, primary_manufacturer_id)
reactions_meddra  (id, preferred_term, soc, severity_default)
countries         (iso_code, name, region)

-- Fact (append-only truth layer)
adverse_events    (id, regulator_id, source_id, drug_id, manufacturer_id,
                   reaction_meddra_id, severity, age, gender, country_reported,
                   received_date,
                   is_indian_export BOOLEAN GENERATED ALWAYS AS (...) STORED,
                   source_payload_hash, ingested_at)

-- Materialized analytics (refreshed post-ingest)
signal_ratios     (drug_id, reaction_meddra_id, regulator_id,
                   prr, ror, bcpnn_ic, ebgm, chi_square, n_cases, computed_at)

-- Vector store (pgvector) for similarity + agent retrieval (NOT clinical grounding)
drug_embeddings   (drug_id, embedding VECTOR(128))

-- Auth handled by Supabase Auth; app roles + scoping:
profiles          (id→auth.users, role, org, manufacturer_id NULLABLE)
-- roles: admin | analyst | viewer | regulator | manufacturer
-- RLS: a 'manufacturer' profile sees only its own manufacturer_id rows.

-- Audit (append-only, hash-chained; UPDATE/DELETE blocked by trigger)
audit_log         (id, ts, actor_id, action, entity_type, entity_id,
                   payload_hash, previous_hash)
llm_verdicts      (id, ts, query_hash, input_metrics JSONB, model,
                   narrative, validation_status, drift_details JSONB)
```

- `is_indian_export` is a **generated column** — it cannot drift from the manufacturer's country.
- `source_payload_hash` proves per-row provenance; `audit_log` is **hash-chained** (each row carries the prior row's hash) so tampering is detectable.

---

## 3. L2 — Federated ETL

### 3.1 Adapter pattern
```
ingest/
├── base_adapter.py        # contract: fetch() → normalize() → upsert()
├── fda_adapter.py         # ✅ openFDA JSON              (Tier 1, live)
├── health_canada_adapter.py # ✅ Vigilance CSV           (Tier 1, live)
├── tga_adapter.py         # ✅ DAEN CSV                  (Tier 1, live)
├── ema_adapter.py         # 🟡 EudraVigilance aggregate  (Tier 2, sample)
├── mhra_adapter.py        # 🟡 Yellow Card iDAP          (Tier 2, sample)
├── pmda_adapter.py        # 🔴 stub interface            (Tier 3, roadmap)
├── who_vigibase_adapter.py# 🔴 stub interface            (Tier 3, roadmap)
├── normalizer.py          # → ICH E2B(R3) core fields
└── india_registry.py      # top ~30 Indian exporters ↔ NDC labeler codes
```

### 3.2 Properties
- **Idempotent, stateless workers** — delta updates via last-sync timestamp; safe re-runs (UPSERT).
- **Normalization** toward E2B(R3) core fields (demographics, reaction MedDRA PT, suspect/concomitant drugs, seriousness). MVP uses string normalization toward these fields; full licensed MedDRA is roadmap.
- **Enrichment** — every record tagged `manufacturer_country`, `is_indian_export`, `indian_manufacturer_canonical` via `india_registry`.
- **Pandas now, PySpark roadmap** — curated India-export volume fits Pandas + Supabase free tier; PySpark is the documented scaling path for full-FAERS volumes.
- Curation strategy: ingest AEs for drugs made by the top ~30 Indian exporters → fits free-tier storage *and* sharpens the unique angle.

---

## 4. L3 — Track Alpha (Deterministic Intelligence, Zero LLM Dependency)

Runs standalone. The system detects, scores, forecasts, and *explains* every signal even with the LLM fully unplugged.

| Module | Task | Library | Metric → target |
|---|---|---|---|
| **Disproportionality** | PRR, ROR, BCPNN (WHO/UMC), EBGM (FDA-style), χ² | numpy / statsmodels | exactness (deterministic) |
| **Severity regressor** | Predict severity from {drug, reaction, age, gender, mfr country} | XGBoost | R² ≥ 0.85 |
| **Signal classifier** | Is a drug–AE pair a true safety signal? | LightGBM | AUC-ROC ≥ 0.90 |
| **DDI toxicity** | Multi-drug interaction risk (research module) | PyTorch MLP | AUC-PR ≥ 0.75 |
| **Forecaster** | AE-volume trend | Prophet | R² ≥ 0.90 |
| **Embeddings** | Drug similarity (→ pgvector) | TruncatedSVD | qualitative |
| **Explainability** | SHAP feature footprint for every alert | shap | 100% alert coverage |
| **Anomaly** | Cross-regulator divergence (same drug, different rates) | IsolationForest | precision@K |

- **Adaptive routing** (P4): cheap stats/classification run always; expensive DL runs only when triggered.
- **Training** on Kaggle/Colab; artifacts + **model cards** pushed to **HF Hub**; served lightweight via `joblib` / `torch.load`. Optional **MLflow** for metric/version history.
- **Reproducibility:** pinned seeds, versioned data snapshot, committed benchmark suite (`benchmarks/`).

---

## 5. L4 — Track Beta (Generative Layer, Caged)

- **Role:** translate locked numeric arrays + SHAP vectors → readable clinical narrative / regulatory-style summary. **Never originates facts.**
- **The cage:** Track Alpha computes first; results are locked inside an immutable, structured prompt wrapper demanding structured (JSON) output. The LLM is prohibited from external ungrounded clinical memory or speculation.
- **Backends (pluggable, config-selected):**
  - **Hugging Face Inference API** — default cloud (no local VRAM).
  - **Google AI Studio** — preferred when strict **structured/JSON/controlled output** is needed (best fit for the cage).
  - **Ollama Cloud** — managed Gemma (27B/31B) option.
  - **Ollama local** — documented offline/sovereign fallback.
### 5.1 Hierarchical Intelligence Routing (resource-aware)

*"Match intelligence level to task complexity — not every task deserves frontier cognition."* An estimated ~80% of operational tasks (formatting, classification, routing, retrieval filtering, metadata extraction) are bounded and repetitive → handled by small models; heavy reasoning escalates selectively.

```
Tier 1  Small local SLM (Gemma e2b)      → format, classify, route, filter   (~80% of calls)
Tier 2  Moderate SLM (Gemma e4b)         → standard clinical narrative
Tier 3  Large cloud (Gemma 27B/31B,      → complex multi-signal reasoning
        Ollama Cloud / HF / AI Studio)
Tier 4  Frontier escalation (human-       → rare, supervised edge cases
        invoked; not in the automated path)
```

Routing is explicit and logged (which tier served which request → Grafana). This is *selective escalation*, not always-on frontier inference — the core of the "intelligence-per-resource" principle (P4). Frontier-tier is **human-invoked only**; the automated trust pipeline never auto-escalates to ungoverned frontier models.

---

## 6. L5 — Trust & Validation

```
Track Alpha numbers + SHAP  ──►  Track Beta narrative  ──►  Validation engine  ──►  Verdict
                                                              │
                       set-math token/number intersection ────┘
```

- **Deterministic auditor:** extracts every number/claim from the narrative and intersects it with the authoritative Track-Alpha payload.
- **Drift handling:** if the narrative invents a digit, drops a core statistic, or misattributes a regulator → drift detected → output **overwritten/flagged**, event logged.
- **Tolerance rules:** explicit handling of rounding (e.g., "≈12" vs 12.4) vs. fabrication; omissions vs. hallucinations tracked separately.
- **Outputs:** immutable validation-status contract + **trust verdict** (green/amber/red) + full entry in `llm_verdicts` and the hash-chained `audit_log`.
- **`/evals/hallucination_tests/`** — golden cases that regression-test drift detection (also the paper's results table).

---

## 7. L6 — Constraint-Based Agent Layer

**Few specialized agents, not swarms.** Event-driven, idle-by-default (critical on the dual-core laptop). Governing law: *"Think longer, act less, verify everything."*

### 7.1 Agent lifecycle & contract
```
Event → activate → analyze → constrain → prepare → execute → validate → report → idle
                                          (≤ 1–3 iterations; else escalate to human)
```
Every agent: single responsibility · scoped permissions · tool-grounded (no claim without tool evidence) · structured output (finding / evidence / fix / verification / status) · self-monitored (attempts/escalations emitted to Grafana).

### 7.2 Roster (6, capped 4–6)

| Agent | One job | Bound to verifier |
|---|---|---|
| **Orchestrator** | Route events, manage constraints, hold state | — |
| **Debug** | Root-cause analysis, bounded repair (Observe→Localize→Reason→Validate→Fix→Verify→Escalate) | pytest / real traceback |
| **Review** | Code quality, lint, complexity/efficiency, security, model-card honesty, observability-lint | AST scan + EXPLAIN + coverage |
| **Tracking** | Sync GitHub Projects (Kanban), telemetry, stalled-workflow detection | GitHub API state |
| **Deployment** | Validate Docker/CI-CD, reproducibility, rollback (isolated from debug logic) | CI status / image build |
| **Context/Retrieval** | Docs + architectural memory (RAG via pgvector) | retrieved-evidence check |

> **RAG boundary:** retrieval augments *context* for agents and "similar drugs" — it is **never** the clinical grounding mechanism. The deterministic math layer remains the only source of truth. Retrieve minimal relevant context (avoid chunk inflation).

**No heavy frameworks** (LangGraph/AutoGen/CrewAI). Runtime agents = a ~explicit bounded controller in Python; dev-time agents = `.github/agents/*.agent.md` definitions. Agents do **engineering/ops only — never autonomous clinical/regulatory decisions** (human-in-the-loop).

---

## 8. L7 — Observability (Non-Negotiable)

**Instrument once (vendor-neutral), point anywhere.** OpenTelemetry (OTLP) + Prometheus metrics + structured logs → Grafana OSS (primary) *or* Grafana Cloud (optional, free tier / 14-day trial).

| Pillar | OSS tool | Captures |
|---|---|---|
| Metrics | Prometheus | RED (rate/errors/duration), model inference latency, drift scores |
| Logs | Loki | API / ETL / trust-pipeline structured logs |
| Traces | Tempo | ETL → ML → LLM → validation spans |
| Dashboards/Alerts | Grafana | visualization + alerting |

**What we monitor (domain-specific, the differentiator):**
- **RED** per endpoint; Supabase query latency / pool saturation; HF Inference latency & failures.
- **ML observability:** inference latency per model; prediction & feature drift (PSI / KS).
- **Trust pipeline (unique):** validation pass/fail rate · drift-interception rate · token-intersection score distribution · trust-verdict breakdown over time.
- **ETL health:** ingest success/failure per regulator · records/run · **data-freshness lag** per source.
- **Agent health:** attempts-per-task (should cluster at 1–2, never climb) · escalation rate.

**Alerts:** validation fail-rate spike · data-freshness breach · SLO (error/latency) breach · feature-drift threshold.

**3-day reality:** Phase-1 ships OTel + Prometheus metrics + one curated dashboard (RED + trust pipeline), pushed to Grafana Cloud free tier (zero local load); `docker-compose.observability.yml` committed so the full OSS LGTM stack *can* run locally. Loki/Tempo + Evidently drift service = Phase-2 roadmap.

---

## 9. L8 — API (FastAPI)

```
GET  /drugs?country=IN                 # India-manufactured drugs (faceted)
GET  /drugs/{id}                       # detail: AE profile + predictions + SHAP + forecast + similar
GET  /manufacturers/{id}               # portfolio + composite risk score + AE rates
GET  /reactions/{id}                   # affected drugs/manufacturers
GET  /regulators                       # data-source pages + freshness
GET  /signals/cross-regulator?drug=X   # cross-jurisdictional divergence flags
POST /reasoning                        # FULL trust pipeline → {metrics, shap, narrative, verdict, audit_id}
GET  /audit/{verdict_id}               # trace every narrative number to its source
GET  /metrics                          # Prometheus scrape
```
Auto-docs (OpenAPI). Read-heavy browse can also use Supabase's auto-API directly; FastAPI owns ML + trust + audit. Deployed as a **Docker Space** on HF.

---

## 10. L9 — Frontend (React / Lovable, OpenAlex Design Language)

- **Stack:** React + Vite + Tailwind (built via Lovable, native Supabase integration). React chosen over Vue for **hiring-market demand**; OpenAlex's *design language* (clean, data-dense, smooth, faceted) is reproduced — exact stack parity is not required.
- **Entity model (mirrors OpenAlex Paper→Author→Institution→Concept):**
  - **Drugs** (browse + detail) · **Manufacturers** (with country flag, portfolio, risk score) · **Reactions** · **Regulators** (data sources).
- **Hero page — the India Dashboard:** Indian manufacturers' global AE footprint at a glance.
- **Trust Verdict card** on every reasoning view (green/amber/red) + **Audit Trail viewer** tracing each number to its source.
- **Model Card pages** documenting each model's metrics, training data, and limitations.
- Charts via ECharts / Plotly.js; skeleton loaders; light/dark theme; Supabase Auth login.
- **Division of labor:** Kiro builds backend/ML/data/schema + API contract + design brief; Lovable builds the frontend against it.

---

## 11. L10 — Compute, Deployment & Workflow

### 11.1 Compute split (P3)
```
TRAIN: Kaggle / Colab (free CPU/GPU) → models + cards → HF Hub
SERVE: FastAPI loads pre-trained artifacts → cheap inference (laptop or HF Space)
DB:    Supabase (cloud)        LLM: HF Inference / AI Studio (cloud)
```
**Free-compute strategy (use deliberately, not impulsively):** Kaggle is treated as a *strategic experimental compute layer* (GPU experiments, embeddings, benchmarking, RAG tests), not just a dataset site. Additional free tiers held in reserve: Google Colab, AWS Free Tier, Oracle Cloud Free Tier. Local dev orchestration is intentionally light (VS Code + optional OpenCode/Ollama for SLMs); all heavy inference/training stays in the cloud.

### 11.2 Deployment & CI/CD
- **Docker** for the backend; **HF Docker Space** as the live host.
- **GitHub Actions:** test → lint → build image → deploy to HF Space.
- **GitHub Projects (Kanban):** Backlog → To Do → In Progress → Blocked → Done. GitHub-native (Issues/PRs/Actions) — chosen over Jira/Linear for solo + free-tier + old-hardware fit; makes execution discipline visible to recruiters.

### 11.3 Repository structure (target)
```
pharmashield-verifaers/
├── docs/            ARCHITECTURE.md · PROJECT_BRIEF.md · prompting_strategy.md · failure_patterns.md
├── ingest/          federated ETL adapters + normalizer + india_registry
├── core/            shared_types · db (repository abstraction) · config
├── intelligence/    stats · models (xgb/lgbm/mlp/prophet) · shap · routing
├── trust/           reasoning_engine (Track Beta) · validation_engine (L5)
├── agents/          orchestrator + 6 bounded agents (+ .github/agents/*.agent.md)
├── api/             FastAPI app + routers
├── prompts/         system/ · chains/ · templates/
├── evals/           hallucination_tests/ · formatting_tests/
├── benchmarks/      reproducible metric scripts
├── observability/   otel + docker-compose.observability.yml + dashboards/
├── models/          serialized artifacts (or HF Hub refs)
└── .github/         agents/ · workflows/ (CI-CD)
```
*(Migrates the current flat layout: `app.py`, `ingest_pipeline.py`, `query_engine.py`, `reasoning_engine.py`, `validation_engine.py`, `shared_types.py`, `test_stack.py` into the modular structure above.)*

---

## 12. End-to-End Data Flow (Trust Pipeline)

```
1. ETL adapters fetch → normalize (E2B R3) → enrich (India lens) → UPSERT Supabase
2. Post-ingest: refresh signal_ratios (PRR/ROR/BCPNN/EBGM) + drug_embeddings
3. Request → FastAPI /reasoning
4. Track Alpha: SQL aggregations + model predictions + SHAP  → locked numeric payload
5. Track Beta: caged Gemma turns payload → structured narrative
6. Validation: set-math intersection vs payload → drift? overwrite : pass
7. Persist llm_verdicts + hash-chained audit_log
8. Return {metrics, shap, narrative, verdict, audit_id}
9. Throughout: OTel metrics/logs/traces → Grafana; alerts on drift/staleness/SLO
```

---

## 13. Tech Stack Summary

| Layer | Choice | Rationale |
|---|---|---|
| Database | Supabase (Postgres + Auth + RLS + pgvector) | Auth+DB in one; cloud-offloaded; self-hostable |
| ETL | Python + Pandas (PySpark roadmap) | Right-sized for curated volume |
| Stats | numpy / statsmodels | PRR/ROR/BCPNN/EBGM |
| ML | XGBoost · LightGBM | Severity / signal |
| DL | PyTorch MLP · Prophet · TruncatedSVD | DDI · forecast · embeddings |
| XAI | SHAP | 100% alert explainability |
| LLM | Gemma via HF Inference / AI Studio / Ollama | Pluggable, cloud-first |
| Trust | Custom validation engine | Set-math drift intercept |
| Agents | Explicit bounded controller + `.agent.md` | No heavy frameworks |
| API | FastAPI | Async, auto-docs |
| Frontend | React + Tailwind (Lovable) | Hiring-market + OpenAlex design |
| Observability | OpenTelemetry → Grafana OSS / Cloud | Vendor-neutral, non-negotiable |
| Train | Kaggle / Colab | Free compute |
| Serve/Host | HF Spaces (Docker) | Free live demo |
| CI/CD | GitHub Actions + Projects (Kanban) | GitHub-native |
| Tracking | MLflow (optional) | Model/metric versioning |

---

## 14. Metric Scorecard (cross-ref `PROJECT_BRIEF.md` §10)

| Module | Metric | Committed | Stretch |
|---|---|---|---|
| Severity regressor (XGBoost) | R² | ≥ 0.85 | 0.90 |
| AE-volume forecast (Prophet) | R² | ≥ 0.90 | 0.95 |
| Manufacturer risk score | R² | ≥ 0.90 | 0.95 |
| Signal classifier (LightGBM) | AUC-ROC | ≥ 0.90 | 0.94 |
| DDI MLP (PyTorch) | AUC-PR | ≥ 0.75 | 0.85 |
| SHAP explainability | coverage | 100% | — |
| LLM narrative validation | pass rate | ≥ 95% | 99% |

---

## 15. Security & Governance

- **AuthN/Z:** Supabase Auth (JWT, OAuth, Argon2id-backed) + **RLS** for per-role/per-manufacturer data scoping.
- **Provenance:** `source_payload_hash` per row; **hash-chained `audit_log`** (append-only, UPDATE/DELETE blocked by trigger).
- **Secrets:** all keys (Supabase, HF token, AI Studio) in gitignored `.env` — never hardcoded.
- **In transit / at rest:** TLS + platform-managed encryption.
- **Governance:** human-in-the-loop for all clinical/regulatory interpretation; agents restricted to engineering/ops; explicit non-diagnostic disclaimer ships with the product.
- **Roadmap:** post-quantum-safe hash chain; full audit signing (Ed25519); SQLCipher for self-hosted offline mode.

---

## 16. Scaling Roadmap ("Scaling is harder than building")

| Dimension | MVP | Scale path |
|---|---|---|
| ETL | Pandas, batch | PySpark, distributed, streaming |
| Sources | FDA/Canada/TGA live | + EMA/MHRA/PMDA/VigiBase |
| Terminology | string-normalized E2B fields | licensed MedDRA + WHO-DD |
| DB | Supabase free tier | Postgres HA / read replicas / partitioning |
| LLM | HF Inference | dedicated HF Endpoints / self-host |
| Observability | metrics + 1 dashboard (Cloud) | full LGTM + Evidently drift service |
| Tenancy | single-user demo | multi-tenant + org isolation |
| Comms (team) | n/a | self-hosted Mattermost/Zulip/Matrix (sovereign) |

---

*End of architecture document. See [`PROJECT_BRIEF.md`](./PROJECT_BRIEF.md) for vision, business, and research strategy.*
