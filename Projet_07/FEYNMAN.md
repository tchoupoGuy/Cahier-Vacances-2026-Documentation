# Projet 07 — IA agentique : un agent qui planifie tes vacances

Source : `Cahier-Vacances-2026/Projet_07/projet_07.ipynb`

## 🎯 En une phrase

Un agent, ce n'est pas un LLM : c'est une boucle qui part d'un objectif, utilise des outils pour aller chercher des faits, vérifie si le résultat convient, et **se corrige tout seul** quand ce n'est pas le cas.

## 1. Explique-le à un enfant de 12 ans

Imagine que tu demandes à un ami organisateur de voyages : "Madrid, 4 nuits, 750 euros par personne, j'aime les musées." Un assistant bête ferait un seul essai — le vol le moins cher, l'hôtel le plus joli, toutes les visites — et s'il dépasse le budget, il dirait juste "désolé, impossible."

Un bon organisateur, lui, ne s'arrête pas là. Il regarde son premier plan, voit qu'il dépasse de 80 euros, et se demande : "qu'est-ce que je peux retirer sans gâcher le voyage ?" Il enlève la visite la plus chère, recalcule. Toujours trop cher ? Il change d'hôtel pour un moins cher. Toujours rien ? Il regarde même si partir un jour plus tôt ou plus tard ne changerait pas tout (les vols du week-end coûtent plus cher). Et à la fin, il t'explique exactement ce qu'il a dû sacrifier et pourquoi.

C'est exactement ça, un agent : pas un programme qui appelle trois fonctions dans l'ordre et s'arrête au premier problème, mais un programme qui **essaie, constate, corrige, réessaie**, et qui sait expliquer ses choix.

Ce projet est aussi la synthèse de tout l'été : les outils de l'agent sont exactement le SQL du Projet 01 (pour les vols et les activités) et les embeddings du Projet 04 (pour comprendre "un hôtel calme avec une piscine" dans les brochures d'hôtels).

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **Agent** | Une boucle : objectif → outil → évaluation → correction si besoin | Un organisateur de voyage humain qui n'abandonne jamais au premier essai |
| **Outil (tool)** | Une fonction qui va chercher un fait précis dans le monde extérieur | Un coup de fil à l'aéroport, un coup de fil à l'hôtel |
| **Requête paramétrée (`?`)** | Une requête SQL où les valeurs sont fournies à part, jamais collées dans le texte | Remplir un formulaire à cases plutôt que d'écrire une phrase libre qu'on doit ensuite déchiffrer |
| **Injection SQL** | Une faille où une valeur mal insérée dans une requête est exécutée comme du code | Glisser un ordre caché dans un formulaire que le système obéit sans vérifier |
| **Recherche sémantique** | Trouver un texte proche par le *sens*, pas par les mots exacts, via des embeddings | Comprendre que "havre de calme" et "hôtel tranquille" veulent dire la même chose |
| **Repli (fallback)** | La stratégie qu'un agent applique quand son premier plan échoue | Le plan B, puis le plan C, choisis dans un ordre réfléchi |
| **Journal (log de décision)** | La trace de chaque sacrifice ou ajustement fait par l'agent, en langage clair | Le carnet de bord de l'organisateur, qui explique chaque choix a posteriori |
| **Garde-fou (guardrail)** | Une vérification qui empêche une action irréversible sans accord explicite | Le bouton "êtes-vous sûr ?" avant de valider un paiement |
| **Streamlit** | Une librairie qui transforme un script Python en application web sans HTML/JS | Un traducteur automatique entre du code Python et une page web |
| **API REST** | Une interface où un serveur expose des fonctions à travers des adresses web (`/api/plan`) qui échangent du JSON | Le comptoir d'un guichet : tu passes une demande écrite dans un format fixe, on te répond dans le même format |
| **Sans état (stateless)** | Le serveur ne se souvient de rien entre deux requêtes ; chaque appel contient tout ce qu'il faut | Un guichet où tu dois redonner ton dossier complet à chaque visite, plutôt que de dire juste "comme la dernière fois" |

## 3. Comment ça marche, en détail

1. **Trois sources de données, trois métiers.** Une base SQL (`vols`, `activites`, `reservations`) et 135 brochures PDF d'hôtels en texte libre. Rien de commun entre les deux formats, donc deux familles d'outils différentes.
2. **Les deux premiers outils sont du SQL paramétré.** `outil_vols` et `outil_activites` utilisent des `?` à la place des valeurs (jamais de f-string qui insère directement une valeur dans le SQL), pour se protéger des injections SQL et des caractères spéciaux (comme une apostrophe dans un nom de ville).
3. **Le troisième outil est une recherche sémantique.** `outil_hotels` encode le résumé de chaque brochure et l'envie du voyageur en vecteurs, puis compare par similarité cosinus (produit scalaire de vecteurs normalisés). Seuls la présentation et les avis clients sont encodés, pas la liste d'équipements ni le pied de page : ce texte quasi-identique d'une brochure à l'autre rapprocherait artificiellement tous les hôtels entre eux (mesuré dans le projet : 80 % → 92 % de bonnes réponses en ne gardant que le texte qui porte le sens).
4. **La boucle de décision (`essayer_une_date`) applique un ordre de sacrifice réfléchi.** D'abord les activités payantes (la plus chère en premier — retirer une sortie gratuite ne ferait rien économiser), puis seulement l'hôtel (en dernier, car explicitement demandé par le voyageur). Cet ordre n'est écrit nulle part dans les données : c'est une décision de conception, à assumer et à défendre.
5. **L'agent explore au-delà de ce qu'on lui a demandé (`planifier`).** Il regarde aussi les jours voisins de la date demandée, car le prix des vols varie fortement (week-end vs semaine). Il ne déplace jamais la date tout seul : il signale l'opportunité, la décision reste à l'utilisateur.
6. **Comparer des voyages "presque au budget" par le prix ne marche pas.** L'agent s'arrête dès qu'il repasse sous le budget, donc tous les plans finissent à peu près au même prix. Ce qui les différencie vraiment, c'est ce qu'il reste dedans (le nombre d'activités conservées) : d'où une clé de comparaison à deux niveaux, `(nombre d'activités, -prix)`.
7. **La réservation a un garde-fou explicite.** Tant que `confirme=False`, aucune écriture en base : la fonction se contente de décrire ce qu'elle *ferait*. C'est le principe de "action irréversible = confirmation obligatoire", central dans la conception d'agents fiables.
8. **L'interface n'est qu'une couche d'affichage — et il en existe deux ici.** Streamlit d'un côté (un script Python qui devient une page web) ; une API FastAPI + un frontend React/TypeScript de l'autre (le navigateur parle en JSON à un serveur Python). Les deux appellent exactement les mêmes fonctions `planifier` et `reserver` : c'est ce qui garantit qu'elles se comportent identiquement, sans code dupliqué.

## 4. Le code clé, annoté

```python
# Requête paramétrée : jamais de valeur collée directement dans le SQL
sql = """
    SELECT numero, origine, heure_depart, duree_h, prix_eur, places_restantes
    FROM vols
    WHERE destination = ? AND date_depart = ? AND places_restantes >= ?
    ORDER BY prix_eur
"""
requete(conn, sql, (destination, date_depart, voyageurs))
```

```python
# Recherche sémantique : comparer une envie libre aux brochures d'un ville
vecteurs = encoder(encodeur, hotels_ville["resume"])       # une ligne par hôtel
vecteur_envie = encoder(encodeur, [envie])[0]               # un seul vecteur
hotels_ville["score"] = vecteurs @ vecteur_envie             # similarité cosinus (vecteurs normalisés)
hotels_ville.sort_values("score", ascending=False).head(k)
```

```python
# La boucle de l'agent : sacrifier, dans un ordre réfléchi, jusqu'à tenir le budget
for _ in range(30):  # garde-fou anti-boucle infinie
    total = chiffrer_voyage(vol, hotel, retenues, nuits)
    if total <= budget_max:
        break
    if payantes:                              # repli n°1 : la sortie payante la plus chère
        plus_chere = max(payantes, key=lambda a: a["prix_eur"])
        retenues = [a for a in retenues if a is not plus_chere]
        position = 0
    elif position + 1 < len(ordre):            # repli n°2 : un hôtel moins cher
        position += 1
    else:                                        # plus rien à sacrifier
        impossible = True
```

```python
# Le garde-fou de la réservation : rien n'est écrit sans confirmation explicite
if not confirme:
    return "Rien n'a été réservé. ... Il faut confirmer pour que la réservation soit enregistrée."
conn.execute(sql, (...))
conn.commit()
```

## 5. Les pièges et questions qui bloquent

- **F-string dans une requête SQL = danger.** `f"WHERE destination = '{destination}'"` casse dès qu'une valeur contient une apostrophe, et ouvre la porte à l'injection SQL si la valeur vient d'un utilisateur. Toujours des `?` et un tuple de paramètres à part.
- **Encoder tout le texte d'une brochure dilue le signal.** Si la liste d'équipements et le pied de page (quasi identiques d'un hôtel à l'autre) sont inclus dans l'embedding, tous les hôtels se ressemblent artificiellement. Ne garder que le texte qui porte vraiment le sens (présentation + avis) améliore nettement la précision.
- **Comparer des prix pour juger "quel jour est le meilleur" est un piège.** L'agent s'arrête dès qu'il repasse sous le budget : tous les plans finissent proches du budget, donc les prix ne discriminent presque rien. Comparer le nombre d'activités conservées d'abord est la bonne clé.
- **L'ordre des sacrifices n'est pas neutre.** Sacrifier l'hôtel avant les activités déplairait au voyageur, puisque l'hôtel est ce qu'il a explicitement décrit. Ce choix de conception doit être assumé, pas caché.
- **Un embedding ne comprend pas la négation.** "Hôtel calme, sans enfants" peut quand même faire remonter des hôtels familiaux, car le modèle capte "enfants" sans comprendre le "sans". C'est une limite connue des embeddings, pas un bug.
- **Un agent qui invente une solution est dangereux.** Quand aucun jour ne convient, l'agent doit répondre "impossible", jamais forcer une réponse plausible mais fausse — même logique de prudence que la consigne anti-hallucination du Projet 04.

## 6. Test de Feynman

- Pourquoi dit-on qu'un agent n'est "pas un LLM" ? Qu'est-ce qui fait qu'un programme mérite ce nom ?
- Explique pourquoi `f"WHERE ville = '{ville}'"` est dangereux, avec un exemple concret d'apostrophe ou d'injection.
- Pourquoi ne garder que la présentation et les avis clients (et pas tout le texte) améliore-t-il la recherche d'hôtels ?
- Pourquoi l'agent sacrifie-t-il d'abord les activités payantes, puis seulement l'hôtel, jamais l'inverse ? Que déciderais-tu à sa place ?
- Pourquoi comparer les prix des voyages des jours voisins ne suffit-il pas pour juger lequel est "meilleur" ?
- À quoi sert le paramètre `confirme=False` par défaut dans `reserver()` ?

## 7. Pour aller plus loin

- Intégrer un LLM (comme le Qwen du Projet 04, ou une API Claude/ChatGPT) pour transformer une phrase libre ("je veux 2 semaines en famille avec 4000 euros") en la demande structurée que l'agent attend.
- Documentation Streamlit officielle : [docs.streamlit.io/develop/api-reference](https://docs.streamlit.io/develop/api-reference).
- Repenser l'ordre des sacrifices, ou ajouter un quatrième critère (ex. changer de destination) quand plus rien ne rentre.
- Pour la posture d'ingénierie plutôt que le domaine métier — comment un développeur devient performant sur ce type de projet en entreprise — voir [`PRINCIPES-INGENIERIE.md`](./PRINCIPES-INGENIERIE.md).
