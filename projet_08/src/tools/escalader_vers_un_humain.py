"""Outil : escalader une conversation vers un agent humain (garde-fou inclus)."""

from __future__ import annotations

import logging

import psycopg

logger = logging.getLogger(__name__)

SQL_ETAT_CONVERSATION = """
SELECT status
FROM support_conversations
WHERE id = %s
"""

SQL_ESCALADER = """
UPDATE support_conversations
SET status = 'escalated', updated_at = CURRENT_TIMESTAMP
WHERE id = %s
"""

SQL_MESSAGE_ESCALADE = """
INSERT INTO support_messages (conversation_id, sender_type, message, ai_generated)
VALUES (%s, 'ai', %s, 1)
"""


def escalader_vers_un_humain(conn: psycopg.Connection, conversation_id: int, raison: str) -> str:
    """Transfère une conversation à un agent humain, avec la raison de l'escalade.

    GARDE-FOU : une conversation déjà 'escalated' ou 'closed' n'est pas
    escaladée une seconde fois — la fonction renvoie un message qui le
    signale plutôt que d'insérer un doublon. Décision assumée, pas neutre :
    sans ce garde-fou, un agent qui rappellerait cet outil par erreur (ou
    dans une boucle mal bornée) spammerait la conversation de messages
    d'escalade identiques et laisserait une fausse impression d'urgence
    répétée à l'agent humain qui la reprendrait.

    Args:
        conn: connexion ouverte (voir src.data.database.connect).
        conversation_id: identifiant de la conversation (support_conversations.id).
        raison: pourquoi l'agent escalade (ex. score de confiance trop bas,
            question hors du périmètre de la base de connaissance).

    Returns:
        Un message décrivant ce qui a été fait (ou pourquoi rien ne l'a été).

    Note:
        Ne fait jamais `conn.commit()` elle-même : c'est à l'appelant (script
        de démo, endpoint, ou fixture de test) de décider quand valider la
        transaction — c'est ce qui permet aux tests d'annuler (`rollback`)
        tout ce que cette fonction écrit, sans jamais toucher la vraie base.
    """
    etat = conn.execute(SQL_ETAT_CONVERSATION, (conversation_id,)).fetchone()

    if etat is None:
        logger.warning("escalade demandée pour la conversation %s, introuvable", conversation_id)
        return f"Conversation {conversation_id} introuvable : rien n'a été escaladé."

    (status,) = etat
    if status in ("escalated", "closed"):
        logger.info("conversation %s déjà '%s' : garde-fou, pas de nouvelle escalade", conversation_id, status)
        return f"Conversation {conversation_id} déjà '{status}' : pas de nouvelle escalade."

    conn.execute(SQL_ESCALADER, (conversation_id,))
    conn.execute(SQL_MESSAGE_ESCALADE, (conversation_id, raison))

    # WARNING, pas INFO : chaque escalade est un cas où l'agent n'a pas su
    # répondre seul — un taux d'escalade anormalement élevé sur une période
    # donnée est précisément ce qu'une équipe doit pouvoir repérer dans ses logs.
    logger.warning("conversation %s escaladée à un agent humain — raison : %s", conversation_id, raison)
    return f"Conversation {conversation_id} transférée à un agent humain. Raison : {raison}"
