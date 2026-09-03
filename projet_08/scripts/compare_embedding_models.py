"""Compare deux modèles d'embeddings sur les VRAIES données du projet — précision et vitesse.

Contexte : `DEFAULT_MODEL` (src/embeddings/encoder.py) avait été changé
manuellement de MiniLM vers mpnet pour "voir si c'est mieux", sans mesure —
juste une ligne commentée à côté de l'autre. Ce script répond à la question
avec des chiffres plutôt qu'à l'instinct, sur les données réelles du projet :

- Vérité terrain : chaque fiche de la base de connaissance liste ses
  "formulations possibles des clients" — de VRAIES questions qu'un client
  poserait, écrites pour cette fiche précise. On les extrait et on vérifie,
  pour chacune, si la recherche sémantique retrouve la BONNE fiche en
  position 1 (`chercher_dans_la_base_de_connaissance`, le même outil que
  l'agent utilise réellement).
- Vitesse : temps de chargement du modèle, d'indexation des 19 fiches (une
  fois, voir `encoder_la_base_de_connaissance`), et de recherche par
  question (à chaque appel de l'agent).

Nécessite un accès réseau (téléchargement des modèles depuis Hugging Face
au premier lancement). Depuis la racine du projet :

    uv run python scripts/compare_embedding_models.py
"""

from __future__ import annotations

import time

import pandas as pd

from src.data.knowledge_base import load_knowledge_base
from src.embeddings.encoder import encoder_la_base_de_connaissance, load_encoder
from src.tools.chercher_dans_la_base_de_connaissance import chercher_dans_la_base_de_connaissance

# Le caractère qui sépare chaque formulation dans le texte extrait des PDF
# (un bug de rendu pypdf sur les puces Wingdings du document source — voir
# tests/test_compare_embedding_models.py pour la preuve sur un vrai extrait).
SEPARATEUR_FORMULATIONS = "\x7f"

MODELES = [
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
]

# src/agent/repondre_a_la_question.py::SEUIL_CONFIANCE_PAR_DEFAUT — dupliqué
# ici en constante plutôt qu'importé, pour ne pas faire dépendre ce script
# (qui ne touche jamais à la base Postgres) du module qui, lui, en a besoin.
SEUIL_CONFIANCE_ACTUEL = 0.6


def extraire_verite_terrain(kb: pd.DataFrame) -> list[tuple[str, str]]:
    """Reconstruit des paires (question, id_fiche_attendu) à partir des
    "formulations possibles des clients" de chaque fiche.

    Ce ne sont pas des questions inventées pour l'occasion : ce sont les
    questions que ces fiches ont explicitement été écrites pour couvrir
    (voir `data/knowledge_base/*/*.pdf`, section "Formulations possibles
    des clients").
    """
    paires = []
    for row in kb.itertuples():
        formulations = [f.strip() for f in row.formulations_clients.split(SEPARATEUR_FORMULATIONS) if f.strip()]
        paires.extend((question, row.id) for question in formulations)
    return paires


def evaluer_modele(model_name: str, kb: pd.DataFrame, verite_terrain: list[tuple[str, str]]) -> dict:
    print(f"\n=== {model_name} ===")

    debut = time.perf_counter()
    encodeur = load_encoder(model_name)
    temps_chargement = time.perf_counter() - debut

    debut = time.perf_counter()
    kb_indexee = encoder_la_base_de_connaissance(kb, encodeur)
    temps_indexation = time.perf_counter() - debut

    correctes = 0
    scores_corrects: list[float] = []
    scores_incorrects: list[float] = []

    debut = time.perf_counter()
    for question, id_attendu in verite_terrain:
        meilleure = chercher_dans_la_base_de_connaissance(kb_indexee, encodeur, question, k=1).iloc[0]
        if meilleure["id"] == id_attendu:
            correctes += 1
            scores_corrects.append(float(meilleure["score"]))
        else:
            scores_incorrects.append(float(meilleure["score"]))
    temps_recherche_total = time.perf_counter() - debut

    n = len(verite_terrain)
    return {
        "modele": model_name,
        "n_questions": n,
        "precision_top1": correctes / n,
        "temps_chargement_s": temps_chargement,
        "temps_indexation_ms": temps_indexation * 1000,
        "temps_recherche_moyen_ms": (temps_recherche_total / n) * 1000,
        "score_moyen_correct": sum(scores_corrects) / len(scores_corrects) if scores_corrects else None,
        "score_moyen_incorrect": sum(scores_incorrects) / len(scores_incorrects) if scores_incorrects else None,
        "bonnes_reponses_sous_le_seuil": sum(1 for s in scores_corrects if s < SEUIL_CONFIANCE_ACTUEL),
    }


def afficher_resultats(resultats: list[dict]) -> None:
    print("\n" + "=" * 88)
    print(f"{'Modèle':56s} {'Précision':>10s} {'Recherche':>12s} {'Chargement':>10s}")
    print("-" * 88)
    for r in resultats:
        print(
            f"{r['modele']:56s} {r['precision_top1']:>9.1%} "
            f"{r['temps_recherche_moyen_ms']:>9.1f} ms {r['temps_chargement_s']:>8.1f} s"
        )
    print("=" * 88)

    for r in resultats:
        print(f"\n{r['modele']}")
        print(f"  précision top-1         : {r['precision_top1']:.1%} "
              f"({round(r['precision_top1'] * r['n_questions'])}/{r['n_questions']})")
        print(f"  chargement du modèle    : {r['temps_chargement_s']:.1f} s")
        print(f"  indexation (19 fiches)  : {r['temps_indexation_ms']:.0f} ms")
        print(f"  recherche, par question : {r['temps_recherche_moyen_ms']:.1f} ms")
        if r["score_moyen_correct"] is not None:
            print(f"  score moyen (bonnes)    : {r['score_moyen_correct']:.3f}")
        if r["score_moyen_incorrect"] is not None:
            print(f"  score moyen (mauvaises) : {r['score_moyen_incorrect']:.3f}")
        if r["bonnes_reponses_sous_le_seuil"]:
            print(f"  ⚠️  {r['bonnes_reponses_sous_le_seuil']} bonne(s) réponse(s) auraient été escaladées "
                  f"à tort avec le seuil actuel ({SEUIL_CONFIANCE_ACTUEL}) !")

    print(f"\nPour changer le modèle par défaut : src/embeddings/encoder.py::DEFAULT_MODEL.")
    print(f"Le seuil de confiance ({SEUIL_CONFIANCE_ACTUEL}, src/agent/repondre_a_la_question.py) "
          "a été calibré pour le modèle actuellement en place dans DEFAULT_MODEL — à revérifier "
          "si vous en changez (voir la colonne 'score moyen' ci-dessus).")


def main() -> None:
    kb = load_knowledge_base()
    verite_terrain = extraire_verite_terrain(kb)
    print(f"{len(kb)} fiches chargées, {len(verite_terrain)} questions de vérité terrain extraites.")

    resultats = [evaluer_modele(nom, kb, verite_terrain) for nom in MODELES]
    afficher_resultats(resultats)


if __name__ == "__main__":
    main()
