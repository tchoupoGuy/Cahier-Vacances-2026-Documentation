"""Accès à la base de données Clients (customers, orders, order_items, payments, shipments, returns)."""

from __future__ import annotations

import logging
import os
import re

import pandas as pd
import psycopg
from dotenv import load_dotenv

# Charge .env une fois à l'import : DATABASE_URL devient disponible dans os.environ
# sans que quiconque ait besoin de l'exporter manuellement dans son shell.
load_dotenv()

logger = logging.getLogger(__name__)

# Ne remplace jamais un mot de passe par des espaces dans une URL affichée à
# l'utilisateur : ce module se contente de logger, jamais de configurer les
# handlers/le format (ça, c'est le travail du point d'entrée — voir main.py).
_MOT_DE_PASSE_RE = re.compile(r"(://[^:]+:)[^@]+(@)")


def _masquer_mot_de_passe(database_url: str) -> str:
    """Jamais le mot de passe en clair dans un message de log, même une erreur."""
    return _MOT_DE_PASSE_RE.sub(r"\1***\2", database_url)


def connect() -> psycopg.Connection:
    """Ouvre la base de données PostgreSQL.

    Aucun identifiant n'est écrit ici : DATABASE_URL (dans .env, jamais commité)
    est la SEULE source de vérité pour la connexion. Dupliquer host/user/password
    en dur dans le code créerait deux endroits à tenir synchronisés — et le jour
    où ils divergent (comme ça a été le cas ici avec un nom de base différent),
    l'erreur de connexion devient difficile à comprendre.

    Ne capture PAS l'erreur : elle est journalisée avec un message utile (le
    "quoi" et le "pourquoi possible"), puis relancée telle quelle. Cacher
    l'erreur ici empêcherait l'appelant de savoir que la connexion a échoué.
    """
    database_url = os.environ["DATABASE_URL"]
    try:
        return psycopg.connect(database_url)
    except psycopg.OperationalError:
        logger.exception(
            "connexion à %s impossible — vérifie que docker-compose est démarré "
            "(`docker-compose up -d`) et que le port dans .env correspond à celui "
            "publié par docker-compose.yml",
            _masquer_mot_de_passe(database_url),
        )
        raise


def query(conn: psycopg.Connection, sql: str, params: tuple = ()) -> pd.DataFrame:
    """Exécute une requête SQL PARAMÉTRÉE et renvoie le résultat en DataFrame.

    Attention au style de paramètre : psycopg utilise `%s`, pas `?` (le style
    SQLite utilisé dans les autres projets du cahier). `WHERE email = %s`,
    jamais de f-string avec une valeur insérée directement dans le texte.
    """
    return pd.read_sql_query(sql, conn, params=params)
