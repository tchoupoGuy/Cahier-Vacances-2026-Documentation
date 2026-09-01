"""Point d'entrée : construit l'assistant RAG de l'Hôtel Le Belvédère et répond à des questions.

Usage :
    python main.py

Nécessite un accès réseau la première fois (téléchargement des modèles
Hugging Face : Qwen2.5-0.5B-Instruct et le modèle d'embedding multilingue).
"""

from __future__ import annotations

import time
from pathlib import Path

from src.display import print_chat
from src.embeddings.embedder import load_embedder
from src.generation.llm import load_generator
from src.ingestion.formatter import add_markdown_sections, full_context
from src.ingestion.pdf_loader import load_pages
from src.rag_pipeline import answer_naive, answer_with_rag
from src.retrieval.vector_store import VectorStore

DOCS_DIR = Path(__file__).resolve().parent / "data" / "docs"

QUESTIONS = [
    "A quelle heure commence le check-in ?",
    "Le wifi est-il gratuit ?",
    "Combien coute une chambre Classique en basse saison ?",
    "Est-ce que vous acceptez les paiements en Bitcoin ?",
]


def main() -> None:
    pages = add_markdown_sections(load_pages(DOCS_DIR))
    context_md = full_context(pages)
    print(f"{len(pages)} rubriques chargées, {len(context_md.split())} mots au total.\n")

    generator = load_generator()

    print("=== Acte 2 : toute la documentation dans le prompt ===")
    start = time.time()
    for question in QUESTIONS:
        answer = answer_naive(generator, context_md, question)
        print_chat(question, answer)
    print(f"Temps total (acte 2) : {time.time() - start:.0f} s\n")

    embedder = load_embedder()
    store = VectorStore(pages, embedder)

    print("=== Acte 3 : RAG (uniquement les rubriques pertinentes) ===")
    start = time.time()
    for question in QUESTIONS:
        answer, sources = answer_with_rag(generator, store, question)
        print_chat(question, answer, sources)
    print(f"Temps total (acte 3) : {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
