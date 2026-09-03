"""Interface Gradio de l'assistant RAG — branchée directement sur src/.

Contrairement au notebook d'atelier dont cette page s'inspire (un exercice à
trous, avec un LLM et des PDF encodés en secours pour tourner isolément dans
Google Colab), cette version réutilise le pipeline RAG déjà construit et
testé de Projet_04 (`src/rag_pipeline.py::answer_with_rag`) : aucune logique
de recherche ni de génération n'est dupliquée ici, seulement l'habillage web.

Pour la lancer, depuis la racine du projet :
    python webapp/app.py

Ça ouvre l'interface en local (http://127.0.0.1:7860), inaccessible depuis
l'extérieur. Pour obtenir une adresse PUBLIQUE temporaire (quelques heures,
via le tunnel Gradio), passer --share explicitement :

    python webapp/app.py --share

Ce n'est JAMAIS activé par défaut : voir FEYNMAN.md ("Pièges") pour pourquoi
partager ce lien largement (LinkedIn, etc.) est une mauvaise idée même si
Gradio le permet techniquement.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr

from src.embeddings.embedder import load_embedder
from src.generation.llm import load_generator
from src.ingestion.formatter import add_markdown_sections
from src.ingestion.pdf_loader import load_pages
from src.rag_pipeline import answer_with_rag
from src.retrieval.vector_store import VectorStore

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"


def build_interface() -> gr.Interface:
    """Charge les modèles et les documents une seule fois, construit l'interface Gradio."""
    pages = add_markdown_sections(load_pages(DOCS_DIR))
    generator = load_generator()
    store = VectorStore(pages, load_embedder())

    def repondre(question: str) -> str:
        if not question.strip():
            return "Posez-moi une question sur l'Hôtel Le Belvédère !"
        answer, sources = answer_with_rag(generator, store, question)
        titres = ", ".join(sources["title"])
        return f"{answer}\n\n📎 Sources : {titres}"

    return gr.Interface(
        fn=repondre,
        inputs=gr.Textbox(label="Votre question", placeholder="Ex : le wifi est-il gratuit ?"),
        outputs=gr.Textbox(label="Réponse de l'assistant"),
        title="Assistant de l'Hôtel Le Belvédère 🏨",
        description="Répond à partir de la documentation officielle de l'hôtel (RAG) — "
                     "jamais du texte inventé : voir src/generation/prompt.py::CONSIGNE.",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Lance l'assistant RAG dans une interface web.")
    parser.add_argument(
        "--share", action="store_true",
        help="Crée un lien public temporaire (quelques heures) via le tunnel Gradio.",
    )
    args = parser.parse_args()

    demo = build_interface()
    demo.launch(share=args.share)


if __name__ == "__main__":
    main()
