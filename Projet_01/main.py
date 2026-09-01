"""Point d'entrée : construit la base, lance l'étude business, affiche la recommandation.

Usage :
    python main.py
"""

from __future__ import annotations

from src.database import build_database, table_counts
from src.report import print_recommendation, run_study


def main() -> None:
    conn = build_database()
    print("Base construite :", table_counts(conn))

    results = run_study(conn)
    print_recommendation(results)

    conn.close()


if __name__ == "__main__":
    main()
