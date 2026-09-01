"""Affichage joli d'un échange question/réponse (avec ses sources)."""

from __future__ import annotations

import pandas as pd


def print_chat(question: str, answer: str, sources: pd.DataFrame | None = None) -> None:
    print(f"Client   : {question}")
    if sources is not None:
        titles = ", ".join(f"{row.title} ({row.score:.2f})" for row in sources.itertuples())
        print(f"Sources  : {titles}")
    print(f"Assistant: {answer}")
    print("-" * 80)
