"""Point d'entrée : démo de l'agent de support client, de bout en bout.

Usage :
    uv run python main.py

Nécessite : la base Postgres démarrée (docker-compose up -d, avec le schéma
et les données déjà appliqués), et un accès réseau la première fois
(téléchargement du modèle d'embeddings Hugging Face).

Ce script ÉCRIT réellement dans support_messages et peut faire passer la
conversation de test à 'escalated' — ce n'est pas un test automatisé (voir
tests/, avec le pattern transaction + rollback), c'est une démo manuelle
contre la vraie base, pour voir si le seuil de confiance (0.6) est réaliste.
"""

from __future__ import annotations

import logging
import sys

from src.agent.repondre_a_la_question import repondre_a_la_question
from src.data.database import connect
from src.data.knowledge_base import load_knowledge_base
from src.embeddings.encoder import encoder_la_base_de_connaissance, load_encoder

logger = logging.getLogger(__name__)

# Trois cas volontairement différents : une question nette (devrait répondre
# du premier coup), une question polie et diluée (devrait déclencher la
# reformulation, ou pas — c'est justement ce qu'on veut observer avec le
# vrai modèle), et une question hors sujet (devrait escalader).
QUESTIONS_DE_TEST = [
    "Comment annuler ma commande ?",
    "Comment faire quand on est pas livré ?",
    "Bonjour, pourriez-vous me dire s'il vous plaît comment modifier l'adresse de livraison ? Merci d'avance.",
    "Quel temps fera-t-il demain à Paris ?",
]

CONVERSATION_ID_TEST = 2  # conversation 'open' du client 2, telle que seedée dans scripts/02-seed.sql


def main() -> None:
    # Configuré UNE fois, ici, au point d'entrée — jamais dans un module de
    # src/ : une librairie ne décide pas comment ses appelants veulent
    # afficher leurs logs (fichier, format JSON, niveau...), elle se contente
    # de logger. C'est à l'application (ce script) de configurer l'affichage.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s: %(message)s")

    conn = connect()
    try:
        knowledge_base = load_knowledge_base()
        encoder = load_encoder()
        # Indexé UNE FOIS ici, avant la boucle sur les questions — jamais recalculé
        # à chaque question (voir le docstring de encoder_la_base_de_connaissance).
        knowledge_base = encoder_la_base_de_connaissance(knowledge_base, encoder)
        print(f"{len(knowledge_base)} fiches de la base de connaissance chargées et indexées\n")

        for question in QUESTIONS_DE_TEST:
            print(f"Question : {question}")
            resultat = repondre_a_la_question(conn, knowledge_base, encoder, CONVERSATION_ID_TEST, question)
            conn.commit()  # repondre_a_la_question ne commit plus elle-même : c'est à l'appelant de le faire
            for ligne in resultat["journal"]:
                print(f"  - {ligne}")
            if resultat["escalade"]:
                print("  => escaladé, aucune réponse automatique\n")
            else:
                print(f"  => réponse (score {resultat['score']:.2f}) : {resultat['reponse']}\n")
    except Exception:
        # La frontière la plus externe : ici, et seulement ici, une erreur
        # inattendue s'arrête proprement (message clair + code de sortie 1)
        # plutôt que de remonter une trace Python brute à la console.
        logger.exception("la démo s'est arrêtée sur une erreur inattendue")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
