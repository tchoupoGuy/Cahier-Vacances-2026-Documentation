# Projet 01 — SQL : interroger une base de réservations de vols

Source : `Cahier-Vacances-2026/Projet_01/projet_01.ipynb`

## 🎯 En une phrase

SQL, c'est poser des questions précises à des tableaux de données reliés entre eux, et obtenir la réponse en quelques millisecondes.

## 1. Explique-le à un enfant de 12 ans

Imagine trois classeurs sur un bureau : un classeur "passagers" (qui sont les gens), un classeur "vols" (quels avions partent où et quand), et un classeur "réservations" (qui a réservé quel vol). Chaque réservation ne recopie pas toutes les infos du passager et du vol, elle note juste leurs numéros de fiche ("passager n°12 a réservé le vol n°7"). Ça évite d'écrire 50 fois le nom et l'email de la même personne.

SQL, c'est la façon de demander des choses à ces classeurs sans les feuilleter à la main : "donne-moi tous les vols qui partent de Nice", "combien de personnes ont réservé le vol pour New York", "qui n'a jamais rien réservé". On écrit la question dans un format bien précis, et l'ordinateur fouille les classeurs à notre place, instantanément.

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **Base de données relationnelle** | Un ensemble de tableaux (tables) reliés entre eux par des identifiants | Plusieurs classeurs sur un même bureau, qui se renvoient les uns aux autres par des numéros de fiche |
| **Table** | Un tableau avec des colonnes fixes et une ligne par élément | Une feuille de classeur : une ligne = une personne, une colonne = une info sur cette personne |
| **Clé primaire (`PRIMARY KEY`)** | La colonne qui identifie chaque ligne de façon unique | Le numéro de sécu de chaque fiche : jamais deux fiches avec le même numéro |
| **Clé étrangère (`REFERENCES`)** | Une colonne qui pointe vers l'identifiant d'une autre table | Un post-it sur la fiche "réservation" qui dit "voir fiche passager n°12" |
| **Contrainte (`NOT NULL`, `UNIQUE`, `CHECK`)** | Une règle qui empêche d'enregistrer des données incohérentes | Le règlement du classeur : "on n'accepte pas de fiche sans nom", "pas deux fois le même email" |
| **`SELECT` / `WHERE`** | Choisir les colonnes à afficher / filtrer les lignes selon une condition | "Je veux voir seulement la colonne destination et le prix" / "seulement les vols au départ de Nice" |
| **`GROUP BY` + agrégation (`COUNT`, `SUM`, `AVG`)** | Regrouper des lignes qui partagent une valeur, puis calculer une statistique par groupe | Trier toutes les fiches par destination, puis compter combien il y en a dans chaque pile |
| **`JOIN`** | Recoller deux tables ensemble en suivant les clés étrangères | Agrafer la fiche réservation à la fiche passager correspondante, pour tout voir sur une seule feuille |
| **`INNER JOIN` vs `LEFT JOIN`** | `INNER` garde seulement les lignes qui ont une correspondance des deux côtés ; `LEFT` garde tout ce qu'il y a à gauche, même sans correspondance (avec des `NULL`) | `INNER` = seulement les gens qui ont une fiche des deux côtés du bureau ; `LEFT` = toute la pile de gauche, avec des cases vides pour ceux qui n'ont rien en face |
| **`HAVING`** | Un `WHERE`, mais appliqué après le `GROUP BY`, sur le résultat des groupes | On trie d'abord les fiches en piles (`GROUP BY`), et seulement après on écarte les piles trop petites (`HAVING`) |
| **Sous-requête** | Une requête SQL utilisée à l'intérieur d'une autre requête | Une poupée russe : on calcule d'abord une petite réponse (ex. le prix moyen), puis on l'utilise dans la grande question |

## 3. Comment ça marche, en détail

1. **On construit la base avant de l'interroger.** Le projet crée trois tables en mémoire (`passengers`, `flights`, `bookings`) avec `CREATE TABLE`, puis les remplit avec `INSERT INTO`. C'est la partie "architecture" : on décide des colonnes, de leurs types (`TEXT`, `INTEGER`, `REAL`) et des règles qu'elles doivent respecter.
2. **On isole les liens entre tables.** `bookings` est la table pivot : elle ne contient presque que des identifiants (`passenger_id`, `flight_id`) qui pointent vers les deux autres tables. C'est le principe même d'une base *relationnelle* : au lieu de tout dupliquer, on relie.
3. **On commence simple : `SELECT` + `WHERE` + `ORDER BY`.** Une seule table à la fois, un filtre, un tri. C'est 80 % des besoins du quotidien.
4. **On agrège : `GROUP BY` + `COUNT`/`SUM`/`AVG`.** Utile pour répondre à des questions du type "combien", "quel total", "quelle moyenne", par catégorie.
5. **On croise les tables : `JOIN`.** Dès qu'une question mélange des infos qui vivent dans deux tables différentes (ex. le prix du vol ET le statut de la réservation), il faut une jointure.
6. **On filtre après agrégation : `HAVING`.** Le piège classique est de vouloir mettre une condition sur `COUNT(*)` dans un `WHERE` — ça ne marche pas, car au moment du `WHERE` les groupes n'existent pas encore. `HAVING` s'applique après.
7. **On compare à une statistique globale : sous-requête.** Pour répondre à "quels vols sont plus chers que la moyenne", il faut d'abord calculer la moyenne (une sous-requête), puis comparer chaque ligne à ce résultat.
8. **On assemble tout dans une étude de cas.** Le projet enchaîne 7 étapes (statuts des réservations → chiffre d'affaires par destination → filtrage de la demande récurrente → profil clientèle → clients jamais démarchés → positionnement prix → clients fidèles) pour aboutir à une vraie recommandation business, comme le ferait un analyste de données.

## 4. Le code clé, annoté

```sql
-- Créer une table avec ses règles
CREATE TABLE passengers (
    id INTEGER PRIMARY KEY,      -- identifiant unique, la "clé" de la fiche
    first_name TEXT NOT NULL,    -- obligatoire
    last_name TEXT NOT NULL,     -- obligatoire
    email TEXT UNIQUE,           -- jamais deux fois le même
    nationality TEXT             -- optionnel
);
```

```sql
-- Chiffre d'affaires confirmé par destination (agrégation + jointure)
SELECT flights.destination,
       SUM(flights.price_eur) AS total_revenue,   -- on additionne les prix du groupe
       COUNT(*) AS nb_bookings                     -- on compte les lignes du groupe
FROM flights
JOIN bookings ON flights.id = bookings.flight_id    -- on recolle les deux tables
WHERE bookings.status = 'confirmed'                 -- filtre AVANT le regroupement
GROUP BY flights.destination
HAVING COUNT(*) > 1                                 -- filtre APRÈS le regroupement
ORDER BY total_revenue DESC;
```

```sql
-- Trouver les vols plus chers que la moyenne (sous-requête)
SELECT flight_number, destination, price_eur
FROM flights
WHERE price_eur > (SELECT AVG(price_eur) FROM flights);
```

```python
# Côté Python : transformer chaque requête en tableau lisible
def query(sql):
    return pd.read_sql_query(sql, connexion)
```

## 5. Les pièges et questions qui bloquent

- **`WHERE` vs `HAVING`** : si tu écris `WHERE COUNT(*) > 1`, SQL refuse. `COUNT(*)` n'existe qu'après le `GROUP BY`, donc la condition doit passer par `HAVING`.
- **`INNER JOIN` fait disparaître des lignes.** Un passager sans aucune réservation n'apparaîtra jamais dans un `INNER JOIN` entre `passengers` et `bookings`. Pour le retrouver (étape "clients jamais démarchés"), il faut un `LEFT JOIN` puis filtrer les `NULL` du côté droit.
- **Une clé primaire ne veut pas dire "obligatoire dans les deux sens".** `flight_id REFERENCES flights(id)` dit "cette valeur doit exister dans `flights`", mais ne garantit pas qu'un vol donné a au moins une réservation.
- **Une base "en mémoire" disparaît à chaque exécution.** Si tu relances les cellules de création de table dans le désordre, tu peux avoir une erreur "la table existe déjà" — il faut alors redémarrer le kernel.
- **Une grosse vente peut fausser un classement.** Trier par chiffre d'affaires total sans filtrer sur le nombre de réservations peut faire remonter une destination qui n'a eu qu'une seule très grosse commande, pas une vraie demande récurrente. D'où l'intérêt du `HAVING COUNT(*) > 1`.

## 6. Test de Feynman

Ferme le notebook et essaie de répondre sans regarder :

- Pourquoi dit-on que `bookings` est la table "pivot" du schéma ? Que se passerait-il si elle n'existait pas ?
- Explique avec tes mots la différence entre `INNER JOIN` et `LEFT JOIN`, avec un exemple qui n'est pas celui du notebook.
- Pourquoi `WHERE COUNT(*) > 1` ne fonctionne pas, et que faut-il écrire à la place ?
- Sans regarder le code, écris la structure générale d'une requête qui calcule une moyenne par catégorie en ne gardant que les catégories confirmées.
- Pourquoi utiliser une sous-requête plutôt que de calculer la moyenne "à la main" et de la recopier dans le `WHERE` ?

Si une réponse te résiste, c'est le signal pour retourner dans le notebook sur cette étape précise.

## 7. Pour aller plus loin

- Cours gratuit suggéré dans le projet : [W3Schools SQL](https://www.w3schools.com/sql/sql_intro.asp)
- Essayer les mêmes requêtes sur un vrai moteur d'entreprise (PostgreSQL, MySQL) pour voir que la syntaxe est quasi identique à SQLite.
- Ajouter une quatrième table (ex. `airports`) et pratiquer une jointure à trois tables.
