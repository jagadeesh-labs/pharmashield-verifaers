# PharmaShield VeriFAERS

PharmaShield VeriFAERS is a trust-oriented, local AI infrastructure stack designed for bounded clinical reasoning. The system ingests post-market adverse event data from the openFDA API, normalizes it into a highly optimized local SQLite database, and exposes an asymmetric multi-tier reasoning pipeline through a Streamlit dashboard.

Unlike traditional AI wrappers, this framework treats the large language model (LLM) strictly as an interpretation engine rather than a facts provider. The LLM is mathematically bounded by a deterministic relational truth layer and audited by an isolated verification matrix to catch and flag semantic drift instantly.

# Production Tracker
 Stage 1: Environment & Data Foundation
[x] 1.1 Base Environment: VS Code initialized, paths locked, requirements.txt locked.

[x] 1.2 The Local Brain: Ollama engine running, gemma4:e2b weights pulled successfully.

[x] 1.3 Data ETL Pipeline (ingest_pipeline.py): Script written to ping API, normalize age/gender, and write to SQLite without bloat.

[ ] 1.4 Pipeline Execution: Run python ingest_pipeline.py and verify pharma_shield.db is created.

Stage 2: The Deterministic Logic (Math & SQL)
[ ] 2.1 Query Engine (query_engine.py): Write the pure SQL module to extract total counts, severity sums, and mean ages for a specific drug/reaction pair.

[ ] 2.2 Query Testing: Verify the engine returns strict integer/float payloads, not raw text.

Stage 3: The AI & Trust Layer
[ ] 3.1 Reasoning Engine (reasoning_engine.py): Write the prompt boundary that sends the math to Gemma and retrieves the clinical summary.

[ ] 3.2 Verification Engine (verification_engine.py): Write the deterministic logic that checks if the numbers in Gemma's summary match the actual database numbers.

Stage 4: The Interface & Launch
[ ] 4.1 Streamlit Dashboard (app.py): Build the UI layout (dropdowns, metric cards, text boxes).

[ ] 4.2 Module Wiring: Import the three engines (Query, Reasoning, Verification) into the UI.

[ ] 4.3 Local Launch: Run streamlit run app.py.

[ ] 4.4 Final Audit: Push complete, working repository to GitHub.






# System Architecture

The codebase strictly adheres to modular separation of concerns. Every module owns a single, explicit responsibility to ensure maintainability, testing isolation, and type safety.

```text
├── database/
│   └── pharma_shield.db        # High-performance WAL relational truth layer
├── app.py                      # Pure presentation & pipeline routing layer
├── shared_types.py             # Global semantic type definitions
├── ingest_pipeline.py          # Deterministic openFDA ETL & DB bootstrap engine
├── query_engine.py             # Optimized read-only single-pass data extractor
├── reasoning_engine.py         # Bounded local inference orchestrator (e2b / e4b)
└── validation_engine.py        # Set-mathematics validation & drift interception engine


# System Architecture

shared_types.py: Houses strict global type contracts (SafetyMetricsPayload) to unify semantic signatures across the application and eliminate circular dependencies.

ingest_pipeline.py: Executes an idempotent ETL loop. It configures the database schema, enforces performance-tuned SQLite constraints (PRAGMA journal_mode=WAL), compiles target analytical indexes, and batch-loads api records using low-overhead database methods.

query_engine.py: An isolated, read-only analytics driver. It combines numerical extractions into a single-pass query sequence to minimize disk I/O round-trips.

reasoning_engine.py: Constructs mathematically constrained prompts and handles local inference orchestration via Ollama. It safely extracts logic chains using isolated structural token parsers.

validation_engine.py: A deterministic runtime auditor. It utilizes set intersection logic to verify that generated narratives explicitly and accurately reflect underlying metrics, outputting an immutable validation status contract.

app.py: A stateless presentation layer. It manages real estate allocation and drives the user execution journey lineally from raw data metrics up to the final trust verdict.


🔄 The Three-Stage Trust Pipeline

[ SQLite Relational C-Substrate ]
                 │
                 ▼
  ┌─────────────────────────────┐
  │  Stage 1: Relational Math   │ ──► Extracts absolute statistical evidence
  └──────────────┬──────────────┘
                 │ (SafetyMetricsPayload)
                 ▼
  ┌─────────────────────────────┐
  │  Stage 2: Bounded Inference │ ──► Local multi-tier model reasoning (e2b / e4b)
  └──────────────┬──────────────┘
                 │ (InferenceResult)
                 ▼
  ┌─────────────────────────────┐
  │  Stage 3: Numeric Audit     │ ──► Intersects narrative tokens against math truth
  └─────────────────────────────┘


Stage 1 (Relational Truth): Raw data is fetched, aggregated, and displayed directly from the SQLite database.

Stage 2 (Bounded Context): The model processes the exact numbers from Stage 1. It is explicitly prohibited from leveraging external ungrounded clinical memory or producing speculative claims.

Stage 3 (Validation Output): The narrative output is parsed and evaluated. If the model fails to include the core statistical parameters, the pipeline intercepts the execution thread, exposes the semantic drift, and triggers an override.

🚀 Installation & Deployment
Prerequisites
Python 3.9+

Ollama App running locally in the background.

1. Initialize Environment and Dependencies
Clone the repository to your workspace, open your terminal, and install the required core packages:


pip install streamlit ollama
2. Run the Data Ingestion Pipeline
Bootstrap the optimized SQLite framework and pull the latest production records from the openFDA stream:


python ingest_pipeline.py
3. Fetch Local Reasoning Models
Ensure you have the required inference tiers downloaded locally inside your Ollama environment:


ollama pull gemma4:e2b
ollama pull gemma4:e4b
(Note: If you are running different model architectures, update the mapping parameters inside app.py to match your active local CLI strings.)

4. Boot the Interactive Console Interface
Launch the dashboard locally to audit clinical trends through the multi-tier trust framework:


streamlit run app.py