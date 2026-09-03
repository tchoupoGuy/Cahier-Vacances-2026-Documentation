"""Découpage par fenêtre glissante — alternative à `pdf_loader.load_pages` (découpage par page).

Le découpage par PAGE fonctionne bien quand chaque page traite déjà d'un seul
sujet, comme les rubriques du Belvédère (une page = une rubrique courte). Il
devient inadapté dès qu'une page mélange plusieurs sujets, ou qu'un document
n'a pas de découpage naturel en pages courtes (un long PDF de conditions
générales sur plusieurs pages continues, par exemple). La fenêtre glissante
prend le relais : un découpage par TAILLE plutôt que par structure, avec un
chevauchement pour ne jamais couper une information à cheval sur deux chunks.

Aucune des deux stratégies n'est strictement meilleure — voir la comparaison
dans FEYNMAN.md. `chunk_pages` produit les mêmes colonnes que
`pdf_loader.load_pages` (source, title, text) : le reste du pipeline
(`formatter.add_markdown_sections`, `VectorStore`) fonctionne à l'identique
avec l'une ou l'autre, sans aucune modification.
"""

from __future__ import annotations

import pandas as pd


def split_into_chunks(text: str, size: int = 500, overlap: int = 80) -> list[str]:
    """Découpe `text` en passages d'environ `size` caractères.

    Coupe de préférence en fin de phrase (au dernier ". " trouvé dans la
    moitié la plus proche de la limite), pour ne pas trancher une phrase en
    plein milieu. `overlap` caractères de la fin d'un chunk sont repris au
    début du suivant, pour qu'une information à cheval sur la coupure reste
    lisible dans au moins un chunk entier.
    """
    if size <= 0:
        raise ValueError("size doit être strictement positif")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap doit être positif et strictement inférieur à size")

    text = " ".join(text.split())  # normalise espaces/retours à la ligne du PDF
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = text.rfind(". ", start + size // 2, end)
            if cut != -1:
                end = cut + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def chunk_pages(pages: pd.DataFrame, size: int = 500, overlap: int = 80) -> pd.DataFrame:
    """Redécoupe un DataFrame de pages (colonnes source, title, text) en chunks glissants.

    Chaque page peut donner PLUSIEURS lignes en sortie (une par chunk), avec
    un titre suffixé (" · passage N") pour rester traçable jusqu'à la page
    d'origine. Colonnes de sortie identiques à `pdf_loader.load_pages`.
    """
    rows = []
    for row in pages.itertuples():
        for i, chunk in enumerate(split_into_chunks(row.text, size=size, overlap=overlap), start=1):
            rows.append({"source": row.source, "title": f"{row.title} · passage {i}", "text": chunk})
    return pd.DataFrame(rows, columns=["source", "title", "text"])
