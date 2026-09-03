# Projet 08 — Agent de support client

Premier projet de la feuille de route d'entraînement ([`../PROJETS-ENTRAINEMENT.md`](../PROJETS-ENTRAINEMENT.md), projet 1). Contrairement aux Projets 01 à 07, il n'y a pas de notebook source à réécrire : c'est un projet original, conçu et codé pour s'entraîner sur l'approche "outils d'abord, puis la boucle" décrite dans [`../Projet_07/PRINCIPES-INGENIERIE.md`](../Projet_07/PRINCIPES-INGENIERIE.md).

Un bilan honnête de ce qui est déjà au niveau entreprise et de ce qui manque encore se trouve dans [`BILAN-ENTREPRISE.md`](./BILAN-ENTREPRISE.md).

## Pourquoi cette architecture

Un centre de support reçoit des questions en langage libre. Certaines ont une réponse déjà écrite dans une base de connaissance ; d'autres nécessitent un humain. L'agent n'est pas un LLM qui invente une réponse : il cherche dans des sources connues (une base SQL pour les faits structurés, des fiches PDF pour les procédures), évalue sa propre confiance, et escalade plutôt que de deviner. Même schéma que le Projet 07 : un package `tools/` (un outil, un fichier, une seule responsabilité), un package `agent/` (le raisonnement — ici une seule fonction, la boucle de décision), et deux points d'entrée qui appellent la même logique (`main.py` en démo CLI, `tests/` en vérification automatisée).

```
Projet_08/
├── data/
│   └── knowledge_base/            # 19 fiches PDF, 5 catégories (commandes, comptes, livraisons, paiements, retours)
├── scripts/
│   ├── 01-schema.sql               # schéma PostgreSQL (auto-appliqué au premier démarrage du conteneur)
│   ├── 02-seed.sql                  # données de démonstration (15 clients, 18 commandes, 8 conversations...)
│   └── compare_embedding_models.py   # précision + vitesse de deux modèles d'embeddings, sur les vraies fiches
├── src/
│   ├── data/
│   │   ├── database.py               # connexion (DATABASE_URL) + exécution de requêtes PARAMÉTRÉES
│   │   └── knowledge_base.py          # lecture des PDF -> DataFrame (résumé + formulations clients)
│   ├── embeddings/
│   │   └── encoder.py                  # le modèle + encoder_la_base_de_connaissance (indexation, une fois)
│   ├── tools/                           # les outils de l'agent, un fichier chacun
│   │   ├── historique_client.py          # SQL paramétré : commandes d'un client
│   │   ├── commande_par_numero.py         # SQL paramétré : une commande par son order_number
│   │   ├── chercher_dans_la_base_de_connaissance.py  # recherche sémantique dans les fiches KB
│   │   └── escalader_vers_un_humain.py     # transfert à un agent humain, avec garde-fou anti-doublon
│   └── agent/
│       └── repondre_a_la_question.py        # la boucle : chercher, évaluer, reformuler une fois, escalader
├── tests/                                     # transaction + rollback : teste la vraie base sans jamais l'abîmer
├── docker-compose.yml                         # PostgreSQL 17, auto-init via scripts/
├── main.py                                    # démo CLI de bout en bout
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_08
cp .env.example .env               # vérifier que le port correspond à docker-compose.yml (5433 par défaut)
docker-compose up -d                # PostgreSQL, avec schema + seed auto-appliqués au premier démarrage
uv sync --extra dev
uv run python main.py               # démo console : 4 questions, réponses ou escalades
uv run pytest -v                    # tests, contre la vraie base (voir la note ci-dessous)
uv run python scripts/compare_embedding_models.py   # précision + vitesse, MiniLM vs mpnet (réseau requis)
```

**Si le conteneur existait déjà avant l'ajout de `scripts/`** (volume `postgres_data` non vide), l'auto-init ne se relance pas. Applique alors le schéma et les données à la main :

```bash
Get-Content scripts\01-schema.sql | docker exec -i support-client-db psql -U support_user -d support_client
Get-Content scripts\02-seed.sql   | docker exec -i support-client-db psql -U support_user -d support_client
```

**Note sur les tests.** Contrairement aux projets SQLite du cahier (copier le fichier `.db` dans un dossier temporaire), on ne peut pas "copier" une base PostgreSQL aussi simplement. Le pattern ici est transaction + rollback : `tests/conftest.py` ouvre une connexion, et l'annule (`rollback()`) à la fin de chaque test — ce qui exige que le code testé ne fasse jamais `conn.commit()` lui-même (voir la note dans `escalader_vers_un_humain.py` et `repondre_a_la_question.py` : c'est à l'appelant, `main.py` en production, de committer). Les tests tournent donc directement sur les vraies lignes de `scripts/02-seed.sql` (un vrai client, une vraie conversation), sans jamais les modifier durablement. Seule `chercher_dans_la_base_de_connaissance` est testée avec une base synthétique (voir `tests/test_chercher_dans_la_base_de_connaissance.py`) : un texte réel peut créer des collisions de mots-clés fragiles, sans rapport avec la mécanique de recherche elle-même.

## Comment lire ce code

- **`src/tools/` contient un outil par fichier, chacun testable indépendamment.** `historique_client.py` et `commande_par_numero.py` n'utilisent que des requêtes SQL paramétrées (`%s`, jamais de f-string avec une valeur insérée directement).
- **`chercher_dans_la_base_de_connaissance.py` accepte un `encode_fn` injectable**, comme `find_hotels` au Projet 07 — c'est ce qui permet de tester toute la recherche sémantique sans télécharger de modèle.
- **La base de connaissance est indexée UNE FOIS (`encoder_la_base_de_connaissance`), jamais à chaque question.** `main.py` l'appelle juste après `load_encoder()`, avant sa boucle : `chercher_dans_la_base_de_connaissance` n'encode plus que la question à chaque appel, pas les 19 fiches.
- **`escalader_vers_un_humain.py` isole le garde-fou anti-doublon dans une vérification d'état explicite** : une conversation déjà `'escalated'` ou `'closed'` n'est jamais escaladée une seconde fois.
- **`agent/repondre_a_la_question.py` est la seule fonction qui orchestre tous les outils ensemble.** Elle cherche, compare le score du meilleur résultat à un seuil de confiance, reformule UNE fois si besoin (retire les formules de politesse), répond si le score passe, escalade sinon — jamais de réponse envoyée avec une confiance trop basse, même si le résultat semble plausible.
- **Aucun LLM ne génère de texte libre.** La réponse envoyée est toujours le `resume` littéral d'une fiche de la base de connaissance : traçable, sans risque d'hallucination — un choix d'architecture assumé, pas une limitation.

## Aller plus loin

Voir [`BILAN-ENTREPRISE.md`](./BILAN-ENTREPRISE.md) pour la liste complète, argumentée point par point. Déjà fait : documentation, gestion d'erreurs/journalisation, mise en cache des embeddings. Restent, dans l'ordre suggéré : une CI qui lance les tests automatiquement, et une vraie gestion des secrets avant tout environnement partagé.
