# Projet 07 — Principes d'ingénierie pour construire ce type de projet en entreprise

Ce document répond à une question différente de `FEYNMAN.md` : pas "comment fonctionne cet agent ?", mais "quelles sont les approches et les principes qui font qu'un développeur est performant pour concevoir CE GENRE de système (agent + SQL + embeddings + boucle de décision + API + frontend) en entreprise ?". Même méthode Feynman, appliquée cette fois à la posture d'ingénierie plutôt qu'au domaine métier.

## En une phrase

Un projet pro n'est pas meilleur parce qu'il a plus de fichiers — il est meilleur parce que chaque décision de conception peut être justifiée, testée isolément, et changée sans casser le reste. C'est la différence entre un notebook qui "marche une fois" et un système qu'une équipe peut faire évoluer pendant des années.

## 1. Explique-le à un enfant de 12 ans

Imagine une cuisine de restaurant. Le commis qui coupe les légumes ne fait pas aussi la caisse, et le chef ne va pas courir chercher les produits au marché en plein coup de feu. Chacun a un poste précis, et surtout : la recette du plat n'existe qu'à un seul endroit (le carnet du chef), jamais recopiée à moitié dans la tête de chaque commis — sinon le jour où la recette change, quelqu'un continue de faire l'ancienne version sans le savoir.

Un projet d'ingénierie pro, c'est pareil. Chaque "poste" (accès aux données, raisonnement de l'agent, interface utilisateur) a un rôle précis et ne fait que ça. Et la logique importante n'est écrite qu'à un seul endroit : dans le Projet 07, `webapp/app.py` (Streamlit) et `api/main.py` (FastAPI) appellent tous les deux exactement les mêmes fonctions de `src/`. Si la logique de repli budgétaire change demain, elle change à un seul endroit — pas dans trois fichiers qu'on espère avoir tous retrouvés.

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **Séparation des responsabilités** | Chaque module fait une seule chose, et une seule couche connaît chaque autre couche | Le commis coupe, le chef cuisine, le serveur sert — personne ne fait le travail des autres |
| **Source unique de vérité** | La logique métier n'existe qu'à un seul endroit, jamais recopiée | Le carnet de recettes du chef, jamais retapé de mémoire dans chaque tête |
| **Injection de dépendance** | Une fonction reçoit ses outils en paramètre plutôt que de les fabriquer elle-même | Un cuisinier qui s'entraîne sur un four factice, toujours identique, plutôt que sur le vrai four à gaz qui varie selon la météo |
| **Garde-fou (guardrail)** | Une vérification qui bloque une action irréversible sans confirmation explicite | Le bouton "êtes-vous sûr ?" avant de valider un paiement, qu'aucun raccourci ne doit pouvoir éviter |
| **Explicabilité (explainability)** | La capacité d'un système à dire *pourquoi* il a pris telle décision | Le carnet de bord de l'organisateur, qui justifie chaque sacrifice a posteriori |
| **Contrat d'interface** | Une définition explicite et partagée de la forme des données échangées entre deux systèmes | Un formulaire administratif : les deux parties savent exactement quelles cases remplir |
| **Sans état (stateless)** | Le serveur ne se souvient de rien entre deux requêtes ; chaque appel contient tout ce qu'il faut | Un guichet où l'on redonne son dossier complet à chaque visite, plutôt que de dire "comme la dernière fois" |
| **Déterministe vs probabiliste** | Un code qui donne toujours le même résultat pour les mêmes entrées, vs un modèle dont la réponse dépend d'un apprentissage statistique | Une calculatrice (déterministe) vs un sommelier qui devine un accord mets-vin (probabiliste) |

## 3. Comment ça marche, en détail

1. **La séparation des responsabilités doit être visible dans l'arborescence, pas seulement dans la tête du développeur.** `tools/` (les outils, chacun indépendant), `agent/` (le raisonnement), `data/`+`embeddings/` (l'accès aux sources) : en ouvrant le dossier, n'importe quel nouveau développeur comprend où chercher avant même de lire une ligne de code. C'est un gain de vitesse d'onboarding mesurable, pas un détail esthétique.

2. **Une seule source de vérité rend le changement sûr.** Deux interfaces (Streamlit et React) appellent le même `src/`. Sans cette discipline, corriger un bug dans la boucle de repli obligerait à se souvenir de tous les endroits où cette logique a été recopiée — et l'expérience montre qu'on en oublie toujours un.

3. **L'injection de dépendance rend l'intelligence artificielle testable.** `find_hotels(..., encode_fn=default_encode)` accepte un encodeur de remplacement (`tests/fakes.py::FakeEncoder`). Sans ce principe, chaque test dépendrait d'un vrai modèle Hugging Face — lent, parfois payant, et ici littéralement bloqué par le pare-feu du sandbox. En entreprise, un pipeline CI qui appelle un vrai LLM à chaque test est un pipeline qui finit désactivé ou qui explose le budget API. La règle générale : tout ce qui est lent, coûteux, non déterministe ou dépendant du réseau doit pouvoir être remplacé par une doublure au moment du test.

4. **Découpler la logique métier déterministe du composant probabiliste, dans la stratégie de test.** La boucle de décision de `agent/planner.py` (sacrifier, comparer, réessayer) est un algorithme classique : on peut calculer à la main le résultat exact attendu et l'écrire en assertion (voir `tests/test_planner.py`, où chaque scénario a été vérifié chiffre par chiffre avant d'écrire le test). La recherche d'hôtel, elle, s'appuie sur un modèle — on ne teste pas "le modèle a-t-il raison ?" mais "le code utilise-t-il correctement ce que le modèle renvoie ?". Confondre les deux mène soit à des tests fragiles (qui échouent quand le modèle change légèrement), soit à une logique métier jamais vraiment testée.

5. **Les garde-fous sur les actions irréversibles doivent exister à chaque couche qui pourrait les contourner.** `book_trip(..., confirme=False)` protège la base de données ; `BookingPanel.tsx` (deux clics côté React) protège l'interface. Un agent de plus en plus autonome ne doit jamais pouvoir enchaîner "décider" et "agir sur le monde réel" sans un point de passage explicite qu'aucun raccourci ne peut éviter.

6. **L'explicabilité n'est pas un luxe, c'est un outil de confiance et de débogage.** Le `journal` que produit l'agent (pourquoi il a retiré telle activité, pourquoi il propose tel autre jour) n'est pas du texte décoratif : c'est ce qui permet à un humain de comprendre — et de corriger — une décision automatisée. Un agent qui échoue silencieusement est un agent qu'on ne peut ni déboguer ni déployer en confiance à grande échelle.

7. **Un contrat d'interface explicite évite les ruptures silencieuses entre équipes.** `api/schemas.py` (Pydantic) et `frontend/src/types.ts` sont des miroirs manuels l'un de l'autre, documentés comme tels dans les deux fichiers. Le piège classique : un champ ajouté côté backend qui casse le frontend sans qu'aucune erreur ne le signale avant l'exécution. La solution la plus mature (voir section 7) est de générer un des deux automatiquement à partir de l'autre.

8. **Le sans-état côté serveur est un réflexe d'architecture, même sur un petit projet.** `/api/plan` renvoie le voyage complet, que le client renvoie tel quel à `/api/book` — aucune session à synchroniser entre deux requêtes. C'est ce qui permettrait de faire tourner plusieurs instances de l'API derrière un load balancer sans qu'elles se marchent dessus, le jour où le projet doit monter en charge.

9. **La sécurité doit être structurelle, jamais une question de vigilance personnelle.** `WHERE destination = ?` plutôt qu'un f-string : ce n'est pas "faire attention à chaque requête", c'est rendre la faille impossible par construction. Un développeur pro ne compte pas sur sa propre discipline pour éviter les injections SQL — il choisit une API qui ne laisse pas la faille exister.

## 4. Le code clé, annoté

```python
# Injection de dépendance : l'encodeur (et sa fonction d'appel) sont des PARAMÈTRES,
# jamais fabriqués à l'intérieur de la fonction. Un test peut donc passer un faux
# encodeur déterministe sans toucher au code de production.
def find_hotels(brochures, encoder, ville, envie, k=3, encode_fn=default_encode):
    ...
```

```python
# Garde-fou : la seule ligne qui écrit dans la base est protégée par une
# condition explicite, jamais implicite dans un enchaînement de fonctions.
if not confirme:
    return "Rien n'a été réservé. ... Il faut confirmer pour que la réservation soit enregistrée."
conn.execute(sql, (...))
conn.commit()
```

```python
# Requête paramétrée : la sécurité est structurelle (le driver sqlite3 échappe
# lui-même la valeur), pas une question de vigilance au moment d'écrire le SQL.
SQL_VOLS = "SELECT ... FROM vols WHERE destination = ? AND date_depart = ?"
query(conn, SQL_VOLS, (destination, date_depart))
```

```typescript
// Contrat d'interface : ce type est un miroir MANUEL de api/schemas.py::TripOut.
// Un champ ajouté d'un côté sans l'autre casse le typage silencieusement —
// documenté comme tel dans les deux fichiers pour qu'on y pense au bon moment.
export interface TripOut {
  destination: string;
  vol: FlightOut;
  hotel: HotelOut;
  activites: ActivityOut[];
  prix_total: number;
  budget_max: number;
}
```

## 5. Les pièges et questions qui bloquent

- **Dupliquer un bout de logique "parce que c'est plus rapide sur le moment".** Recopier trois lignes de calcul de prix dans le frontend plutôt que d'appeler l'API semble gagner du temps — jusqu'au jour où la règle de calcul change et qu'un seul des deux endroits est corrigé.
- **Tester un modèle probabiliste comme s'il était déterministe.** Écrire `assert hotel_recommande == "Hotel Familia"` contre le vrai modèle d'embeddings est un test fragile : il peut échouer après une mise à jour du modèle sans qu'aucun bug n'ait été introduit. Tester la mécanique (filtrer, encoder, comparer, trier) avec une doublure déterministe est plus solide.
- **Un garde-fou posé à un seul endroit.** Protéger la réservation côté serveur mais pas côté interface (ou l'inverse) laisse un chemin de contournement — par un appel direct à l'API, ou par un bug d'interface qui saute l'étape de confirmation.
- **Un contrat d'interface implicite.** Se fier à "on sait ce que l'API renvoie" sans le documenter explicitement fonctionne à deux personnes sur un petit projet, et casse silencieusement dès qu'une troisième personne rejoint l'équipe ou que six mois passent.
- **Confondre "ça marche chez moi" et "c'est testé".** Un `main.py` qui s'exécute sans erreur ne garantit pas que chaque cas limite (budget impossible, ville inconnue, aucune activité) est géré correctement — seuls des tests écrits à partir de scénarios calculés à la main (comme dans `tests/test_planner.py`) le garantissent.

## 6. Test de Feynman

- Pourquoi un `encode_fn` injectable rend-il un pipeline qui dépend d'un modèle d'IA testable en intégration continue sans budget API ni accès réseau ?
- Pourquoi le garde-fou de réservation doit-il exister à la fois côté serveur (`src/agent/booking.py`) et côté interface (`BookingPanel.tsx`), et pas seulement à l'un des deux ?
- Pourquoi teste-t-on la boucle de décision (`try_one_date`) avec des chiffres calculés à la main plutôt qu'en vérifiant juste "ça ne plante pas" ?
- Qu'est-ce qui casse, concrètement, si `api/schemas.py` change sans que `frontend/src/types.ts` soit mis à jour en même temps ?
- Pourquoi une API sans état (`/api/plan` puis `/api/book` avec le voyage complet renvoyé par le client) est-elle plus facile à faire monter en charge qu'une API qui garderait le voyage en mémoire côté serveur ?
- Donne un exemple concret où recopier une logique dans deux endroits (plutôt que d'appeler une fonction commune) a fini par créer un bug en production.

## 7. Pour aller plus loin

- Génération automatique de `frontend/src/types.ts` depuis le schéma OpenAPI de FastAPI (`/openapi.json`), pour supprimer le risque de désynchronisation manuelle du contrat d'interface.
- Tests de contrat (contract testing, ex. Pact) entre l'API et le frontend, pour détecter une rupture de compatibilité avant le déploiement plutôt qu'en production.
- Observabilité en production : remplacer le `print`/le journal en mémoire par un vrai logger structuré + une trace par requête, pour pouvoir répondre à "pourquoi l'agent a-t-il pris cette décision pour CE client, à CE moment" longtemps après coup.
- Feature flags pour activer/désactiver un nouveau repli de l'agent (ex. changer de destination) sans redéploiement, et pouvoir revenir en arrière instantanément si le comportement surprend en production.
- Revue de code centrée sur ces principes plutôt que sur le style : dans une équipe, la question à poser n'est pas "est-ce que ça marche ?" mais "est-ce que ça reste facile à changer dans six mois, par quelqu'un d'autre que moi ?".
