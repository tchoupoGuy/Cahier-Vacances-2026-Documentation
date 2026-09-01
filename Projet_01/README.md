# Projet 01 — SQL : réécriture pro

Réécriture du notebook `Cahier-Vacances-2026/Projet_01/projet_01.ipynb` en petit projet d'analyse SQL structuré comme en entreprise. Pour l'explication pédagogique (méthode Feynman), voir [`FEYNMAN.md`](./FEYNMAN.md).

## Pourquoi cette architecture

Un projet SQL "pro" sépare toujours trois choses qu'un notebook mélange dans des cellules : le **schéma** de la base (la structure), les **requêtes** (le SQL métier, versionné comme du code), et le **code applicatif** (ce qui orchestre tout). C'est le pattern qu'on retrouve dans des outils comme dbt ou dans n'importe quel repo d'analyste de données en entreprise : chaque requête vit dans son propre fichier `.sql`, ce qui permet de la relire, la tester et la réutiliser indépendamment du reste.

```
Projet_01/
├── sql/
│   ├── schema.sql                  # CREATE TABLE (structure de la base)
│   ├── seed.sql                    # INSERT (données de démonstration)
│   └── queries/
│       ├── basic/                  # requêtes simples, paramétrées
│       │   ├── flights_from_origin.sql
│       │   ├── cheap_flights.sql
│       │   └── passenger_search.sql
│       └── analytics/              # l'étude business complète
│           ├── booking_status_breakdown.sql
│           ├── revenue_by_destination.sql
│           ├── recurring_demand_destinations.sql
│           ├── passengers_on_flight.sql
│           ├── passengers_never_booked.sql
│           ├── above_average_price_flights.sql
│           └── loyal_passengers.sql
├── src/
│   ├── database.py                 # construit la connexion + applique schema.sql et seed.sql
│   ├── queries.py                  # charge et exécute les .sql, renvoie des DataFrames
│   └── report.py                   # orchestre l'étude business et génère le graphique
├── tests/
│   ├── test_database.py            # intégrité du schéma et des contraintes
│   └── test_queries.py             # une assertion par requête métier (reprend les asserts du notebook)
├── reports/figures/                # graphique généré (revenue_by_destination.png)
├── main.py                         # point d'entrée : construit, étudie, recommande
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_01
pip install -e ".[dev]"
python main.py          # lance l'étude complète et affiche la recommandation
pytest                  # vérifie schéma, contraintes et chaque requête
```

## Comment lire ce code

- **Les requêtes SQL ne sont jamais écrites en dur dans le Python.** `src/queries.py` ne fait que charger un fichier `.sql` et l'exécuter avec des paramètres nommés (`:origin`, `:max_price`...). Résultat : chaque requête est testable et relisible indépendamment, comme le ferait un analyste SQL qui ne veut pas fouiller du code Python pour retrouver une requête.
- **`database.py`** applique `schema.sql` puis `seed.sql` avec `executescript` : la structure et les données de départ sont des artefacts versionnés, pas des chaînes Python noyées dans des cellules de notebook.
- **`report.py`** est la seule couche "métier" : elle enchaîne les requêtes dans l'ordre du raisonnement business (statuts → revenus → demande récurrente → profil clientèle → clients à démarcher → positionnement prix → fidélité) et produit une recommandation, comme le faisait la partie 3 du notebook.
- **Les tests reprennent un à un les `assert` du notebook d'origine**, pour garantir que la réécriture produit exactement les mêmes résultats métier (13 vols au départ de Nice, New York JFK en tête du CA, etc.).

## Aller plus loin (idées d'évolution "pro")

- Remplacer SQLite par PostgreSQL via une variable d'environnement (`DATABASE_URL`), sans toucher aux fichiers `.sql`.
- Ajouter un `Makefile` ou une CLI (`typer`/`click`) pour exposer chaque requête analytique en commande.
- Générer le rapport en HTML/PDF avec les fonctions déjà présentes dans `report.py`.
