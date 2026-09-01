"""Le cœur de l'agent : compose un voyage, sacrifie dans un ordre réfléchi, explore les jours voisins.

C'est ici que la "boucle" prend tout son sens : essayer un plan, l'évaluer,
et si besoin corriger avant de réessayer — jamais s'arrêter au premier échec.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.agent.pricing import neighbouring_dates, price_trip
from src.embeddings.encoder import encode as default_encode
from src.tools.activities import find_activities
from src.tools.flights import find_flights
from src.tools.hotels import find_hotels

MAX_ITERATIONS = 30  # garde-fou anti-boucle infinie


def try_one_date(demande: dict, conn: sqlite3.Connection, brochures, encoder, *, verbose: bool = False,
                  encode_fn=default_encode):
    """Compose le meilleur voyage possible pour UN jour de départ donné.

    Arguments
    ---------
    demande -- dict avec destination, date_depart, nuits, voyageurs, budget_max, envie
    conn, brochures, encoder -- les sources de données de l'agent

    Returns
    -------
    (voyage, journal) -- voyage est None si rien ne rentre dans le budget.
    """
    vols = find_flights(conn, demande["destination"], demande["date_depart"], demande["voyageurs"])
    hotels = find_hotels(brochures, encoder, demande["destination"], demande["envie"], encode_fn=encode_fn)
    activites = find_activities(conn, demande["destination"])

    journal = []
    if vols.empty or hotels.empty:
        return None, ["aucun vol ou aucun hôtel disponible pour cette destination et cette date"]

    vol = vols.iloc[0]                              # le vol le moins cher
    retenues = activites.to_dict("records")          # toutes les activités, pour commencer
    impossible = False

    # Ordre d'essai des hôtels : le plus pertinent d'abord, puis ceux qui coûtent vraiment
    # moins cher que lui, du plus cher au moins cher (pour descendre en douceur).
    prix_du_premier = hotels.iloc[0]["prix_nuit"]
    replis = [j for j in range(1, len(hotels)) if hotels.iloc[j]["prix_nuit"] < prix_du_premier]
    ordre = [0] + sorted(replis, key=lambda j: hotels.iloc[j]["prix_nuit"], reverse=True)
    position = 0

    total = 0.0
    for _ in range(MAX_ITERATIONS):
        hotel = hotels.iloc[ordre[position]]
        total = price_trip(vol, hotel, retenues, demande["nuits"])

        if verbose:
            ecart = total - demande["budget_max"]
            verdict = "OK" if ecart <= 0 else f"dépasse de {ecart:.0f}"
            print(f"   {demande['date_depart'][8:]}/{demande['date_depart'][5:7]}  {hotel['hotel'][:20]:20s} "
                  f"vol {vol['prix_eur']:4.0f} + hôtel {hotel['prix_nuit'] * demande['nuits']:5.0f} "
                  f"+ sorties {sum(a['prix_eur'] for a in retenues):4.0f} = {total:6.0f} EUR   {verdict}")

        if total <= demande["budget_max"]:
            break  # le plan tient dans le budget

        payantes = [a for a in retenues if a["prix_eur"] > 0]

        if payantes:  # repli n°1 : sacrifier la sortie payante la plus chère
            plus_chere = max(payantes, key=lambda a: a["prix_eur"])
            retenues = [a for a in retenues if a is not plus_chere]
            position = 0  # on repart du meilleur hôtel, le budget vient de s'alléger
            journal.append(f"j'ai retiré « {plus_chere['nom']} » ({plus_chere['prix_eur']:.0f} EUR)")

        elif position + 1 < len(ordre):  # repli n°2 : un hôtel moins cher
            position += 1
            journal.append(f"{hotel['hotel']} restait trop cher, "
                            f"j'ai pris {hotels.iloc[ordre[position]]['hotel']} à la place")

        else:  # plus rien à relâcher
            impossible = True
            journal.append("je n'avais plus rien à sacrifier ce jour-là")

        if impossible:
            return None, journal

    voyage = {
        "destination": demande["destination"], "date_depart": demande["date_depart"],
        "nuits": demande["nuits"], "voyageurs": demande["voyageurs"],
        "vol": vol, "hotel": hotels.iloc[ordre[position]], "activites": retenues,
        "prix_total": total, "budget_max": demande["budget_max"],
    }
    return voyage, journal


def plan_trip(demande: dict, conn: sqlite3.Connection, brochures, encoder, *, verbose: bool = False,
              encode_fn=default_encode):
    """L'agent complet : compose le voyage demandé, puis explore les jours voisins.

    Il ne déplace JAMAIS la date tout seul : il signale une meilleure
    opportunité dans le journal, la décision reste à l'utilisateur.

    Returns
    -------
    (voyage, journal) -- voyage pour la date demandée (ou None), journal
    incluant les remarques sur les jours voisins.
    """
    voyage, journal = try_one_date(demande, conn, brochures, encoder, verbose=verbose, encode_fn=encode_fn)

    alternatives = []
    for autre_jour in neighbouring_dates(demande["date_depart"]):
        candidat, _ = try_one_date(dict(demande, date_depart=autre_jour), conn, brochures, encoder,
                                    verbose=verbose, encode_fn=encode_fn)
        if candidat is not None:
            alternatives.append(candidat)

    if not alternatives:
        return voyage, journal

    if voyage is None:
        secours = min(alternatives, key=lambda v: v["prix_total"])
        jour = datetime.strptime(secours["date_depart"], "%Y-%m-%d").strftime("%d/%m")
        journal.append(f"en revanche, en partant le {jour}, un voyage à "
                        f"{secours['prix_total']:.0f} EUR par personne devenait possible")
        return voyage, journal

    # On compare d'abord ce qu'il RESTE dans le voyage (nombre d'activités conservées), le
    # prix seulement en cas d'égalité : l'agent s'arrête dès qu'il repasse sous le budget,
    # donc tous les plans finissent proches du budget, et le prix seul ne discrimine rien.
    meilleure = max(alternatives, key=lambda v: (len(v["activites"]), -v["prix_total"]))
    sorties_en_plus = len(meilleure["activites"]) - len(voyage["activites"])
    economie = voyage["prix_total"] - meilleure["prix_total"]

    jour = datetime.strptime(meilleure["date_depart"], "%Y-%m-%d").strftime("%d/%m")
    if sorties_en_plus > 0:
        journal.append(f"au passage, en partant le {jour} vous gardiez "
                        f"{len(meilleure['activites'])} sorties au lieu de {len(voyage['activites'])}, "
                        f"pour {meilleure['prix_total']:.0f} EUR")
    elif economie >= 10:
        journal.append(f"au passage, en partant le {jour} le même programme revenait à "
                        f"{meilleure['prix_total']:.0f} EUR, soit {economie:.0f} EUR de moins par personne")

    return voyage, journal
