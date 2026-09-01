"""Point d'entrée : démo en console de l'agent de voyage, de bout en bout.

Usage :
    python main.py

Nécessite un accès réseau la première fois (téléchargement du modèle
d'embeddings Hugging Face utilisé pour la recherche d'hôtels).
"""

from __future__ import annotations

from src.agent.booking import book_trip
from src.agent.planner import plan_trip
from src.data.brochures import load_brochures
from src.data.database import connect
from src.display import print_trip, trip_description
from src.embeddings.encoder import load_encoder


def main() -> None:
    conn = connect()
    brochures = load_brochures()
    encoder = load_encoder()
    print(f"{len(brochures)} brochures d'hôtels chargées\n")

    demande = {
        "destination": "Barcelone", "date_depart": "2026-08-12", "nuits": 4,
        "voyageurs": 2, "budget_max": 750,
        "envie": "un hôtel pour la famille avec une piscine, et des visites dans la ville",
    }

    voyage, journal = plan_trip(demande, conn, brochures, encoder, verbose=True)
    print()
    print_trip(voyage, journal)
    print()
    print(trip_description(voyage, journal))

    print()
    print(book_trip(conn, voyage, "Marc"))  # sans confirmation : rien n'est écrit
    print(book_trip(conn, voyage, "Marc", confirme=True))  # avec confirmation


if __name__ == "__main__":
    main()
