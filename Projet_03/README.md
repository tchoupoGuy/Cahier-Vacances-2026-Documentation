# Projet 03 — Clustering & TSP : réécriture pro

Réécriture du notebook `Cahier-Vacances-2026/Projet_03/projet_03.ipynb` en petit projet d'optimisation structuré comme en entreprise. Pour l'explication pédagogique (méthode Feynman), voir [`FEYNMAN.md`](./FEYNMAN.md).

## Pourquoi cette architecture

Ce projet mélange deux algorithmes de nature très différente (clustering géométrique, puis optimisation combinatoire), plus une bonne dose d'affichage cartographique. Une architecture pro sépare ces trois familles de responsabilités dans des sous-packages distincts, pour qu'on puisse par exemple changer l'algorithme de routage sans toucher au clustering, ou remplacer l'affichage matplotlib par une autre librairie sans toucher au calcul.

```
Projet_03/
├── data/
│   ├── villages_2027.csv           # les 120 villages-étapes
│   └── france_outline.json         # contour de la France (donnée, pas du code)
├── src/
│   ├── data/
│   │   └── loader.py                # chargement + projection GPS -> kilomètres
│   ├── clustering/
│   │   └── stages.py                # K-Means, CAH, comparaison par score de silhouette
│   ├── routing/
│   │   ├── distance.py              # haversine, matrice de distances, longueur de parcours
│   │   └── heuristics.py            # glouton (plus proche voisin) + 2-opt
│   ├── visualization/
│   │   └── maps.py                  # tous les graphiques (fond de carte, étapes, tracé final)
│   ├── roadbook.py                  # mise en forme texte du livre de route
│   └── pipeline.py                  # orchestre les deux missions de bout en bout
├── reports/figures/                 # cartes générées (villages, étapes, tracé final...)
├── tests/                           # distance, heuristiques, pipeline complet
├── main.py                          # construit le Tour 2027 complet et affiche le livre de route
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_03
pip install -e ".[dev]"
python main.py          # découpe la France en 21 étapes, route chacune, affiche le livre de route
pytest                  # vérifie les distances, les heuristiques et le pipeline complet
```

## Comment lire ce code

- **`data/france_outline.json` sépare la donnée géographique du code.** Le contour de la France (~470 points) n'a rien à faire mélangé au code Python d'affichage : c'est une ressource statique, versionnée à part, comme le seraient des données de référence dans un vrai projet.
- **`src/clustering/stages.py` ne connaît rien au routage.** Il prend des coordonnées, renvoie des étiquettes de groupe. Le choix final (K-Means retenu plutôt que la CAH) est documenté dans `FEYNMAN.md` et appliqué dans `pipeline.py`, pas caché dans le module de clustering lui-même.
- **`src/routing/heuristics.py` combine deux briques indépendantes** : `greedy_path` (construction rapide et approximative) et `two_opt` (amélioration locale). `best_route` les enchaîne en testant plusieurs points de départ, exactement comme le faisait la partie 3 du notebook.
- **`src/pipeline.py` est le seul endroit qui connaît l'enchaînement complet** des deux missions (découper puis router) ; `main.py` et les tests s'appuient dessus plutôt que de rejouer la logique.
- **Les tests reprennent les bornes numériques du notebook** (score de silhouette entre 0.30 et 0.60, distance totale entre 3600 et 4600 km) pour garantir que la réécriture produit un Tour équivalent.

## Aller plus loin (idées d'évolution "pro")

- Remplacer les distances à vol d'oiseau par de vraies distances routières (API de routing).
- Comparer les heuristiques maison à un solveur professionnel comme OR-Tools de Google.
- Rendre `N_STAGES` et le fichier de villages configurables en ligne de commande.
