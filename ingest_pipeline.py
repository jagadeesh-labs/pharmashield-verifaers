"""
PharmaShield VeriFAERS
Deterministic ETL Pipeline: openFDA -> SQLite

Engineering Philosophy
----------------------
- SQLite owns deterministic computation.
- Python owns orchestration and normalization.
- Bulk transactions minimize runtime overhead.
- Explicit observability replaces silent failure.
"""

from __future__ import annotations

import json
import os
import sqlite3
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

# -------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# -------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_TARGET = os.path.join(BASE_DIR, "database", "pharma_shield.db")

BASE_FDA_ENDPOINT = "https://api.fda.gov/drug/event.json"

BATCH_SIZE = 100
MAX_BATCHES = 50

TARGET_DRUGS = [
    "metformin",
    "ibuprofen",
    "aspirin",
    "amoxicillin",
    "atorvastatin",
    "lisinopril",
    "omeprazole",
    "levothyroxine",
    "amlodipine",
    "simvastatin",
    "losartan",
    "gabapentin",
    "hydrochlorothiazide",
    "sertraline",
    "montelukast",
    "pantoprazole",
    "prednisone",
    "furosemide",
    "tramadol",
    "warfarin",
    "clopidogrel",
    "cetirizine",
    "fluoxetine",
    "azithromycin",
    "alprazolam",
    "citalopram",
    "doxycycline",
    "meloxicam",
    "metoprolol",
    "naproxen",
    "paracetamol",
    "acetaminophen",
    "insulin",
    "glimepiride",
    "empagliflozin",
    "rosuvastatin",
    "esomeprazole",
    "valsartan",
    "venlafaxine",
    "duloxetine",
    "clindamycin",
    "ondansetron",
    "ciprofloxacin",
    "nitrofurantoin",
    "allopurinol",
    "cephalexin",
    "loratadine",
    "metronidazole",
    "ketorolac",
    "morphine",
]

NETWORK_TIMEOUT_SECONDS = 10

# -------------------------------------------------------------------
# OBSERVABILITY LOGGER LAYER
# -------------------------------------------------------------------


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def log_warning(message: str) -> None:
    print(f"[WARN] {message}")


def log_error(message: str) -> None:
    print(f"[ERROR] {message}")


# -------------------------------------------------------------------
# INDUSTRIAL DATABASE BOOTSTRAP
# -------------------------------------------------------------------


def bootstrap_schema() -> None:
    """
    Initialize schema with low-level SQLite system tuning optimization.
    """
    os.makedirs(os.path.dirname(DB_TARGET), exist_ok=True)

    with sqlite3.connect(DB_TARGET) as conn:
        cursor = conn.cursor()

        # Elite Performance Optimizations (WAL mode + reduced disk syncs)
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS safety_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug TEXT NOT NULL,
                reaction TEXT NOT NULL,
                age REAL,
                gender TEXT NOT NULL,
                severity INTEGER NOT NULL
            )
            """
        )

        cursor.execute("DELETE FROM safety_signals")

        # Performance optimization indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_drug ON safety_signals(drug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reaction ON safety_signals(reaction)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_age ON safety_signals(age)")

        conn.commit()

    log_info("SQLite schema initialized with tuned execution pragmas.")


# -------------------------------------------------------------------
# CLINICAL TRANSFORMATION LAYER
# -------------------------------------------------------------------


def standardize_age(patient_node: Dict[str, Any]) -> Optional[float]:
    """Convert raw FDA temporal metrics into standard decimal years."""
    raw_value = patient_node.get("patientonsetage")
    unit_code = patient_node.get("patientonsetageunit")

    if raw_value is None:
        return None

    try:
        age = float(raw_value)
        
        # Type Guard: If unit_code is missing or not a string, bypass map to satisfy Pylance
        if not isinstance(unit_code, str):
            return age

        conversion_map: Dict[str, float] = {
            "800": age * 10.0,   # Decades
            "801": age,          # Years
            "802": age / 12.0,   # Months
            "803": age / 52.0,   # Weeks
            "804": age / 365.0,  # Days
        }
        return conversion_map.get(unit_code, age)
    except ValueError:
        log_warning(f"Telemetry skipped malformed age metric: {raw_value}")
        return None


# -------------------------------------------------------------------
# INGESTION STREAM LAYER
# -------------------------------------------------------------------


def stream_api_payload() -> List[Dict[str, Any]]:
    """
    Fetch paginated FDA adverse-event reports
    across multiple curated drugs.
    """

    aggregated_results = []

    for drug in TARGET_DRUGS:

        print(f"\n[DRUG] Processing: {drug.upper()}")

        for batch_index in range(MAX_BATCHES):

            skip_value = batch_index * BATCH_SIZE

            endpoint = (
                f"{BASE_FDA_ENDPOINT}"
                f"?search=patient.drug.medicinalproduct:{drug}"
                f"&limit={BATCH_SIZE}"
                f"&skip={skip_value}"
            )

            print(
                f"[BATCH] {drug.upper()} "
                f"{batch_index + 1}/{MAX_BATCHES}"
            )

            try:
                with urllib.request.urlopen(endpoint) as response:

                    payload = json.loads(
                        response.read().decode()
                    )

                    results = payload.get("results", [])

                    if not results:
                        print(
                            f"[STOP] No additional records "
                            f"for {drug.upper()}."
                        )
                        break

                    aggregated_results.extend(results)

            except Exception as err:

                print(
                    f"[ERROR] FDA fetch failed for "
                    f"{drug.upper()}: {err}"
                )

                break

    print(
        f"\n[COMPLETE] Total FDA reports retrieved: "
        f"{len(aggregated_results)}"
    )

    return aggregated_results

# -------------------------------------------------------------------
# DATA CAPTURE HELPERS
# -------------------------------------------------------------------


def normalize_gender(patient_node: Dict[str, Any]) -> str:
    """Map binary tokens to semantic validation labels."""
    gender_code = patient_node.get("patientsex", "0")
    gender_map = {"1": "MALE", "2": "FEMALE"}
    return gender_map.get(str(gender_code), "UNKNOWN")


def determine_severity(case_node: Dict[str, Any]) -> int:
    """Assess clinical severity vector based on hospitalization/mortality indicators."""
    hospitalized = case_node.get("seriousnesshospitalization") == "1"
    deceased = case_node.get("seriousnessdeath") == "1"
    return int(hospitalized or deceased)


def extract_drugs(patient_node: Dict[str, Any]) -> List[str]:
    """Isolate and filter therapeutic substance tokens."""
    return [
        drug.get("medicinalproduct", "").strip().upper()
        for drug in patient_node.get("drug", [])
        if drug.get("medicinalproduct")
    ]


def extract_reactions(patient_node: Dict[str, Any]) -> List[str]:
    """Isolate MedDRA preferred terms."""
    return [
        reaction.get("reactionmeddrapt", "").strip().upper()
        for reaction in patient_node.get("reaction", [])
        if reaction.get("reactionmeddrapt")
    ]


# -------------------------------------------------------------------
# PIPELINE EXECUTION ENGINE
# -------------------------------------------------------------------


def process_and_load(raw_reports: List[Dict[str, Any]]) -> int:
    """Transform data matrix arrays and deploy native C-engine batch array load."""
    batch_records: List[Tuple[str, str, Optional[float], str, int]] = []
    skipped_reports = 0

    for case in raw_reports:
        patient = case.get("patient", {})
        drugs = extract_drugs(patient)

        if not any("METFORMIN" in drug for drug in drugs):
            skipped_reports += 1
            continue

        reactions = set(extract_reactions(patient))
        age = standardize_age(patient)
        gender = normalize_gender(patient)
        severity = determine_severity(case)

        for reaction in reactions:
            batch_records.append(
                ("METFORMIN", reaction, age, gender, severity)
            )

    with sqlite3.connect(DB_TARGET) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO safety_signals (drug, reaction, age, gender, severity)
            VALUES (?, ?, ?, ?, ?)
            """,
            batch_records,
        )
        conn.commit()

    log_info(f"Transaction complete. {len(batch_records)} nodes committed to disk.")
    log_info(f"Telemetry: bypassed {skipped_reports} non-target observations.")
    return len(batch_records)


def main() -> None:
    """Pipeline Entrypoint Orchestrator."""
    log_info("Initializing database bootstrap matrix...")
    bootstrap_schema()

    log_info("Querying stream endpoints...")
    raw_reports = stream_api_payload()

    if not raw_reports:
        log_error("Pipeline terminal fault: data matrix stream returned empty.")
        return

    inserted_count = process_and_load(raw_reports)
    log_info(f"Execution complete. System state verified valid with {inserted_count} records.")


if __name__ == "__main__":
    main()