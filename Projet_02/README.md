# Projet 02 — Machine Learning : réécriture pro

Réécriture du notebook `Cahier-Vacances-2026/Projet_02/projet_02.ipynb` en petit projet ML structuré comme en entreprise. Pour l'explication pédagogique (méthode Feynman), voir [`FEYNMAN.md`](./FEYNMAN.md).

## Pourquoi cette architecture

Un projet de Machine Learning "pro" sépare les étapes du pipeline pour que chacune soit testable, remplaçable et réutilisable indépendamment : chargement des données, feature engineering, entraînement, évaluation, et enfin l'usage du modèle (ici, une simulation de tournoi). C'est le découpage qu'on retrouve dans un repo MLOps typique — jamais tout dans un seul script, encore moins dans un seul notebook.

```
Projet_02/
├── data/raw/results.csv            # jeu de données (copié depuis le projet d'origine)
├── src/
│   ├── data/
│   │   └── loader.py                # chargement, filtre "ère moderne", colonne outcome
│   ├── features/
│   │   ├── form.py                  # forme récente glissante (historique par équipe)
│   │   └── engineering.py           # encodage, features différentielles, cible home_win
│   ├── models/
│   │   ├── train.py                 # split, standardisation, RandomForestClassifier
│   │   └── predict.py               # prédiction d'un match A vs B
│   ├── evaluation/
│   │   └── metrics.py               # accuracy, matrice de confusion, feature importances
│   ├── simulation/
│   │   └── tournament.py            # simulation de tournoi à élimination directe
│   └── pipeline.py                  # orchestre tout le pipeline d'entraînement
├── models/                          # artefacts entraînés (random_forest.joblib, scaler.joblib)
├── reports/figures/                 # graphiques générés
├── tests/                           # un test par étape du pipeline (données, entraînement, prédiction)
├── main.py                          # entraîne, évalue, simule la Coupe du Monde 2030
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_02
pip install -e ".[dev]"
python main.py          # entraîne le modèle, l'évalue, simule le tournoi 2030
pytest                  # vérifie chaque étage du pipeline (données -> features -> modèle -> prédiction)
```

## Comment lire ce code

- **`src/data/loader.py`** ne fait qu'une chose : charger le CSV et le restreindre à l'ère moderne (1994–2026). Aucune notion de modèle ici.
- **`src/features/form.py`** isole la logique la plus subtile du projet (l'historique glissant par équipe, calculé match après match sans fuite d'information vers le futur) dans un module dédié, indépendant du reste.
- **`src/features/engineering.py`** transforme le DataFrame enrichi en table d'entraînement : cible binaire, encodage, features différentielles. C'est la frontière entre "données brutes" et "ce que voit le modèle".
- **`src/models/train.py`** applique la règle d'or du ML (`fit_transform` sur le train, `transform` seul sur le test) et entraîne la forêt aléatoire. Les artefacts (`model.joblib`, `scaler.joblib`) sont sauvegardés séparément du code, comme on le ferait avant un déploiement.
- **`src/models/predict.py`** réutilise exactement les mêmes transformations que l'entraînement pour prédire un match inédit — un piège classique en ML est d'avoir une logique de features différente entre entraînement et inférence, ce module l'évite en réutilisant `FEATURES` et le même `scaler`.
- **`src/pipeline.py`** est le seul endroit qui connaît l'ordre complet des étapes ; c'est lui qu'on appelle depuis `main.py` ou depuis les tests.
- **Les tests reprennent les `assert` du notebook d'origine** (accuracy > 60 %, Brésil dans le top 10, France bat la Grèce...) pour garantir que la réécriture est fonctionnellement identique.

## Aller plus loin (idées d'évolution "pro")

- Exposer `predict_match` derrière une API (FastAPI) pour un usage en dehors du terminal.
- Suivre les métriques d'entraînement avec un outil de tracking (MLflow, Weights & Biases).
- Ajouter une validation croisée temporelle plutôt qu'un split unique, plus rigoureuse pour des données chronologiques.
