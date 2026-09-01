"""Recherche sémantique testée sur une base synthétique (2-3 fiches, mots-clés

sans ambiguïté), découplée des vraies fiches PDF — même principe qu'au
Projet 04 : un texte réel peut créer des collisions de mots-clés fragiles
et non représentatives de la mécanique de recherche elle-même.
"""

import pandas as pd

from src.embeddings.encoder import encoder_la_base_de_connaissance
from src.tools.chercher_dans_la_base_de_connaissance import chercher_dans_la_base_de_connaissance
from tests.fakes import FakeEncoder, fake_encode

KB_SYNTHETIQUE = pd.DataFrame([
    {"id": "KB-A", "resume": "annuler une commande", "a_encoder": "annuler commande"},
    {"id": "KB-B", "resume": "mot de passe oublié", "a_encoder": "mot passe oublie"},
    {"id": "KB-C", "resume": "délai de livraison", "a_encoder": "delai livraison"},
])
VOCABULARY = ["annuler", "commande", "mot", "passe", "livraison"]
ENCODER = FakeEncoder(VOCABULARY)

# Indexée une seule fois ici, comme main.py le fait avant sa boucle sur les
# questions — chercher_dans_la_base_de_connaissance attend désormais une base
# déjà indexée (colonne "vecteur"), pas le DataFrame brut.
KB_SYNTHETIQUE_INDEXEE = encoder_la_base_de_connaissance(KB_SYNTHETIQUE, ENCODER, encode_fn=fake_encode)


def test_returns_the_best_matching_fiche_first():
    resultats = chercher_dans_la_base_de_connaissance(
        KB_SYNTHETIQUE_INDEXEE, ENCODER, "je veux annuler ma commande", k=3, encode_fn=fake_encode,
    )

    assert resultats.iloc[0]["id"] == "KB-A"
    assert resultats.iloc[0]["score"] > resultats.iloc[1]["score"]


def test_respects_k():
    resultats = chercher_dans_la_base_de_connaissance(
        KB_SYNTHETIQUE_INDEXEE, ENCODER, "un problème de mot de passe", k=1, encode_fn=fake_encode,
    )

    assert len(resultats) == 1
    assert resultats.iloc[0]["id"] == "KB-B"


def test_no_keyword_overlap_gives_the_lowest_possible_score():
    resultats = chercher_dans_la_base_de_connaissance(
        KB_SYNTHETIQUE_INDEXEE, ENCODER, "bonjour", k=3, encode_fn=fake_encode,
    )

    assert (resultats["score"] == 0).all()
