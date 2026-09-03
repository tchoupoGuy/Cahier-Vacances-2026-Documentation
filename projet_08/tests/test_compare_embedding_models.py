"""Teste l'extraction de la vérité terrain (scripts/compare_embedding_models.py),
la partie du benchmark qui ne dépend d'aucun modèle réseau — la seule qui a
vraiment besoin d'un test : si elle extrait les mauvaises paires
(question, id), tout le reste du benchmark mesure n'importe quoi.
"""

from __future__ import annotations

import pandas as pd

from scripts.compare_embedding_models import SEPARATEUR_FORMULATIONS, extraire_verite_terrain


def test_extrait_une_paire_par_formulation():
    kb = pd.DataFrame([{
        "id": "KB-001",
        "formulations_clients": (
            f"{SEPARATEUR_FORMULATIONS} Comment annuler ma commande ? "
            f"{SEPARATEUR_FORMULATIONS} Je veux supprimer ma commande."
        ),
    }])

    paires = extraire_verite_terrain(kb)

    assert paires == [
        ("Comment annuler ma commande ?", "KB-001"),
        ("Je veux supprimer ma commande.", "KB-001"),
    ]


def test_plusieurs_fiches_donnent_des_paires_independantes():
    kb = pd.DataFrame([
        {"id": "KB-001", "formulations_clients": f"{SEPARATEUR_FORMULATIONS} Question A ?"},
        {"id": "KB-002", "formulations_clients": f"{SEPARATEUR_FORMULATIONS} Question B ?"},
    ])

    paires = extraire_verite_terrain(kb)

    assert paires == [("Question A ?", "KB-001"), ("Question B ?", "KB-002")]


def test_formulation_vide_est_ignoree():
    kb = pd.DataFrame([{
        "id": "KB-001",
        "formulations_clients": f"{SEPARATEUR_FORMULATIONS}   {SEPARATEUR_FORMULATIONS} Une vraie question ?",
    }])

    paires = extraire_verite_terrain(kb)

    assert paires == [("Une vraie question ?", "KB-001")]


def test_sur_la_vraie_base_de_connaissance(knowledge_base):
    """Vérité terrain extraite des 19 vraies fiches PDF : chaque fiche doit
    fournir au moins une question, et toutes les questions doivent référencer
    un id de fiche qui existe réellement dans la base.
    """
    paires = extraire_verite_terrain(knowledge_base)

    assert len(paires) >= len(knowledge_base)  # au moins une formulation par fiche

    ids_connus = set(knowledge_base["id"])
    ids_references = {id_attendu for _, id_attendu in paires}
    assert ids_references <= ids_connus

    # Exemple connu (voir data/knowledge_base/commandes/KB-001_annuler-une-commande.pdf) :
    questions_kb001 = [q for q, id_ in paires if id_ == "KB-001"]
    assert "Comment annuler ma commande ?" in questions_kb001
