"""Lecture des fiches PDF de la base de connaissance : une ligne par article."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_KB_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base"

_ID_RE = re.compile(r"^(KB-\d+)_")
_TITRE_RE = re.compile(r"KB-\d+\s+—\s+(.+?)\s+Catégorie\s*:\s*(.+?)\s+Résumé")
_RESUME_RE = re.compile(r"Résumé\s+(.+?)\s+Conditions et exceptions")
_FORMULATIONS_RE = re.compile(r"Formulations possibles des clients\s+(.+?)\s+Identifiant")


def load_knowledge_base(directory: str | Path = DEFAULT_KB_DIR) -> pd.DataFrame:
    """Lit chaque fiche PDF de la base de connaissance et renvoie une ligne par article.

    Les fiches sont rangées par catégorie dans des sous-dossiers
    (commandes/, comptes/, livraisons/, paiements/, retours/) : on les
    parcourt tous avec `*/*.pdf`.

    Returns
    -------
    DataFrame avec les colonnes : id, titre, categorie, resume,
    formulations_clients, texte (le document complet) et a_encoder.
    """
    rows = []
    for path in sorted(Path(directory).glob("*/*.pdf")):
        try:
            rows.append(_parse_fiche(path))
        except Exception:
            # Une fiche corrompue ou illisible ne doit pas empêcher de charger
            # les 18 autres : on la journalise et on continue, plutôt que de
            # planter tout l'agent pour un seul PDF défaillant.
            logger.exception("impossible de lire la fiche %s, elle sera absente de la recherche", path)
    if not rows:
        logger.warning("aucune fiche chargée depuis %s — la recherche sémantique ne trouvera jamais rien", directory)
    return pd.DataFrame(rows)


def _parse_fiche(path: Path) -> dict:
    from pypdf import PdfReader

    reader = PdfReader(path)
    texte = "\n".join((page.extract_text() or "") for page in reader.pages)
    plat = " ".join(texte.split())

    id_match = _ID_RE.match(path.name)
    titre = _TITRE_RE.search(plat)
    resume = _RESUME_RE.search(plat)
    formulations = _FORMULATIONS_RE.search(plat)

    if not resume or not formulations:
        # Pas une exception : la fiche reste utilisable (repli sur le texte
        # complet plus bas), mais une extraction manquante dégrade
        # silencieusement la qualité de la recherche si personne ne le sait.
        logger.warning(
            "%s : format inattendu (résumé %s, formulations %s) — repli sur le texte complet",
            path.name, "trouvé" if resume else "absent", "trouvées" if formulations else "absentes",
        )

    return {
        "id": id_match.group(1) if id_match else path.stem,
        "titre": titre.group(1).strip() if titre else path.stem,
        "categorie": titre.group(2).strip() if titre else path.parent.name,
        "resume": resume.group(1).strip() if resume else "",
        "formulations_clients": formulations.group(1).strip() if formulations else "",
        "texte": plat,
        # Comme pour les brochures d'hôtel du Projet 07 : on n'encode que ce qui
        # porte vraiment le sens (le résumé + les formulations réelles des
        # clients), jamais le pied de page (Identifiant / Catégorie / Dernière
        # mise à jour / Usage), quasi identique d'une fiche à l'autre et qui
        # rapprocherait artificiellement toutes les fiches entre elles.
        "a_encoder": " ".join(m.group(1).strip() for m in (resume, formulations) if m) or plat,
    }
