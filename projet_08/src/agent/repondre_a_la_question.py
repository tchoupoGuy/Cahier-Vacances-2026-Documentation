"""La boucle de l'agent : chercher une réponse, évaluer la confiance, corriger si besoin.

C'est ce fichier, et pas les outils pris séparément, qui mérite le nom
"agent" : il essaie, évalue son propre résultat contre un seuil, et corrige
UNE fois avant d'admettre qu'il ne sait pas répondre et de passer la main.
"""

from __future__ import annotations

import logging
import re

import pandas as pd
import psycopg

from src.embeddings.encoder import encode as default_encode
from src.tools.chercher_dans_la_base_de_connaissance import chercher_dans_la_base_de_connaissance
from src.tools.escalader_vers_un_humain import escalader_vers_un_humain

logger = logging.getLogger(__name__)

SEUIL_CONFIANCE_PAR_DEFAUT = 0.6

# Écrit ici, pas dans un outil séparé : c'est un détail d'implémentation de la
# boucle elle-même (comment elle reformule), pas un fait qu'on va chercher
# dans le monde extérieur — ça ne mérite pas le statut d'outil.
_FORMULES_A_RETIRER = re.compile(
    r"\b(bonjour|bonsoir|salut|merci(\s+d'avance)?|s'il (vous|te) pla[iî]t|svp|"
    r"je voudrais savoir|je voudrais|j'aimerais savoir|j'aimerais|"
    r"pouvez[- ]vous( me)?( dire)?|est[- ]ce que|"
    r"je (vous )?(contacte|écris)( pour)?)\b",
    re.IGNORECASE,
)

SQL_MESSAGE_REPONSE = """
INSERT INTO support_messages
    (conversation_id, sender_type, message, ai_generated, knowledge_article_id, confidence_score)
VALUES (%s, 'ai', %s, 1, %s, %s)
"""


def _reformuler(question: str) -> str:
    """Retire les formules de politesse et d'introduction, pour ne garder que le cœur de la demande.

    La SEULE correction que la boucle s'autorise avant d'escalader : une
    reformulation, pas dix — sans cette limite, l'agent pourrait reformuler
    indéfiniment sans jamais admettre qu'il ne sait pas répondre.
    """
    nettoye = _FORMULES_A_RETIRER.sub("", question)
    nettoye = " ".join(nettoye.split())
    return nettoye or question


def _meilleure_fiche(knowledge_base: pd.DataFrame, encoder, question: str, encode_fn) -> pd.Series:
    """Appelle l'outil de recherche et renvoie sa meilleure ligne. Laisse toute exception remonter :

    c'est `repondre_a_la_question` qui décide quoi faire d'un échec technique
    (elle traite ça comme un score nul et escalade), pas cette fonction.
    """
    resultats = chercher_dans_la_base_de_connaissance(knowledge_base, encoder, question, k=1, encode_fn=encode_fn)
    return resultats.iloc[0]


def repondre_a_la_question(
    conn: psycopg.Connection,
    knowledge_base: pd.DataFrame,
    encoder,
    conversation_id: int,
    question: str,
    *,
    seuil_confiance: float = SEUIL_CONFIANCE_PAR_DEFAUT,
    encode_fn=default_encode,
) -> dict:
    """Essaie de répondre à une question à partir de la base de connaissance, sinon escalade.

    La boucle : chercher, évaluer le score du meilleur résultat contre
    `seuil_confiance`. Si ça passe, répondre et journaliser la réponse. Sinon,
    reformuler UNE fois la question et chercher à nouveau. Si ça ne suffit
    toujours pas, escalader vers un humain — jamais répondre avec un score de
    confiance trop bas, même si le résultat semble plausible.

    Si la recherche elle-même échoue techniquement (modèle d'embeddings
    indisponible, erreur inattendue), c'est traité comme un échec de
    confiance, pas comme un crash : direction escalade, pas de trace Python
    renvoyée au client. Une conversation qui bascule vers un humain à cause
    d'un problème technique reste un meilleur résultat qu'une conversation
    perdue.

    Args:
        conn: connexion ouverte (voir src.data.database.connect).
        knowledge_base: le DataFrame INDEXÉ renvoyé par
            `embeddings.encoder.encoder_la_base_de_connaissance` — pas le
            DataFrame brut de `load_knowledge_base`. L'indexation doit être
            faite UNE FOIS avant la boucle sur les questions (voir main.py),
            jamais à chaque appel de cette fonction.
        encoder: le modèle renvoyé par load_encoder (ou une doublure de test).
        conversation_id: la conversation dans laquelle journaliser la réponse ou l'escalade.
        question: la question du client, telle qu'elle est posée.
        seuil_confiance: score minimum (0-1) pour répondre automatiquement.
        encode_fn: injectable pour les tests (par défaut : embeddings.encoder.encode).

    Returns:
        Un dict : {"reponse": str | None, "fiche_id": str | None, "score": float,
        "escalade": bool, "journal": list[str]}.

    Note:
        Ne fait jamais `conn.commit()` elle-même, ni via `escalader_vers_un_humain` :
        c'est à l'appelant de committer (ou d'annuler, en test) la transaction.
    """
    journal: list[str] = []
    logger.info("conversation %s : nouvelle question reçue", conversation_id)

    try:
        meilleure = _meilleure_fiche(knowledge_base, encoder, question, encode_fn)
        journal.append(f"recherche initiale : {meilleure['id']} (score {meilleure['score']:.2f})")
        logger.info("conversation %s : recherche initiale -> %s (score %.2f)",
                    conversation_id, meilleure["id"], meilleure["score"])

        if meilleure["score"] < seuil_confiance:
            question_reformulee = _reformuler(question)
            if question_reformulee != question:
                meilleure = _meilleure_fiche(knowledge_base, encoder, question_reformulee, encode_fn)
                journal.append(
                    f"reformulation ('{question_reformulee}') : "
                    f"{meilleure['id']} (score {meilleure['score']:.2f})"
                )
                logger.info("conversation %s : reformulation -> %s (score %.2f)",
                            conversation_id, meilleure["id"], meilleure["score"])
    except Exception:
        # La recherche sémantique a échoué techniquement (pas "aucun résultat
        # assez proche" : une vraie exception). On le journalise en détail
        # ici — la seule trace complète de l'erreur — puis on traite ça comme
        # une confiance nulle : direction escalade, sans propager le crash.
        logger.exception("conversation %s : échec technique de la recherche sémantique", conversation_id)
        meilleure = None

    if meilleure is None or meilleure["score"] < seuil_confiance:
        if meilleure is None:
            raison = "la recherche dans la base de connaissance a échoué techniquement"
        else:
            raison = (
                f"aucune fiche assez proche (meilleur score {meilleure['score']:.2f} "
                f"< seuil {seuil_confiance})"
            )
        message_escalade = escalader_vers_un_humain(conn, conversation_id, raison)
        journal.append(message_escalade)
        logger.info("conversation %s : escaladée (%s)", conversation_id, raison)
        return {
            "reponse": None,
            "fiche_id": None,
            "score": float(meilleure["score"]) if meilleure is not None else 0.0,
            "escalade": True,
            "journal": journal,
        }

    reponse = meilleure["resume"]
    # confidence_score est contraint entre 0 et 1 dans le schéma : on ne passe
    # ce point que si score >= seuil_confiance, donc jamais négatif tant que
    # seuil_confiance reste positif (le cas normal).
    conn.execute(SQL_MESSAGE_REPONSE, (conversation_id, reponse, meilleure["id"], float(meilleure["score"])))
    journal.append(f"réponse envoyée, fondée sur {meilleure['id']}")
    logger.info("conversation %s : réponse envoyée, fondée sur %s", conversation_id, meilleure["id"])

    return {
        "reponse": reponse,
        "fiche_id": meilleure["id"],
        "score": float(meilleure["score"]),
        "escalade": False,
        "journal": journal,
    }
