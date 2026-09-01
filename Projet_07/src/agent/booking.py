"""Réservation : la seule action de l'agent qui écrit dans la base, avec garde-fou."""

from __future__ import annotations

import sqlite3
from datetime import datetime

SQL_INSERT_RESERVATION = """
    INSERT INTO reservations
        (client, destination, date_depart, nuits, voyageurs, vol, hotel, activites, prix_total, reservee_le)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def book_trip(conn: sqlite3.Connection, voyage: dict | None, client: str, confirme: bool = False) -> str:
    """Enregistre le voyage dans la table `reservations`, seulement si confirmé.

    LE GARDE-FOU : tant que `confirme` vaut False, rien n'est écrit dans la
    base — la fonction se contente de décrire ce qu'elle ferait. C'est le
    principe "action irréversible = confirmation explicite obligatoire".
    """
    if voyage is None:
        return "Rien à réserver : aucun voyage n'a été trouvé."

    if not confirme:
        return (f"Rien n'a été réservé. Le voyage à {voyage['destination']} coûterait "
                f"{voyage['prix_total']:.0f} EUR par personne, soit "
                f"{voyage['prix_total'] * voyage['voyageurs']:.0f} EUR au total. "
                f"Il faut confirmer pour que la réservation soit enregistrée.")

    conn.execute(SQL_INSERT_RESERVATION, (
        client, voyage["destination"], voyage["date_depart"], voyage["nuits"],
        voyage["voyageurs"], voyage["vol"]["numero"], voyage["hotel"]["hotel"],
        ", ".join(a["nom"] for a in voyage["activites"]),
        voyage["prix_total"] * voyage["voyageurs"],
        datetime.now().strftime("%Y-%m-%d %H:%M"),
    ))
    conn.commit()

    return (f"C'est réservé pour {client} : {voyage['destination']}, "
            f"{voyage['nuits']} nuits, {voyage['prix_total'] * voyage['voyageurs']:.0f} EUR au total.")
