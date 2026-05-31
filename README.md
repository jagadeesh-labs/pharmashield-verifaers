# PharmaShield VeriFAERS

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/Docs-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![Status](https://img.shields.io/badge/status-pre--MVP-orange.svg)](docs/PROJECT_BRIEF.md)

> An open project by **Jagadeesh Labs** — code is licensed under [Apache 2.0](LICENSE); documentation is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

PharmaShield VeriFAERS is built around one strict idea: when an AI summarizes drug-safety data, it should never be trusted to produce the numbers itself. The system ingests post-market adverse-event reports from the openFDA API, computes the statistics deterministically, and lets a language model only *explain* those results in plain language — with a separate check that flags any summary whose numbers don't match the source data.

## The core idea — bounded trust

It separates two jobs that most AI tools wrongly merge:

- **The math is the truth.** Counts and summary statistics are computed directly from the database. These values are authoritative.
- **The language model only interprets.** It receives the computed numbers and writes a readable summary. It is never the source of a fact.
- **A validation step audits the summary.** If the narrative adds or drops a number, the mismatch is caught and the output is flagged.

The goal is auditability: every figure in a summary should trace back to a database value.

## Status

**Pre-MVP — under active development.** This repository currently holds an early prototype, and the architecture is being migrated:

| Layer | Prototype (current code) | Target (see docs) |
| --- | --- | --- |
| Database | SQLite | PostgreSQL via Supabase |
| Interface | Streamlit | FastAPI + React |
| LLM runtime | local Ollama | Hugging Face Inference |

The authoritative design lives in [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Where this README and the docs differ, treat the docs as current.

## Repository layout

```text
app.py                 # prototype UI (Streamlit)
ingest_pipeline.py     # openFDA ingestion + database bootstrap
query_engine.py        # deterministic statistical queries
reasoning_engine.py    # bounded LLM summary (interpretation only)
validation_engine.py   # numeric drift check on the summary
shared_types.py        # shared type definitions
test_stack.py          # integration test harness
database/              # local prototype database
docs/                  # project brief + architecture (source of truth)
```


## Roadmap

1. Run the prototype end-to-end on a single drug and metric.
2. Migrate the data layer to Supabase / PostgreSQL.
3. Add the statistical and ML layers with reproducible benchmarks.
4. Replace the interface with FastAPI + React.
5. Add observability and publish reproducible results.

Detailed scope and honest limitations are documented in the [project brief](docs/PROJECT_BRIEF.md).

## Disclaimer

PharmaShield VeriFAERS is decision-support tooling. It is **not** a diagnostic device, **not** a substitute for professional clinical or regulatory judgment, and **not** validated for clinical use. See [`NOTICE`](NOTICE).

## License

Code is licensed under the [Apache License 2.0](LICENSE); documentation under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright (c) 2026 Jagadeesh Labs.
