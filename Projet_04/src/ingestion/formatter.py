"""Mise en forme Markdown de la documentation, pour la donner au LLM."""

from __future__ import annotations

import pandas as pd


def add_markdown_sections(pages: pd.DataFrame) -> pd.DataFrame:
    """Ajoute une colonne `section` : chaque rubrique devient un titre Markdown + son texte."""
    pages = pages.copy()
    pages["section"] = "## " + pages["title"] + "\n\n" + pages["text"]
    return pages


def full_context(pages: pd.DataFrame) -> str:
    """Concatène toutes les rubriques en un seul texte Markdown (approche « tout dans le prompt »)."""
    return "\n\n".join(pages["section"])
