"""Fixtures partagées : connexion en transaction jamais commitée, base de connaissance réelle."""

from __future__ import annotations

import pytest

from src.data.database import connect
from src.data.knowledge_base import load_knowledge_base


@pytest.fixture()
def conn():
    """Connexion vers la VRAIE base Postgres, dans une transaction annulée à la fin du test.

    `escalader_vers_un_hu
    main` et `repondre_a_la_question` ne font jamais
    `conn.commit()` elles-mêmes (voir leur docstring) — c'est ce qui permet
    d'appeler ces fonctions ici sur de vraies lignes de `seed.sql` (une
    conversation existante, un client existant) sans jamais modifier
    durablement les données de développement : le `rollback()` ci-dessous
    annule tout ce que le test a écrit.
    """
    connection = connect()
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.fixture(scope="session")
def knowledge_base():
    """Les vraies fiches PDF (19), chargées une seule fois pour toute la session de test."""
    return load_knowledge_base()
