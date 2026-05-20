"""
PharmaShield - Deterministic Query Engine
Strictly executes read-only analytical queries against the SQLite truth layer.
"""

import os
import sqlite3
from typing import Dict, List, Union

# -------------------------------------------------------------------
# CONFIGURATION & CONSTANTS
# -------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_TARGET = os.path.join(BASE_DIR, "database", "pharma_shield.db")

# High-level configuration fallback assets
DEFAULT_REACTIONS = ["DIARRHEA", "LACTIC ACIDOSIS", "NAUSEA"]

# -------------------------------------------------------------------
# CORE ANALYTICAL READS
# -------------------------------------------------------------------


def fetch_safety_metrics(target_drug: str, target_reaction: str) -> Dict[str, Union[int, float, str]]:
    """
    Extracts counts, severity indices, and age means in a single database pass.
    """
    try:
        with sqlite3.connect(DB_TARGET) as conn:
            cursor = conn.cursor()

            # Single pass aggregation eliminates an entire disk I/O round-trip
            cursor.execute(
                """
                SELECT COUNT(*), SUM(severity), AVG(age) 
                FROM safety_signals 
                WHERE drug = ? AND reaction = ?
                """,
                (target_drug, target_reaction),
            )
            
            row = cursor.fetchone()
            total_cases = row[0] or 0
            severe_cases = row[1] or 0
            avg_age = round(row[2], 1) if row[2] is not None else "N/A"

        return {
            "total_cases": total_cases,
            "severe_cases": severe_cases,
            "average_age_years": avg_age,
        }
    except sqlite3.OperationalError as error:
        print(f"[ERROR] Query engine failure: {error}")
        return {"total_cases": 0, "severe_cases": 0, "average_age_years": "N/A"}


def get_available_reactions() -> List[str]:
    """Populates interface control options dynamically from dataset state."""
    try:
        with sqlite3.connect(DB_TARGET) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT reaction 
                FROM safety_signals 
                ORDER BY reaction ASC 
                LIMIT 50
                """
            )
            reactions = [r[0] for r in cursor.fetchall()]
            return reactions if reactions else DEFAULT_REACTIONS
    except sqlite3.OperationalError as error:
        print(f"[ERROR] Query engine dropdown extraction failed: {error}")
        return DEFAULT_REACTIONS

def debug_available_reactions() -> None:
    with sqlite3.connect(DB_TARGET) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT reaction, COUNT(*)
            FROM safety_signals
            GROUP BY reaction
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """)

        for row in cursor.fetchall():
            print(row)

def debug_top_reactions() -> None:
    with sqlite3.connect(DB_TARGET) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT reaction, COUNT(*)
            FROM safety_signals
            GROUP BY reaction
            ORDER BY COUNT(*) DESC
            LIMIT 20
        """)

        rows = cursor.fetchall()

        for reaction, count in rows:
            print(f"{reaction}: {count}")

if __name__ == "__main__":
    debug_top_reactions()