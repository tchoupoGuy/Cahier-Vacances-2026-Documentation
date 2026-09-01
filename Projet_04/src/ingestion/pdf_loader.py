"""Extraction du texte des PDF de documentation en un tableau de rubriques.

Une page = une rubrique. La première ligne de chaque page est son titre,
la dernière est un pied de page qu'on écarte.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pypdf import PdfReader


def list_pdfs(docs_dir: str | Path) -> list[Path]:
    return sorted(Path(docs_dir).glob("*.pdf"))


def load_pages(docs_dir: str | Path) -> pd.DataFrame:
    """Charge toutes les pages de tous les PDF d'un dossier en un DataFrame.

    Returns
    -------
    DataFrame avec les colonnes : source (nom du fichier), title (1re ligne
    de la page), text (le reste, sans la dernière ligne de pied de page).
    """
    rows = []
    for path in list_pdfs(docs_dir):
        reader = PdfReader(path)
        for page in reader.pages:
            lines = page.extract_text().split("\n")
            rows.append({
                "source": path.name,
                "title": lines[0],
                "text": "\n".join(lines[1:-1]),
            })
    return pd.DataFrame(rows)
