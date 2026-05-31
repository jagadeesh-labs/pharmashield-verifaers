# Contributing to PharmaShield VeriFAERS

Thanks for your interest. This project is part of **Jagadeesh Labs** and is developed in the open under the [Apache 2.0 License](LICENSE).

Contributions of any size are welcome — bug reports, fixes, tests, docs, model improvements, or new ideas. Please read this short guide first.

---

## Before you contribute

By submitting a contribution (a pull request, patch, or any other change), you agree that:

1. Your contribution is your own original work, or you have the right to submit it.
2. Your contribution is provided under the project's [Apache 2.0 License](LICENSE).
3. You agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
4. You understand that this project is **decision-support tooling, not a clinical or regulatory device** (see `NOTICE`). Contributions that misrepresent the project's safety or validation claims will not be accepted.

No CLA is required at this time.

---

## Ways to contribute

- **Report a bug** — open an Issue with steps to reproduce, expected vs. actual behavior, and environment details.
- **Suggest an improvement** — open an Issue describing the use case and the proposed change.
- **Fix or improve code** — open a Pull Request (see workflow below).
- **Improve documentation** — typos, clarifications, examples, model cards.
- **Report a security vulnerability** — see [SECURITY.md](SECURITY.md) (do **not** open a public Issue).

---

## Pull request workflow

1. **Fork** the repository and create a feature branch from `main`:
   ```
   git checkout -b feat/short-description
   ```
2. **Make focused, atomic commits.** One logical change per commit; clear messages.
3. **Add or update tests** for any behavior change.
4. **Run the local checks** before opening the PR:
   - Linting: `ruff check .` (or the configured linter)
   - Type checks: `mypy .` (where applicable)
   - Tests: `pytest`
5. **Open a Pull Request** to `main`. Include:
   - What changed and why
   - How it was tested
   - Any relevant Issue numbers
6. **Respond to review feedback.** PRs are typically reviewed within a reasonable timeframe; please be patient.

---

## Coding standards

- **Python style:** PEP 8, enforced via Ruff. Type hints expected on public APIs.
- **Docstrings:** Google style for any non-trivial function or class.
- **Tests:** `pytest` with reproducible seeds. Prefer small, fast unit tests; reserve integration tests for the trust pipeline and ETL adapters.
- **Reproducibility is non-negotiable:** pin random seeds, version data snapshots, and ensure benchmark scripts are runnable end-to-end by a third party.
- **Honesty in metrics:** report confidence intervals, baselines, and negative results. Do not claim accuracy without statistical context.

---

## Domain-specific contribution rules

PharmaShield operates in a regulated domain. The following rules are stricter than standard OSS projects:

- **Track Alpha (deterministic) outputs are authoritative.** Any change that lets the LLM (Track Beta) influence numeric outputs without going through the validation engine will be rejected.
- **Audit log is append-only.** Contributions that alter audit-log semantics, hash chaining, or provenance fields require explicit maintainer approval.
- **No clinical or regulatory advice in code, comments, or docs.** Frame outputs as decision-support, never as recommendations.
- **PII / patient data:** never commit real patient-level data, even from public datasets that may contain re-identifiable fields. Use synthetic or aggregated samples in tests.

---

## Questions

For non-security questions, open an Issue or start a Discussion.
For security issues, see [SECURITY.md](SECURITY.md).

— Jagadeesh Labs
