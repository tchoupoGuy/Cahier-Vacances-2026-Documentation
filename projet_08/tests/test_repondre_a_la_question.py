"""Teste la boucle de l'agent avec un encodeur scripté (déterministe, sans réseau)

et une fiche synthétique, sur une VRAIE conversation de seed.sql — protégée
par le rollback du fixture `conn` (voir tests/conftest.py).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.agent.repondre_a_la_question import _reformuler, repondre_a_la_question
from src.data.database import query
from src.embeddings.encoder import encoder_la_base_de_connaissance

KB_SYNTHETIQUE = pd.DataFrame([{"id": "KB-TEST", "resume": "réponse de test", "a_encoder": "fiche de test"}])

CONVERSATION_ID = 7  # 'open' dans seed.sql, indépendante des conversations utilisées ailleurs


def _scripted_encode(bons_textes: set[str]):
    """Encodeur factice : score 1.0 pour un texte listé tel quel, 0.0 sinon.

    Contrairement à un encodeur par sac de mots (FakeEncoder), celui-ci
    contrôle exactement le score AVANT et APRÈS reformulation, ce qui est
    le seul moyen de tester la branche de reformulation de façon fiable
    (un sac de mots n'est pas dilué par des mots en trop, donc ne peut pas
    démontrer l'effet de la reformulation).
    """

    def encode_fn(_encoder, texts):
        return np.array([[1.0] if t in bons_textes else [0.0] for t in texts])

    return encode_fn


def _messages_de(conn, conversation_id):
    return query(conn, "SELECT * FROM support_messages WHERE conversation_id = %s", (conversation_id,))


def test_responds_directly_when_the_first_search_is_confident(conn):
    # Compte avant/après plutôt qu'un total absolu : la table n'est pas garantie
    # vide pour cette conversation (des essais manuels antérieurs peuvent y
    # avoir laissé des lignes réelles) — seul le DELTA prouve ce que CE test a fait.
    avant = _messages_de(conn, CONVERSATION_ID)

    encode_fn = _scripted_encode({"fiche de test", "Comment faire ?"})
    kb_indexee = encoder_la_base_de_connaissance(KB_SYNTHETIQUE, encoder=None, encode_fn=encode_fn)
    resultat = repondre_a_la_question(
        conn, kb_indexee, encoder=None, conversation_id=CONVERSATION_ID,
        question="Comment faire ?", seuil_confiance=0.6, encode_fn=encode_fn,
    )

    assert resultat["escalade"] is False
    assert resultat["fiche_id"] == "KB-TEST"
    assert len(resultat["journal"]) == 2  # recherche initiale + réponse envoyée, pas de reformulation

    apres = _messages_de(conn, CONVERSATION_ID)
    assert len(apres) == len(avant) + 1
    nouvelle_ligne = apres[~apres["id"].isin(avant["id"])].iloc[0]
    assert nouvelle_ligne["knowledge_article_id"] == "KB-TEST"
    assert nouvelle_ligne["ai_generated"] == 1


def test_responds_after_one_reformulation(conn):
    question = "Bonjour, pouvez-vous me dire comment faire ? Merci d'avance."
    reformulee = _reformuler(question)
    assert reformulee != question  # sinon le test ne prouve rien

    encode_fn = _scripted_encode({"fiche de test", reformulee})
    kb_indexee = encoder_la_base_de_connaissance(KB_SYNTHETIQUE, encoder=None, encode_fn=encode_fn)
    resultat = repondre_a_la_question(
        conn, kb_indexee, encoder=None, conversation_id=CONVERSATION_ID,
        question=question, seuil_confiance=0.6, encode_fn=encode_fn,
    )

    assert resultat["escalade"] is False
    assert len(resultat["journal"]) == 3
    assert "reformulation" in resultat["journal"][1]


def test_escalates_when_still_below_threshold_after_reformulation(conn):
    question = "Bonjour, pouvez-vous m'aider ? Merci d'avance."
    encode_fn = _scripted_encode(set())  # rien ne matche jamais, ni avant ni après reformulation
    kb_indexee = encoder_la_base_de_connaissance(KB_SYNTHETIQUE, encoder=None, encode_fn=encode_fn)

    resultat = repondre_a_la_question(
        conn, kb_indexee, encoder=None, conversation_id=CONVERSATION_ID,
        question=question, seuil_confiance=0.6, encode_fn=encode_fn,
    )

    assert resultat["escalade"] is True
    assert resultat["reponse"] is None

    statut = query(conn, "SELECT status FROM support_conversations WHERE id = %s", (CONVERSATION_ID,))
    assert statut["status"].iloc[0] == "escalated"
