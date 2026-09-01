# Projet 06 — Séries temporelles : réécriture pro

Réécriture du notebook `Cahier-Vacances-2026/Projet_06/Projet_06.ipynb` en petit projet de prévision structuré comme en entreprise. Pour l'explication pédagogique (méthode Feynman), voir [`FEYNMAN.md`](./FEYNMAN.md).

## Pourquoi cette architecture

Un projet de séries temporelles "pro" sépare la mécanique statistique pure (autocorrélation, simulation) des modèles ajustés (MA, ARMA), de leur évaluation (MAE, AIC, résidus) et de leur usage final (prévision). Ce découpage permet, par exemple, de tester `autocorrelation()` sans jamais ajuster de modèle, ou d'ajouter un modèle SARIMA plus tard sans toucher à l'évaluation.

```
Projet_06/
├── data/ventes_glaces.csv          # 4 étés de ventes quotidiennes
├── src/
│   ├── data/
│   │   └── loader.py                # chargement + découpage train/test CHRONOLOGIQUE
│   ├── baseline/
│   │   └── naive.py                 # "toujours la moyenne" / "comme hier"
│   ├── models/
│   │   ├── autocorrelation.py       # autocorrelation() + simulate_ma() (la mécanique du MA)
│   │   └── arima_models.py          # fit_ma, fit_arma, prévision à 1 jour, prévision à N jours
│   ├── evaluation/
│   │   ├── metrics.py               # MAE, tableau de scores trié
│   │   └── diagnostics.py           # test de Ljung-Box sur les résidus
│   └── visualization/
│       └── plots.py                 # ventes, corrélogrammes, prévisions, semaine à venir
├── tests/                           # autocorrélation, baselines, chargement, pipeline complet
├── main.py                          # compare les modèles et prévoit les 7 prochains jours
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_06
pip install -e ".[dev]"
python main.py           # compare les modèles et affiche la prévision de la semaine
pytest                    # vérifie autocorrélation, baselines, et le pipeline complet (rapide, CPU)
```

## Comment lire ce code

- **`src/models/autocorrelation.py` ne dépend d'aucune librairie de modélisation.** `autocorrelation()` et `simulate_ma()` sont de pures fonctions numpy, testées indépendamment de tout modèle ajusté — c'est la mécanique qui justifie ensuite le choix d'un MA(q) plutôt qu'un autre ordre.
- **`src/data/loader.py` impose un découpage chronologique**, jamais aléatoire : `train_test_split_series` prend toujours les derniers jours comme test, exactement comme il faut le faire sur une série temporelle (on ne peut pas "prédire le passé à partir du futur").
- **`src/models/arima_models.py` encapsule la subtilité de la prévision à 1 jour.** `one_day_ahead_forecast` réutilise les coefficients appris sur le train (`.apply()`) mais avance la fenêtre d'observation jusqu'à la fin de la série : c'est ce qui permet de comparer un MA(3) et un ARMA(1,1) sur un pied d'égalité, jour après jour.
- **`src/evaluation/diagnostics.py` isole le test de Ljung-Box**, le vrai juge de qualité (au-delà de l'AIC) : des résidus qui ressemblent à du bruit pur signifient que le modèle n'a rien laissé sur la table.
- **`src/pipeline.py` est le seul endroit qui connaît l'enchaînement complet** (baselines -> MA -> ARMA -> comparaison -> diagnostics) ; `main.py` et les tests s'appuient dessus.

## Aller plus loin (idées d'évolution "pro")

- Ajouter la saisonnalité hebdomadaire avec un **SARIMA** (`seasonal_order=(P, D, Q, 7)`).
- Ajouter la température comme variable explicative externe (**SARIMAX**, argument `exog=`).
- Automatiser le choix de l'ordre (p, d, q) avec une recherche sur grille guidée par l'AIC.
