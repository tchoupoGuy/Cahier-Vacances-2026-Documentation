# Cahier de Vacances 2026 — Documentation & réécriture pro

Ce dossier est le pendant "documentation + ingénierie" de [`Cahier-Vacances-2026`](../Cahier-Vacances-2026), le dépôt de notebooks du cahier de vacances Machine Learnia. Pour chaque projet du cahier, il contient deux choses :

1. **Une fiche pédagogique `FEYNMAN.md`**, construite avec la méthode Feynman : expliquer simplement, repérer les trous de compréhension, simplifier encore. Voir [`METHODE-FEYNMAN.md`](./METHODE-FEYNMAN.md).
2. **Une réécriture `README.md` + `src/` en architecture professionnelle** : le code du notebook, réorganisé en petit projet Python structuré comme il le serait en entreprise — chaque architecture est adaptée au style du projet (requêtes SQL versionnées pour le Projet 01, pipeline MLOps pour le Projet 02, injection de dépendance testable pour le RAG du Projet 04, etc.).

## Structure

```
Cahier-Vacances-2026-Documentation/
├── METHODE-FEYNMAN.md              # la méthode Feynman, expliquée et appliquée à ce dossier
├── README.md                       # ce fichier
└── Projet_XX/
    ├── README.md                    # architecture pro : structure, installation, comment lire le code
    ├── FEYNMAN.md                    # fiche pédagogique (méthode Feynman)
    ├── src/                          # code réorganisé en modules (le détail varie par projet)
    ├── tests/                        # tests qui rejouent les assertions du notebook d'origine
    ├── data/                         # données nécessaires au projet (copiées, autonomes)
    ├── main.py                       # point d'entrée exécutable
    └── pyproject.toml                # dépendances du projet
```

## Index des projets

| # | Projet | Sujet | Architecture pro |
|---|---|---|---|
| 01 | [SQL : réservations de vols](./Projet_01/README.md) ([Feynman](./Projet_01/FEYNMAN.md)) | Bases relationnelles, requêtes, jointures | `sql/` (schéma + requêtes versionnées) + `src/` (exécution, rapport) |
| 02 | [ML : qui gagnera la Coupe du Monde 2026 ?](./Projet_02/README.md) ([Feynman](./Projet_02/FEYNMAN.md)) | Apprentissage supervisé, classification | pipeline `data -> features -> models -> evaluation -> simulation` |
| 03 | [Clustering : dessiner le Tour de France 2027](./Projet_03/README.md) ([Feynman](./Projet_03/FEYNMAN.md)) | Non supervisé, optimisation (TSP) | `clustering/` + `routing/` (heuristiques) + `visualization/` séparés |
| 04 | [RAG & LLM : assistant virtuel d'hôtel](./Projet_04/README.md) ([Feynman](./Projet_04/FEYNMAN.md)) | LLM, retrieval, embeddings | `ingestion -> embeddings -> retrieval -> generation`, testable hors-ligne |
| 05 | [Deep Learning & Vision : poissons de l'aquarium](./Projet_05/README.md) ([Feynman](./Projet_05/FEYNMAN.md)) | Détection d'objets, fine-tuning | `data -> models -> training -> inference -> evaluation` |
| 06 | [Séries temporelles : les glaces de Bruno](./Projet_06/README.md) ([Feynman](./Projet_06/FEYNMAN.md)) | Prévision, autocorrélation | `baseline -> models -> evaluation -> visualization` |
| 07 | [IA agentique : un agent qui planifie tes vacances](./Projet_07/README.md) ([Feynman](./Projet_07/FEYNMAN.md), [Principes d'ingénierie](./Projet_07/PRINCIPES-INGENIERIE.md)) | Agents, SQL + embeddings combinés, boucle de décision | `tools/` (SQL + recherche sémantique) + `agent/` (boucle de repli, réservation) + `webapp/` (Streamlit) + `api/` + `frontend/` (React/TypeScript) |

Chaque `Projet_XX/README.md` a été vérifié : le code s'exécute (`python main.py`) et les tests passent (`pytest`), avec des résultats numériques cohérents avec le notebook d'origine.

## Aller plus loin : s'entraîner sur des projets originaux

[`PROJETS-ENTRAINEMENT.md`](./PROJETS-ENTRAINEMENT.md) propose 6 projets d'agents "style entreprise" (support client, stock, notes de frais, DevOps, RH, logistique), sans notebook source cette fois : à toi de les spécifier en détail et de les coder, en réutilisant les briques des projets 01-07 (SQL, embeddings, séries temporelles, TSP) et les principes de [`Projet_07/PRINCIPES-INGENIERIE.md`](./Projet_07/PRINCIPES-INGENIERIE.md).

## Comment travailler avec ce dossier

**Pour apprendre (méthode Feynman) :**
1. Termine un projet du cahier de vacances (le notebook, les exercices, les asserts qui passent).
2. Ouvre `Projet_XX/FEYNMAN.md`, commence par la section **Test de Feynman** sans regarder le reste.
3. Retourne dans les sections précédentes pour combler les trous révélés par le test.

**Pour voir à quoi ressemble une version "pro" du même projet :**
1. Ouvre `Projet_XX/README.md` : il explique pourquoi cette architecture précise a été choisie pour ce projet.
2. Installe (`pip install -e ".[dev]"`) et lance (`python main.py`, puis `pytest`) pour voir le code tourner.
3. Compare avec le notebook d'origine : même logique, mais découpée en modules testables et réutilisables.
