"""Lecture des brochures PDF d'hôtels : une ligne par hôtel, texte complet + résumé."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd

DEFAULT_BROCHURES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "hotels"

_ENTETE_RE = re.compile(r"^(.+?) - (\d) etoiles - a partir de (\d+) euros la nuit", re.M)
_NOTE_RE = re.compile(r"Note des voyageurs : ([\d.]+) sur 10 \((\d+) avis\)")
_PRESENTATION_RE = re.compile(r"Presentation (.*?) Equipements")
_AVIS_RE = re.compile(r"Avis des clients (.*?) [A-ZÀ-Ý][^ ]* .*Brochure du reseau")


def load_brochures(directory: str | Path = DEFAULT_BROCHURES_DIR) -> pd.DataFrame:
    """Lit chaque brochure PDF et renvoie une ligne par hôtel.

    Quelques informations (ville, étoiles, prix, note) sont écrites dans un
    format fixe à l'intérieur de chaque brochure : de simples expressions
    régulières les extraient. Tout le reste reste du texte brut, car c'est
    lui que le modèle d'embeddings lira.

    Returns
    -------
    DataFrame avec les colonnes : ville, hotel, etoiles, note, avis,
    prix_nuit, texte (le document complet) et resume (présentation + avis
    clients uniquement — voir le README pour pourquoi cette distinction compte).
    """
    rows = []
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".pdf"):
            continue
        rows.append(_parse_brochure(Path(directory) / filename))
    return pd.DataFrame(rows)


def _parse_brochure(path: Path) -> dict:
    from pypdf import PdfReader

    reader = PdfReader(path)
    texte = "\n".join((page.extract_text() or "") for page in reader.pages)

    entete = _ENTETE_RE.search(texte)
    note = _NOTE_RE.search(texte)
    plat = " ".join(texte.split())
    presentation = _PRESENTATION_RE.search(plat)
    avis_clients = _AVIS_RE.search(plat)

    return {
        "ville": entete.group(1).strip() if entete else "?",
        "hotel": texte.strip().splitlines()[0].strip(),
        "etoiles": int(entete.group(2)) if entete else 0,
        "note": float(note.group(1)) if note else float("nan"),
        "avis": int(note.group(2)) if note else 0,
        "prix_nuit": float(entete.group(3)) if entete else float("nan"),
        "texte": plat,
        # Le "résumé" ne garde que la présentation et les avis clients : c'est là que
        # s'exprime le caractère de l'hôtel ("calme", "en famille", "romantique"). La
        # liste d'équipements et le pied de page sont quasi identiques d'une brochure à
        # l'autre : les encoder ne ferait qu'ajouter du bruit et rapprocher artificiellement
        # tous les hôtels les uns des autres.
        "resume": " ".join(m.group(1) for m in (presentation, avis_clients) if m) or plat,
    }
