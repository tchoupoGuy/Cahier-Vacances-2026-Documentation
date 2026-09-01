"""Construction du prompt envoyé au LLM."""

from __future__ import annotations

ROLE = (
    "Tu es l'assistant virtuel de l'Hôtel Le Belvédère, au bord du lac d'Annecy.\n"
    "Voici la documentation officielle de l'hôtel :"
)

CONSIGNE = (
    "Réponds en une ou deux phrases, uniquement à partir des informations "
    "de la documentation ci-dessus. Si l'information ne s'y trouve pas, réponds exactement : "
    '"Je ne sais pas, je vous invite à contacter la réception."'
)


def build_prompt(context: str, question: str) -> str:
    """Assemble le rôle, le contexte (documentation), la question et la consigne anti-hallucination.

    L'ordre et la mise en forme exacts comptent : le modèle étant
    déterministe, un prompt identique au caractère près garantit des
    réponses reproductibles.
    """
    return f"{ROLE}\n\n{context}\n\nQuestion d'un client : {question}\n{CONSIGNE}"
