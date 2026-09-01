# Projet 03 — Clustering & algorithmes : dessiner le Tour de France 2027

Source : `Cahier-Vacances-2026/Projet_03/projet_03.ipynb`

## 🎯 En une phrase

Deux problèmes différents, deux familles d'outils : regrouper des points proches sans aucune "bonne réponse" fournie (clustering), puis trouver un ordre de passage le plus court possible dans chaque groupe (heuristiques d'optimisation).

## 1. Explique-le à un enfant de 12 ans

Imagine 120 points dispersés sur une carte de France, et tu dois les répartir en 21 paquets, chaque paquet regroupant des villages proches les uns des autres — un peu comme trier des billes par couleur, sauf qu'ici la "couleur" c'est la position géographique. Personne ne te donne la bonne réponse à l'avance : c'est à l'algorithme de deviner tout seul quels points vont naturellement ensemble. C'est ça, l'apprentissage **non supervisé**.

Une fois les paquets faits, il reste un deuxième problème, un peu différent : dans chaque paquet, dans quel ordre visiter les villages pour parcourir le moins de kilomètres possible ? Ce problème s'appelle le "voyageur de commerce", et il est tellement difficile que même les meilleurs ordinateurs du monde ne peuvent pas tester toutes les combinaisons dès qu'il y a beaucoup de villages (le nombre de trajets possibles explose plus vite que tu ne l'imagines). La solution : des recettes malines qui ne trouvent pas forcément LE meilleur chemin, mais un très bon chemin, en un temps raisonnable.

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **Apprentissage non supervisé** | Trouver une structure dans les données sans qu'on donne la bonne réponse | Trier des chaussettes par couleur sans qu'on te dise combien de tas faire ni quelle couleur va où |
| **Clustering** | Regrouper des points selon leur proximité | Former des équipes de camarades qui habitent près les uns des autres |
| **K-Means** | Placer K centres, assigner chaque point au centre le plus proche, recalculer les centres, répéter jusqu'à stabilité | Poser 21 punaises au hasard sur la carte, laisser chaque village "voter" pour la punaise la plus proche, déplacer chaque punaise au centre de son groupe, et recommencer |
| **CAH** (classification ascendante hiérarchique) | Partir de groupes d'un seul élément et fusionner à chaque étape les deux groupes les plus proches | Des amis isolés qui se regroupent petit à petit en bandes, en fusionnant toujours les deux bandes les plus proches |
| **Score de silhouette** | Une note entre -1 et 1 qui mesure si chaque point est bien plus proche de son groupe que du groupe voisin | La note de qualité d'un tri : est-ce que chaque bille est bien dans le bon tas et loin des autres tas ? |
| **TSP** (problème du voyageur de commerce) | Trouver l'ordre de passage le plus court à travers un ensemble de points | Un livreur qui veut visiter toutes ses adresses en roulant le moins possible |
| **Algorithme glouton (greedy)** | À chaque étape, on prend le choix qui semble le meilleur sur l'instant, sans anticiper la suite | Un randonneur qui choisit toujours le sentier le plus proche, sans se demander s'il va se retrouver coincé plus loin |
| **2-opt** | Une amélioration locale : on teste des "croisements" de trajet et on les corrige s'ils raccourcissent le chemin | Repérer que deux bouts de ficelle du trajet se croisent sur la carte et les "décroiser" pour gagner de la distance |

## 3. Comment ça marche, en détail

1. **On explore les 120 villages** (répartition par département, carte) avant de lancer le moindre algorithme — toujours regarder les données d'abord.
2. **On corrige un piège géographique** : les coordonnées sont en degrés de latitude/longitude, mais un degré de longitude ne vaut pas la même distance réelle qu'un degré de latitude (les méridiens se resserrent en s'éloignant de l'équateur). Il faut convertir en kilomètres avant de calculer des distances, sinon le clustering serait faussé par cette déformation.
3. **On teste deux algorithmes de clustering, K-Means et CAH**, plutôt que de se contenter du premier venu — c'est la démarche attendue d'un data scientist : comparer, pas se satisfaire d'un seul essai.
4. **On juge objectivement avec le score de silhouette** et en regardant la taille de chaque groupe, plutôt qu'à l'œil.
5. **Une fois les 21 étapes formées**, pour chacune il faut résoudre un mini-TSP : trouver le meilleur ordre de passage entre ses villages.
6. **On explique pourquoi le force brute est impossible** : le nombre d'ordres possibles explose de façon factorielle avec le nombre de villages — tester tous les trajets d'une étape à 10 villages, ce n'est déjà plus envisageable.
7. **On construit une solution rapide avec l'algorithme glouton** : depuis le village courant, toujours aller au plus proche village non visité.
8. **On l'améliore avec 2-opt**, qui corrige les croisements de trajet que le glouton a pu laisser passer (le glouton avance sans jamais revenir en arrière, donc il peut créer des détours absurdes qu'une passe d'amélioration locale répare).

## 4. Le code clé, annoté

```python
from sklearn.cluster import KMeans

kmeans = KMeans(
    n_clusters=21,     # on veut 21 étapes, comme le vrai Tour de France
    random_state=42,   # reproductibilité (le placement initial des centres est aléatoire)
    n_init=10,          # essaie 10 placements de départ différents, garde le meilleur
)
labels_kmeans = kmeans.fit_predict(villages[["x_km", "y_km"]])  # un numéro d'étape par village
```

```python
from sklearn.cluster import AgglomerativeClustering

# Pas de random_state : la CAH ne tire rien au hasard, résultat toujours identique
labels_cah = AgglomerativeClustering(n_clusters=21, linkage="ward").fit_predict(
    villages[["x_km", "y_km"]]
)
```

```python
from sklearn.metrics import silhouette_score

sil_kmeans = silhouette_score(villages[["x_km", "y_km"]], labels_kmeans)
sil_cah = silhouette_score(villages[["x_km", "y_km"]], labels_cah)
# Plus le score est proche de 1, mieux les groupes sont séparés et compacts
```

```python
def greedy_path(indices, depart):
    chemin = [depart]
    restants = set(indices) - {depart}
    while restants:
        courant = chemin[-1]
        # à chaque étape : le village non visité le plus proche du village courant
        prochain = min(restants, key=lambda v: distance(courant, v))
        chemin.append(prochain)
        restants.remove(prochain)
    return chemin
```

## 5. Les pièges et questions qui bloquent

- **Ne pas convertir les degrés en kilomètres est une erreur silencieuse.** Le code tourne sans erreur, mais les groupes formés sont subtilement déformés est-ouest, car un degré de longitude "pèse" moins qu'un degré de latitude en France.
- **K-Means dépend d'un départ aléatoire, la CAH non.** C'est pour ça que K-Means a un `random_state` et un `n_init` (pour limiter le risque de tomber sur un mauvais tirage de départ), alors que la CAH donne toujours exactement le même résultat.
- **Le score de silhouette juge la géométrie, pas le "bon sens métier".** Un découpage peut avoir un bon score de silhouette tout en produisant une étape avec un seul village et une autre avec vingt — regarder aussi la taille des groupes reste indispensable.
- **Un algorithme glouton n'est jamais garanti optimal.** Il peut se retrouver "coincé" à devoir faire un grand détour à la fin parce qu'il a fait des choix myopes au début. C'est exactement ce que 2-opt vient corriger après coup.
- **Le TSP en vol d'oiseau n'est qu'une approximation.** De vraies routes ne sont pas des lignes droites ; le notebook le signale explicitement comme piste d'amélioration.

## 6. Test de Feynman

- Pourquoi faut-il convertir les coordonnées GPS en kilomètres avant de faire un clustering géographique ?
- Explique la différence de logique entre K-Means (partir de centres) et la CAH (partir de groupes individuels qui fusionnent).
- Pourquoi ne peut-on pas simplement tester tous les ordres de passage possibles pour trouver le trajet le plus court, même avec seulement 15 villages ?
- Qu'est-ce qu'un algorithme "glouton" décide à chaque étape, et pourquoi ce n'est pas toujours la meilleure stratégie globale ?
- À quoi sert concrètement le 2-opt après le glouton ?

## 7. Pour aller plus loin

- Télécharger une autre liste de villes françaises et refaire l'exercice de zéro.
- Remplacer les distances "à vol d'oiseau" par de vraies distances routières.
- Découvrir des solveurs professionnels de tournées comme OR-Tools de Google.
