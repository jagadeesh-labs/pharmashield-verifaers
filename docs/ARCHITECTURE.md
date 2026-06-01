# PharmaShield VeriFAERS — Architecture

> Technical reference. Companion to [`PROJECT_BRIEF.md`](./PROJECT_BRIEF.md). The deterministic layers are authoritative; the language model is bounded and audited.

## Design principles

1. **Data first.** The ingestion and storage layer is hardened before any model.
2. **Asymmetric trust.** Statistics and ML decide the facts; the LLM only phrases them; a deterministic check rejects drift.
3. **Cloud-offloaded compute.** Training and inference run on managed or free cloud tiers; the local machine only orchestrates.
4. **Pluggable, no lock-in.** Database, LLM backend, and monitoring target are swappable by configuration.
5. **Smallest sufficient component.** Use the simplest model, the fewest services, and no runtime agents until a concrete need is proven.

## System overview

```text
[ Ingestion ]  openFDA · Health Canada · TGA  →  normalize  →  enrich
       │
       ▼
[ Data layer ]  PostgreSQL (Supabase) — relational truth + materialized statistics
       │
       ├───────────►  [ Deterministic intelligence ]
       │               disproportionality (PRR/ROR/BCPNN/EBGM) + ML (severity, signal, forecast)
       │                      │   computed values = source of truth
       │                      ▼
       │               [ Bounded LLM ]  phrases the computed values only
       │                      │
       │                      ▼
       │               [ Validation ]  numeric-faithfulness check → pass / flag / withhold
       ▼
[ Interface ]  FastAPI + React            [ Observability ]  OpenTelemetry → Grafana
```

## Data layer

- **Target:** PostgreSQL via Supabase (managed auth, row-level security, encryption at rest). **Current prototype:** SQLite.
- Access goes through a repository abstraction, so the backend is swappable (Supabase → self-hosted Postgres → SQLite) without touching business logic.
- Core tables: `adverse_events` (append-only fact), dimension tables (`drugs`, `manufacturers`, `reactions`, `regulators`), and a materialized `signal_statistics` table refreshed after ingest.
- Integrity: foreign keys and check constraints enforced; writes are idempotent (upsert on `(regulator, source_id)`); each row carries a source hash for provenance.

### Schema (core)

```sql
-- Dimensions
regulators(id, code, name, country, source_type, last_synced_at)
drugs(id, generic_name, atc_code, is_generic)
manufacturers(id, name, country)
reactions(id, meddra_pt, soc)

-- Fact (append-only)
adverse_events(
  id, regulator_id, source_id, drug_id, manufacturer_id, reaction_id,
  severity, age, sex, country_reported, received_date,
  source_payload_hash, ingested_at,
  UNIQUE (regulator_id, source_id)          -- idempotent upsert key
)

-- Materialized analytics (refreshed after each ingest)
signal_statistics(
  drug_id, reaction_id, regulator_id,
  n_cases, prr, ror, bcpnn_ic, ebgm, computed_at
)

-- Append-only audit of every generated summary
validation_verdicts(
  id, ts, query_hash, inputs_json,
  model, summary, status, drift_json
)
```

## Ingestion

- One adapter per source behind a single contract: `fetch → normalize → upsert`.
- **Live:** openFDA. **Additional (proof of multi-source normalization):** Health Canada, TGA. **Interface-only (restricted public access):** EMA, MHRA, PMDA, WHO VigiBase.
- Normalization maps each source toward the ICH E2B(R3) core fields; full licensed MedDRA is out of initial scope (field mapping is used instead).
- Workers are stateless and idempotent (delta by last-sync timestamp); safe to re-run.
- Pandas at the curated data scale; distributed ETL (PySpark) is a scaling concern, not an initial one.

## Deterministic intelligence

- **Disproportionality:** PRR, ROR, BCPNN, EBGM — computed directly, with confidence intervals.
- **Models (supporting):** severity regression and signal classification (gradient-boosted trees), and volume forecasting. Trained offline on Kaggle/Colab; artifacts are versioned and loaded for inference.
- **Explainability:** feature attributions (SHAP) accompany model outputs.
- All outputs are numeric and reproducible (pinned seeds, versioned data). These computed values are the only source of truth downstream.

## Bounded generation

- The LLM (Gemma, via Hugging Face Inference or Google AI Studio) receives the computed values inside a fixed, structured prompt and returns a structured summary.
- It is prohibited from external ungrounded knowledge and from emitting any figure not supplied to it.
- Backends are config-selected; a local runtime (Ollama) is the offline fallback. Use the smallest model that meets quality; escalate only when needed.

## Validation — the core

- A deterministic auditor extracts every number and key claim from the summary and intersects it with the computed values.
- Rounding tolerance is explicit; omissions and fabrications are tracked separately.
- On mismatch, the output is withheld or corrected and the event is logged. Each verdict and its inputs are recorded for audit.
- This layer is also packaged as the project's contribution: a reproducible numeric-faithfulness benchmark with baselines (LLM-as-judge, NLI, lexical).

## API and interface

- **Frontend:** React + Tailwind (target); the current prototype uses Streamlit.
- **API:** FastAPI.

```text
GET  /drugs?q=&country=         list / search drugs
GET  /drugs/{id}                drug detail + signal statistics
GET  /manufacturers/{id}        portfolio + adverse-event profile
GET  /reactions/{id}            reaction detail
GET  /signals?drug=&reaction=   disproportionality statistics
POST /reasoning                 run the trust pipeline (below)
GET  /health   /metrics         liveness + Prometheus scrape
```

`POST /reasoning` response shape:

```json
{
  "statistics": { "n_cases": 0, "prr": 0.0, "ror": 0.0, "ci": [0.0, 0.0] },
  "summary":    "model-generated narrative, phrasing only the values above",
  "verdict":    { "status": "pass | flagged | withheld", "drift": [] },
  "audit_id":   "uuid"
}
```

## Data flow (end to end)

```text
1. Ingest       fetch → normalize (E2B R3) → upsert           (idempotent)
2. Post-ingest  refresh signal_statistics
3. Request      POST /reasoning(drug, reaction)
4. Compute      statistics from the database                  (authoritative)
5. Phrase       bounded LLM turns the values into a summary
6. Validate     intersect summary numbers vs statistics  →  pass / flag / withhold
7. Persist      verdict + inputs (append-only audit)
8. Respond      { statistics, summary, verdict, audit_id }
```

Telemetry is emitted at each step.

## Observability (from the start, not bolted on)

- **Stack:** OpenTelemetry metrics, logs, and traces → Grafana (OSS-first; managed Grafana optional).
- **Metrics:** request rate / error rate / latency (p50, p95, p99); ingestion success and records per run; **data-freshness lag per source**; model inference latency; **validation pass rate** and **drift-interception rate**.
- **Alerts:** validation pass-rate drop; data-freshness breach; error-rate or latency SLO breach.
- One curated dashboard covers all of the above.

## Compute and deployment

- **Train** on Kaggle/Colab (free tiers); **serve** lightweight inference from pre-trained, versioned artifacts.
- **Database** on Supabase; **LLM** via hosted inference. The local machine orchestrates only.
- **Package** the backend as a Docker image and deploy to a container host (e.g., a Hugging Face Space). CI via GitHub Actions: test → lint → build → deploy.

## Repository layout (target)

```text
ingest/         source adapters + normalizer
core/           shared types · db repository · config
intelligence/   statistics · models · explainability
trust/          reasoning (bounded LLM) · validation engine
api/            FastAPI app
evals/          faithfulness benchmark + tests
benchmarks/     reproducible metric scripts
docs/           project brief + this document
```

The current flat prototype (`app.py`, `ingest_pipeline.py`, `query_engine.py`, `reasoning_engine.py`, `validation_engine.py`) migrates into the structure above.

## Security and governance

- Authentication and row-level access via Supabase; secrets live in environment variables and are never committed.
- Append-only audit of validation verdicts, with per-row source hashing for provenance.
- Human-in-the-loop for all clinical or regulatory interpretation; the system is decision-support only.

## Scaling (later, not now)

Additional regulators, licensed MedDRA harmonization, distributed ETL, read replicas, and multi-tenancy are deferred until the single-source slice is built, deployed, and validated.
