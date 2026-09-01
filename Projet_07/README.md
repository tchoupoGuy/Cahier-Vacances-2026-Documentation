# Projet 07 — IA agentique : réécriture pro

Réécriture du notebook `Cahier-Vacances-2026/Projet_07/projet_07.ipynb` en petit projet d'agent structuré comme en entreprise. Pour l'explication pédagogique du domaine (méthode Feynman), voir [`FEYNMAN.md`](./FEYNMAN.md) ; pour les principes d'ingénierie qui font qu'un développeur est performant sur ce type de projet, voir [`PRINCIPES-INGENIERIE.md`](./PRINCIPES-INGENIERIE.md).

## Pourquoi cette architecture

C'est le projet le plus transversal du cahier : il réutilise le SQL du Projet 01 et les embeddings du Projet 04, et y ajoute une vraie boucle de décision. L'architecture reflète directement le schéma "agent = outils + cerveau" du notebook : un package `tools/` (un fichier par outil, chacun indépendant), un package `agent/` (le raisonnement : tarification, boucle de repli, réservation), et **deux interfaces indépendantes au-dessus du même `src/`** — Streamlit pour une démo rapide en Python pur, et une API FastAPI + un frontend React/TypeScript pour une vraie séparation front/back. Exactement la séparation que ferait une équipe produit construisant un vrai agent : la logique ne vit qu'à un seul endroit, les interfaces ne font qu'appeler.

```
Projet_07/
├── data/
│   ├── voyages.db                   # vols, activités, réservations (SQLite)
│   └── hotels/*.pdf                 # 135 brochures d'hôtels
├── src/
│   ├── data/
│   │   ├── database.py               # connexion + exécution de requêtes PARAMÉTRÉES
│   │   └── brochures.py               # lecture des PDF -> DataFrame (texte complet + résumé)
│   ├── embeddings/
│   │   └── encoder.py                 # le même modèle d'embeddings que le Projet 04
│   ├── tools/                          # les 3 outils de l'agent, un fichier chacun
│   │   ├── flights.py                   # SQL paramétré : vols disponibles
│   │   ├── activities.py                 # SQL paramétré : activités d'une ville
│   │   └── hotels.py                      # recherche sémantique dans les brochures
│   ├── agent/                            # le "cerveau" : la boucle de décision
│   │   ├── pricing.py                     # chiffrage d'un voyage, dates voisines
│   │   ├── planner.py                      # la boucle de repli + l'exploration des jours voisins
│   │   └── booking.py                       # réservation, avec garde-fou de confirmation
│   └── display.py                          # affichages console + proposition en texte
├── webapp/
│   └── app.py                               # interface Streamlit, branchée directement sur src/
├── api/                                      # interface HTTP : FastAPI branchée directement sur src/
│   ├── schemas.py                             # contrat Pydantic (miroir de frontend/src/types.ts)
│   ├── converters.py                           # pandas.Series / dict -> JSON-safe
│   └── main.py                                  # endpoints /api/destinations, /api/plan, /api/book
├── frontend/                                 # client React + TypeScript, parle à l'API en JSON typé
│   └── src/
│       ├── types.ts                            # miroir de api/schemas.py
│       ├── api.ts                               # client HTTP typé (fetch)
│       ├── App.tsx                              # formulaire -> résultat -> réservation
│       └── components/                          # SearchForm, TripResult, BookingPanel
├── tests/                                    # outils SQL, recherche sémantique (doublure), boucle de décision, garde-fou, API
├── main.py                                   # démo CLI de bout en bout
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_07
pip install -e ".[dev]"
python main.py                    # démo console : planifie un voyage, réserve
streamlit run webapp/app.py       # l'application web Streamlit (inchangée)
pytest                            # voir la note ci-dessous
```

**Note sur les tests.** Les outils SQL (`tools/flights.py`, `tools/activities.py`) et la réservation sont testés directement sur une COPIE de `data/voyages.db` (`tests/conftest.py` la recrée dans un dossier temporaire à chaque test, jamais sur le fichier réel). La recherche d'hôtels et la boucle de décision (`agent/planner.py`) sont testées avec un encodeur factice (`tests/fakes.py`, même principe qu'au Projet 04) sur des hôtels synthétiques dont les prix sont choisis pour déclencher précisément chaque repli — aucun accès réseau requis pour `pytest`. `tests/test_api.py` teste l'API FastAPI de bout en bout avec les mêmes doublures. Seuls `main.py` et `webapp/app.py` téléchargent le vrai modèle d'embeddings.

## L'application React + TypeScript

Deuxième interface, indépendante de Streamlit : une API FastAPI qui expose `src/` en JSON, et un frontend React/TypeScript (Vite) qui l'appelle. Aucune des deux ne duplique la logique de l'agent — elles ne font qu'appeler `plan_trip`/`book_trip` et reformater.

**Lancement rapide (les deux serveurs d'un coup) :**

```bash
run_dev.bat     # Windows : double-clic, ou depuis un terminal
./run_dev.sh    # macOS/Linux
```

Le script installe `npm install` la première fois si besoin, puis ouvre l'API et le frontend (`uv run` installe aussi les dépendances Python manquantes automatiquement, ex. `fastapi`). API sur http://localhost:8000 (doc interactive sur `/docs`), frontend sur http://localhost:5173.

**Ou manuellement, dans deux terminaux :**

```bash
# Terminal 1 : l'API
cd Projet_07
pip install -e ".[dev]"
uvicorn api.main:app --reload --port 8000

# Terminal 2 : le frontend
cd Projet_07/frontend
npm install
npm run dev              # http://localhost:5173
```

Architecture : `frontend/` (React + TypeScript, formulaire de recherche, résultat de voyage, journal de l'agent, réservation) appelle `api/` (FastAPI, 3 endpoints : `GET /api/destinations`, `POST /api/plan`, `POST /api/book`) qui appelle `src/` (le même agent, mot pour mot, que Streamlit et `main.py`). L'API est **sans état** : `/api/plan` renvoie le voyage complet au client, qui le renvoie tel quel à `/api/book` — pas de session serveur à synchroniser.

Deux détails qui comptent pour la suite :
- **`frontend/src/types.ts` est le miroir manuel de `api/schemas.py`.** Rien ne les garde synchronisés automatiquement (pas de génération de client OpenAPI ici, volontairement, pour rester lisible) : un champ ajouté d'un côté doit être ajouté de l'autre.
- **Chaque endpoint ouvre sa propre connexion SQLite** (`api/main.py::_connection`) plutôt que d'en partager une entre requêtes : `sqlite3.Connection` n'est pas fait pour être utilisé depuis plusieurs threads, et FastAPI exécute les endpoints synchrones dans un pool de threads.

## Comment lire ce code

- **`src/tools/` contient exactement les 3 outils du schéma du notebook**, chacun dans son fichier, chacun testable indépendamment. `flights.py` et `activities.py` n'utilisent que des requêtes SQL paramétrées (jamais de f-string avec une valeur insérée directement — voir `FEYNMAN.md` pour l'explication du risque d'injection SQL).
- **`src/tools/hotels.py` accepte un `encode_fn` injectable.** C'est ce qui permet de tester toute la mécanique de recherche sémantique (filtrer par ville, encoder, comparer, trier) avec une doublure déterministe, sans télécharger de modèle — le même principe d'injection de dépendance qu'au Projet 04.
- **`src/agent/planner.py` est la seule fonction qui orchestre les 3 outils ensemble.** `try_one_date` implémente la boucle de repli (sacrifier une activité payante, puis changer d'hôtel, puis abandonner) ; `plan_trip` l'enrichit en explorant aussi les jours voisins, sans jamais déplacer la date demandée automatiquement.
- **`src/agent/booking.py` isole le garde-fou dans une fonction de trois lignes.** Tant que `confirme=False`, rien n'est écrit en base : c'est la seule action irréversible de tout le projet, et elle est protégée en conséquence.
- **`webapp/app.py` importe directement `src/`**, contrairement au notebook d'origine qui régénérait un fichier `agent.py` à partir du code des cellules. Une seule source de vérité pour la logique de l'agent, que ce soit en CLI, en tests, dans l'application Streamlit ou dans l'API.
- **`api/` ne fait que trois choses : valider l'entrée (Pydantic), appeler `src/`, reformater la sortie (`api/converters.py`).** Aucun calcul métier n'y vit — si la logique de l'agent devait changer, seul `src/` bougerait, ni `api/` ni `frontend/`.
- **`frontend/src/App.tsx` reproduit le même flux que `main.py` et `webapp/app.py`** : composer un voyage (`POST /api/plan`), l'afficher avec le journal de l'agent, puis réserver en deux temps (`POST /api/book` avec `confirme=false` pour prévisualiser, `true` pour écrire) — le garde-fou de `booking.py` existe donc aussi côté interface, pas seulement côté serveur.

## Aller plus loin (idées d'évolution "pro")

- Brancher un LLM (Qwen du Projet 04, ou une API Claude/ChatGPT) pour transformer une phrase libre en la demande structurée à 6 clés que l'agent attend.
- Remplacer le `print` de debug de `try_one_date` par un vrai logger structuré (niveau DEBUG), pour ne pas polluer la sortie en production.
- Ajouter un quatrième repli (changer de destination) quand plus rien ne rentre dans le budget.
- Générer `frontend/src/types.ts` automatiquement depuis le schéma OpenAPI de FastAPI (`/openapi.json`), pour ne plus avoir à synchroniser les deux fichiers à la main.
