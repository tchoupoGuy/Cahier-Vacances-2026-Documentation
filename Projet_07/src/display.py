"""Affichages en console : vols, hôtels, voyage complet, proposition en texte."""

from __future__ import annotations


def print_flights(vols, n: int = 5) -> None:
    if vols.empty:
        print("  aucun vol")
        return
    for _, v in vols.head(n).iterrows():
        print(f"  {v['numero']:8s} {v['origine']:10s} -> {v['heure_depart']}  "
              f"{v['duree_h']:.1f} h  {v['prix_eur']:6.0f} EUR  ({v['places_restantes']:.0f} places)")


def print_hotels(hotels) -> None:
    for _, h in hotels.iterrows():
        print(f"  {h['score']:.3f}  {h['hotel']:22s} {h['etoiles']}*  {h['prix_nuit']:5.0f} EUR/nuit  "
              f"note {h['note']:.1f}/10 ({h['avis']} avis)")
        print(f"          {h['resume'][:145]}...")


def print_trip(voyage: dict | None, journal: list[str] | None = None) -> None:
    if voyage is None:
        print("Aucun voyage ne rentre dans ce budget.")
        if journal:
            print("\nCe que l'agent a tenté :")
            for ligne in journal:
                print(f"  - {ligne}")
        return

    print(f"=== {voyage['destination']}, {voyage['nuits']} nuits, {voyage['voyageurs']} voyageur(s) ===")
    print(f"  Vol    {voyage['vol']['numero']} au départ de {voyage['vol']['origine']} "
          f"le {voyage['date_depart']} à {voyage['vol']['heure_depart']}   "
          f"{voyage['vol']['prix_eur']:.0f} EUR/pers")
    print(f"  Hôtel  {voyage['hotel']['hotel']}, {voyage['hotel']['prix_nuit']:.0f} EUR/nuit : "
          f"{voyage['hotel']['prix_nuit'] * voyage['nuits']:.0f} EUR")
    if voyage["activites"]:
        print("  Activités :")
        for a in voyage["activites"]:
            print(f"      {a['nom']:38s} {a['prix_eur']:5.0f} EUR")
    else:
        print("  Activités : aucune")
    print(f"  {'-' * 52}")
    print(f"  TOTAL  {voyage['prix_total']:.0f} EUR   (budget : {voyage['budget_max']:.0f} EUR)")

    if journal:
        print("\nCe que l'agent a fait, et ce qu'il a remarqué :")
        for ligne in journal:
            print(f"  - {ligne}")


def trip_description(voyage: dict | None, journal: list[str] | None = None) -> str:
    """Rédige la proposition de voyage en texte, uniquement à partir des chiffres calculés.

    Aucun LLM ici : rien de ce qui est écrit ne peut être inventé.
    """
    if voyage is None:
        return ("Je n'ai rien trouvé qui rentre dans ce budget. Essaie d'augmenter le budget "
                "ou de partir un autre jour : les vols du week-end sont nettement plus chers.")

    v, h = voyage["vol"], voyage["hotel"]
    phrases = [
        f"Départ de {v['origine']} le {voyage['date_depart']} à {v['heure_depart']}, "
        f"{v['duree_h']:.0f} h de vol pour {v['prix_eur']:.0f} euros.",
        f"Tu dors {voyage['nuits']} nuits au {h['hotel']}, à {h['prix_nuit']:.0f} euros la nuit.",
    ]
    if voyage["activites"]:
        noms = ", ".join(a["nom"] for a in voyage["activites"])
        phrases.append(f"Au programme : {noms}.")
    phrases.append(f"Le tout revient à {voyage['prix_total']:.0f} euros par personne, "
                    f"pour un budget de {voyage['budget_max']:.0f}.")

    remarque = ("au passage", "en revanche")
    sacrifices = [l for l in journal or [] if not l.startswith(remarque)]
    remarques = [l for l in journal or [] if l.startswith(remarque)]

    if sacrifices:
        phrases.append("Pour y arriver, " + " puis ".join(sacrifices).lower() + ".")
    for ligne in remarques:
        phrases.append(ligne[0].upper() + ligne[1:] + ".")
    return " ".join(phrases)
