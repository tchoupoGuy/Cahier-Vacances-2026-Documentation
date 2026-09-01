"""Étude business complète : quelle destination renforcer l'été prochain ?

Reproduit, sous forme de script réutilisable, l'enchaînement d'étapes du
notebook : état des réservations, chiffre d'affaires par destination,
demande récurrente, profil clientèle, clients jamais démarchés,
positionnement prix, clients fidèles, puis une recommandation finale
avec graphique.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt

from . import queries

FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"

TOP_ROUTE_FLIGHT_NUMBER = "AF5501"  # le vol vedette identifié par l'étude (Nice -> New York JFK)


def run_study(conn: sqlite3.Connection, *, save_figure: bool = True) -> dict:
    """Exécute l'étude étape par étape et renvoie tous les résultats intermédiaires."""

    results = {
        "booking_status": queries.booking_status_breakdown(conn),
        "revenue_by_destination": queries.revenue_by_destination(conn),
        "recurring_demand": queries.recurring_demand_destinations(conn, min_bookings=1),
        "top_route_passengers": queries.passengers_on_flight(conn, TOP_ROUTE_FLIGHT_NUMBER),
        "never_booked": queries.passengers_never_booked(conn),
        "above_average_price": queries.above_average_price_flights(conn),
        "loyal_passengers": queries.loyal_passengers(conn, min_bookings=2),
    }

    if save_figure:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        ax = results["recurring_demand"].plot(
            kind="bar", x="destination", y="total_revenue", legend=False, color="steelblue"
        )
        ax.set_title("Chiffre d'affaires par destination (réservations confirmées, demande récurrente)")
        ax.set_ylabel("Chiffre d'affaires (euros)")
        ax.set_xlabel("")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "revenue_by_destination.png", dpi=150)
        plt.close()

    return results


def print_recommendation(results: dict) -> None:
    top = results["recurring_demand"].iloc[0]
    print(f"Recommandation : renforcer la ligne vers {top['destination']}.")
    print(
        f"  - Chiffre d'affaires confirmé : {top['total_revenue']:.0f} EUR "
        f"sur {top['nb_bookings']} réservations récurrentes."
    )
    print(f"  - Profil clientèle sur le vol vedette ({TOP_ROUTE_FLIGHT_NUMBER}) :")
    print(results["top_route_passengers"].to_string(index=False))
    print(f"  - {len(results['never_booked'])} client(s) jamais démarché(s), à cibler pour le lancement.")
    print(f"  - {len(results['loyal_passengers'])} client(s) fidèle(s), ambassadeurs prioritaires.")
