
# Projet 08 — Bilan : est-ce un vrai projet d'entreprise ?

Ce document répond à une question différente de `PRINCIPES-INGENIERIE.md` (Projet 07) : pas "quels principes suivre pour bien concevoir ce genre de système", mais "où en est CE projet précisément, aujourd'hui, par rapport à ce qu'une entreprise exigerait avant de le mettre en production ?". Méthode Feynman : explication simple, puis chaque point de bilan appuyé sur une preuve concrète du code — jamais une affirmation en l'air.

## En une phrase

Le cœur du système (l'agent, ses outils, ses garde-fous, ses tests) est déjà construit comme du code d'entreprise sérieux ; ce qui manque encore, ce n'est presque rien de la logique métier — c'est tout ce qui entoure le code pour qu'une équipe puisse le faire tourner, le surveiller et le faire évoluer en production sans toi à côté.

## Explique-le simplement

Imagine deux maisons. La première a des fondations impeccables, une charpente solide, une plomberie qui ne fuit jamais : c'est le cœur du Projet 08, `src/`. La seconde partie, c'est tout ce qui rend une maison habitable au quotidien : une porte qui ferme à clé (sécurité des accès), un détecteur de fumée (observabilité — savoir qu'un problème arrive avant qu'il ne soit trop tard), une adresse enregistrée à la mairie (documentation), un plan d'évacuation affiché (gestion d'erreurs). Une maison sans fondations est dangereuse à habiter. Une maison avec des fondations parfaites mais sans porte qui ferme, sans détecteur de fumée et sans adresse officielle n'est pas non plus une maison qu'une famille peut emménager dedans en confiance — c'est un chantier très avancé, pas encore un logement.

## Vocabulaire

| Terme | Définition simple | Analogie |
|---|---|---|
| **Observabilité** | La capacité de savoir ce qui se passe dans un système en production sans avoir à le deviner | Le tableau de bord d'une voiture, pas juste le moteur qui tourne |
| **Dette technique** | Un raccourci pris consciemment, à rembourser plus tard | Un emprunt : utile maintenant, mais avec des intérêts si on l'ignore trop longtemps |
| **Environnement isolé de test** | Une base de données dédiée aux tests, séparée de celle du développement | Une salle d'essai, pas la cuisine du restaurant en plein service |
| **Secret** | Une information (mot de passe, clé) qui ne doit jamais apparaître dans le code source suivi par git | La clé de la maison, jamais gravée sur la porte elle-même |
| **Pool de connexions** | Un nombre limité de connexions à la base, réutilisées entre plusieurs requêtes plutôt que recréées à chaque fois | Un pool de taxis partagés plutôt qu'une voiture neuve achetée pour chaque trajet |

## Ce qui est déjà au niveau "entreprise"

**L'architecture sépare vraiment les responsabilités.** `src/data/`, `src/embeddings/`, `src/tools/`, `src/agent/` : un développeur qui rejoint le projet sait où chercher avant même de lire une ligne de code. Ce n'est pas cosmétique — c'est ce qui a permis d'ajouter la boucle de l'agent sans toucher aux outils déjà écrits.

**Aucune requête SQL n'est construite par concaténation.** Les 4 outils utilisent tous des `%s` paramétrés (`SQL_HISTORIQUE`, `SQL_COMMANDE`, `SQL_ETAT_CONVERSATION`...). C'est une protection structurelle contre l'injection SQL, pas une question de vigilance au cas par cas.

**Aucun texte n'est inventé par un modèle.** `repondre_a_la_question` renvoie toujours le `resume` littéral d'une fiche de la base de connaissance, jamais une paraphrase générée. Pour un système qui parle à de vrais clients, c'est le choix le plus défendable qui soit : zéro risque d'hallucination, chaque réponse est traçable jusqu'à une fiche KB écrite et validée par un humain.

**Les actions qui comptent ont un garde-fou, pas une simple bonne intention.** `escalader_vers_un_humain` vérifie l'état réel de la conversation avant d'agir, et refuse d'escalader deux fois — vérifié par un vrai test (`test_guardrail_blocks_an_already_escalated_conversation`), pas juste affirmé dans un commentaire.

**Les tests touchent la vraie base, avec de vraies contraintes SQL, sans jamais l'abîmer.** Le pattern transaction + rollback (`tests/conftest.py`) veut dire que `CHECK (confidence_score BETWEEN 0 AND 1)`, les clés étrangères, les contraintes `UNIQUE` — tout ça est réellement testé, pas simulé en mémoire. Peu de projets d'apprentissage vont jusque-là.

**L'injection de dépendance rend tout testable sans réseau.** `encode_fn` permet de tester la recherche sémantique et toute la boucle de décision sans télécharger de modèle ni dépendre d'un service externe disponible au moment du test.

**Une erreur de données a été trouvée et corrigée avec preuve, pas ignorée.** Les totaux de commandes incohérents (`sql/seed.sql`) ont été recalculés et le test `test_finds_the_right_order` vérifie maintenant la valeur exacte (9996), pas une valeur approximative.

## Ce qui manque encore pour un vrai déploiement

**Aucune gestion d'erreur ni journalisation structurée.** Grep sur `src/` : zéro `try`/`except`, zéro `logging`. Si Postgres est injoignable ou que le téléchargement du modèle d'embeddings échoue, le script plante avec une trace Python brute — utilisable pour toi en train d'apprendre, inacceptable pour une équipe qui doit diagnostiquer un incident à 2h du matin sans relire le code source.
> **Corrigé.** `database.py`, `encoder.py` et `knowledge_base.py` journalisent puis relancent leurs erreurs (mot de passe jamais loggé) ; `agent/repondre_a_la_question.py` journalise chaque étape et traite un échec technique de la recherche comme une confiance nulle (escalade, pas de crash) ; `main.py` configure `logging` une seule fois et attrape les erreurs fatales au point d'entrée.

**Aucune documentation du projet.** `README.md` fait 0 octet. Ironie du sort dans un dossier entièrement construit autour de la pédagogie et de la documentation : quelqu'un qui clone ce dépôt aujourd'hui n'a aucune indication sur comment le lancer, sans avoir suivi cette conversation.
> **Corrigé.** Voir [`README.md`](./README.md).

**La recherche sémantique recalcule les embeddings de toute la base à chaque question.** `chercher_dans_la_base_de_connaissance` encode les 19 fiches à chaque appel (`encode_fn(encoder, knowledge_base["a_encoder"])`), alors que leur contenu ne change jamais entre deux questions. À l'échelle d'un vrai centre de support (des milliers de questions par jour), c'est un recalcul massivement inutile — les vecteurs des fiches devraient être calculés une fois, mis en cache, et seule la question du client encodée à chaque appel.
> **Corrigé.** `embeddings.encoder.encoder_la_base_de_connaissance` indexe la base UNE FOIS (colonne "vecteur") ; `main.py` l'appelle avant sa boucle sur les questions ; `chercher_dans_la_base_de_connaissance` n'encode plus que la question à chaque appel.

**Une connexion brute par exécution, pas de pool.** `connect()` ouvre une nouvelle connexion à chaque appel, sans limite ni réutilisation. Pour un script de démo, aucun souci. Pour un service qui traite plusieurs conversations en parallèle, c'est le genre de détail qui sature la base de données sous charge.

**Pas de pipeline d'intégration continue.** Les 13 tests n'existent que si quelqu'un pense à taper `uv run pytest`. Rien ne les déclenche automatiquement à chaque changement — donc rien n'empêche une régression silencieuse de passer inaperçue.

**Le schéma évolue par fichiers SQL bruts, sans historique de migration.** `scripts/01-schema.sql` fonctionne très bien pour initialiser un environnement figé, mais le jour où il faut ajouter une colonne à une base déjà en production avec de vraies données, il n'y a aucun mécanisme pour appliquer ce changement proprement (un outil comme Alembic ou Flyway existe précisément pour ce problème).

**Les tests partagent la base de développement plutôt qu'une base de test dédiée.** Le rollback protège les données, mais deux exécutions simultanées (toi en local + une CI, ou deux développeurs) sur les mêmes lignes de `seed.sql` (conversation 4, 5, 7...) pourraient se gêner l'une l'autre. Une vraie base de test isolée (recréée à chaque run) réglerait ça définitivement.

**Le mot de passe de la base est en clair dans `docker-compose.yml`**, un fichier a priori suivi par git (contrairement à `.env`, qui lui est bien ignoré). Acceptable pour un mot de passe de développement jetable ; à corriger avant tout environnement partagé, avec une substitution de variable d'environnement plutôt qu'une valeur en dur.

**Aucun contrôle d'accès sur les outils eux-mêmes.** N'importe quel code qui importe `escalader_vers_un_humain` ou `historique_client` peut les appeler avec n'importe quel `conversation_id`. Dans un vrai système, ces actions seraient tracées à une identité (quel agent, quel service a déclenché l'action) et soumises à des permissions.

**Le seuil de confiance (0.6) n'avait été validé "à la main" que sur une poignée de questions.**
> **Outillé.** `scripts/compare_embedding_models.py` construit maintenant une vraie vérité terrain à partir des "formulations possibles des clients" des 19 fiches (une info déjà présente dans les PDF, jamais exploitée comme jeu de test jusqu'ici) et mesure la précision top-1 réelle de la recherche sémantique, plus le score moyen des bonnes/mauvaises réponses — de quoi juger objectivement si 0.6 est un seuil bien calibré, plutôt qu'une valeur choisie à l'œil sur quelques essais. Ce même script sert aussi à comparer deux modèles d'embeddings (`DEFAULT_MODEL` avait été changé à la main entre MiniLM et mpnet-base, sans mesure, pour "voir si c'est mieux" — voir `src/embeddings/encoder.py`) : lequel retrouve la bonne fiche le plus souvent, et à quel coût en vitesse. **Chiffres pas encore produits** : le bac à sable utilisé pour cette session n'a pas d'accès réseau vers Hugging Face (les modèles ne peuvent pas être téléchargés) — à lancer sur une machine avec accès réseau (`uv run python scripts/compare_embedding_models.py`).

**Des données personnelles réalistes, sans réflexion sur leur protection.** `customers` stocke emails, téléphones, adresses en clair, sans chiffrement, sans politique de rétention. Même avec des données fictives, c'est l'occasion de se poser la question qu'une vraie entreprise doit se poser : qui a le droit de lire ça, combien de temps le garde-t-on, faut-il le chiffrer au repos ?

## Test de Feynman

- Pourquoi dit-on que ne jamais générer de texte libre côté client (toujours renvoyer le `resume` d'une fiche KB) est un choix d'architecture défendable, pas juste une limitation technique ?
- Pourquoi l'absence de `try`/`except` dans `src/` est-elle plus grave dans un service qui tourne en continu que dans un script que tu lances toi-même et regardes planter ?
- Explique, avec l'exemple de `chercher_dans_la_base_de_connaissance`, la différence entre "recalculer à chaque appel" et "mettre en cache" — et pourquoi ce n'est pas juste une question de vitesse mais aussi de coût à l'échelle.
- Pourquoi un mot de passe en dur dans `docker-compose.yml` est-il un problème différent d'un mot de passe en dur dans `database.py` (déjà corrigé plus tôt) ?
- Si tu devais choisir UN seul point à corriger avant de montrer ce projet à un recruteur technique, lequel, et pourquoi celui-là plutôt qu'un autre ?

## Pour aller plus loin (par ordre de priorité suggéré)

1. ~~Écrire le `README.md` (actuellement vide)~~ — fait, voir [`README.md`](./README.md).
2. ~~Ajouter `try`/`except` + un vrai logger (module `logging`) autour des points de défaillance réseau/base~~ — fait.
3. ~~Mettre en cache les embeddings de la base de connaissance (calculés une fois, réutilisés à chaque question)~~ — fait, voir `embeddings.encoder.encoder_la_base_de_connaissance`.
4. Une CI simple (GitHub Actions, par exemple) qui lance `docker-compose up`, applique le schéma, et fait tourner `pytest` à chaque push.
5. Séparer secrets de dev (`docker-compose.yml`) et vraie gestion de secrets, une fois qu'il y a un environnement partagé à protéger.
