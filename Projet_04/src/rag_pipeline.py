"""Les deux approches comparées par le projet : tout dans le prompt, puis le RAG."""

from __future__ import annotations

import pandas as pd

from src.generation.llm import generate_from_prompt
from src.generation.prompt import build_prompt
from src.retrieval.vector_store import VectorStore


def answer_naive(generator, full_context: str, question: str) -> str:
    """Acte 2 : on donne TOUTE la documentation au modèle à chaque question."""
    prompt = build_prompt(full_context, question)
    return generate_from_prompt(generator, prompt)


def answer_with_rag(generator, store: VectorStore, question: str, top_k: int = 2) -> tuple[str, pd.DataFrame]:
    """Acte 3 : on ne donne que les `top_k` rubriques les plus pertinentes (le vrai RAG).

    Returns (réponse, rubriques utilisées comme sources).
    """
    retrieved = store.search(question, top_k=top_k)
    context = "\n\n".join(retrieved["section"])
    prompt = build_prompt(context, question)
    answer = generate_from_prompt(generator, prompt)
    return answer, retrieved
