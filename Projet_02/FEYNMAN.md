# Projet 02 — Machine Learning : qui gagnera la Coupe du Monde 2026 ?

Source : `Cahier-Vacances-2026/Projet_02/projet_02.ipynb`

## 🎯 En une phrase

Au lieu d'écrire des règles ("l'équipe qui marque le plus gagne"), on montre à un algorithme des milliers de matchs passés et on le laisse découvrir tout seul les régularités qui prédisent un résultat.

## 1. Explique-le à un enfant de 12 ans

Imagine que tu veuilles deviner qui va gagner un match sans jamais avoir vu les deux équipes jouer. Tu ne peux pas, sauf si quelqu'un te donne des indices : est-ce que cette équipe a gagné ses 5 derniers matchs ? Est-ce qu'elle joue à domicile ? Est-ce que l'autre équipe encaisse beaucoup de buts d'habitude ?

Le Machine Learning, c'est donner à un ordinateur des milliers d'exemples de matchs passés avec ces indices et le résultat final, et le laisser trouver tout seul la recette : "quand telle combinaison d'indices apparaît, l'équipe à domicile gagne généralement". Une fois que l'ordinateur a compris cette recette sur les matchs passés, on peut lui donner les indices d'un match qui n'a pas encore eu lieu, et il donne un pronostic.

Le piège à éviter à tout prix : ne jamais tester la mémoire de l'élève avec les questions qu'il a déjà vues en cours. Il faut lui garder des exemples cachés, jamais montrés pendant l'apprentissage, pour vérifier honnêtement s'il a compris ou juste appris par cœur.

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **Feature** (caractéristique) | Une information numérique décrivant un exemple, donnée en entrée du modèle | Un indice qu'on donne à l'élève pour l'aider à répondre |
| **Target** (cible) | Ce qu'on veut prédire | La bonne réponse qu'on connaît pour les exemples passés, et qu'on cache pour les exemples futurs |
| **Apprentissage supervisé** | On montre des exemples ET leur bonne réponse | Un cours avec un corrigé pour chaque exercice |
| **Encodage** | Transformer une info non numérique (texte, catégorie) en nombre | Remplacer "domicile"/"extérieur" par 1/0 pour qu'une calculatrice puisse s'en servir |
| **Standardisation** (`StandardScaler`) | Ramener toutes les colonnes à la même échelle (moyenne 0, écart-type 1) | Convertir des notes sur 20 et des notes sur 100 dans la même unité pour pouvoir les comparer équitablement |
| **`train_test_split`** | Séparer les données en un lot pour apprendre et un lot pour évaluer, jamais mélangés | Garder une partie des exercices "en réserve", jamais montrés en cours, pour faire un vrai contrôle surprise |
| **Random Forest** (forêt aléatoire) | Un "comité" de nombreux arbres de décision qui votent, chacun ayant vu les données un peu différemment | Demander l'avis à 200 experts qui ont chacun étudié un échantillon un peu différent du dossier, puis prendre la majorité |
| **Accuracy** (exactitude) | La proportion de prédictions correctes sur le lot de test | La note du contrôle surprise, en pourcentage de bonnes réponses |
| **Matrice de confusion** | Un tableau qui montre, pour chaque vraie catégorie, ce que le modèle a prédit | Le détail des erreurs du contrôle : pas juste la note, mais QUELLES questions ont été ratées et par quoi elles ont été confondues |
| **Feature importance** | Un score qui indique combien chaque indice a pesé dans les décisions du modèle | Demander à l'élève : "sur quel indice t'es-tu le plus appuyé pour répondre ?" |

## 3. Comment ça marche, en détail

1. **On récupère des données réelles.** Un fichier de plus de 49 000 matchs internationaux depuis 1872, avec équipes, scores, type de compétition, lieu.
2. **On filtre pour rester pertinent.** Le foot de 1872 n'a plus rien à voir avec celui d'aujourd'hui : on se limite à l'ère moderne (1994–2026) pour que les régularités apprises restent valables.
3. **On explore avant de modéliser** ("les débats de la taverne") : l'avantage du terrain existe-t-il vraiment dans les chiffres ? Quelles équipes dominent ? Le foot est-il plus offensif aujourd'hui ? C'est le réflexe indispensable de tout data scientist : comprendre les données avant de les donner à un algorithme.
4. **On construit les features.** Un modèle ne comprend que des nombres : il faut décrire chaque match avec des indicateurs de forme récente (buts marqués/encaissés, victoires sur les derniers matchs) pour les deux équipes, puis calculer des **features différentielles** (équipe A moins équipe B) pour que le modèle compare directement les deux forces en présence.
5. **On simplifie la cible.** Le résultat brut (victoire/nul/défaite) est réduit à une prédiction binaire (l'équipe à domicile gagne, oui/non), plus simple à apprendre dans un premier temps.
6. **On sépare train et test AVANT tout entraînement.** Règle d'or : jamais évaluer un modèle sur les données qui ont servi à l'entraîner, sinon la note ne veut rien dire (c'est "réviser sur les annales de l'examen").
7. **On standardise.** Pas strictement nécessaire pour une forêt aléatoire, mais bonne pratique si on change un jour de modèle (régression logistique, réseau de neurones...).
8. **On entraîne (`.fit()`) et on évalue (`.predict()` + `accuracy_score` + matrice de confusion).** On regarde aussi les `feature_importances_` pour savoir ce qui a le plus compté dans les décisions.
9. **On utilise le modèle pour simuler un tournoi entier**, match après match, jusqu'à la finale — l'aboutissement concret du travail.

## 4. Le code clé, annoté

```python
from sklearn.model_selection import train_test_split

X = df[FEATURES]          # les indices (features)
y = df["home_win"]        # la bonne réponse (target)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,      # 20 % des matchs mis de côté pour le contrôle final
    random_state=42,    # pour que tout le monde ait le même découpage
)
```

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # apprend l'échelle SUR le train...
X_test_scaled = scaler.transform(X_test)         # ...et l'applique telle quelle au test
```

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train_scaled, y_train)       # l'apprentissage
predictions = model.predict(X_test_scaled)  # les pronostics sur les matchs jamais vus
```

```python
# Quels indices ont le plus pesé dans les décisions ?
importances = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
```

## 5. Les pièges et questions qui bloquent

- **`fit_transform` sur le train, `transform` seul sur le test.** Si on refait un `fit` sur le test, on "triche" en laissant les infos du test influencer l'échelle de standardisation. La règle : le scaler apprend uniquement sur le train.
- **Une accuracy élevée ne veut pas tout dire.** Si 70 % des matchs sont gagnés à domicile, un modèle qui répond toujours "domicile gagne" aurait déjà 70 % d'accuracy sans rien avoir appris. La matrice de confusion révèle ce genre de biais.
- **Les features différentielles évitent une confusion classique.** Donner brutalement "buts marqués équipe A" et "buts marqués équipe B" force le modèle à réapprendre la comparaison lui-même ; lui donner directement la différence facilite l'apprentissage.
- **`random_state=42` n'est pas magique**, c'est juste une graine de hasard fixée pour que le découpage et l'entraînement soient reproductibles d'une exécution à l'autre.
- **La feature importance ne dit pas "cause".** Un indice important dans les décisions du modèle n'est pas forcément la cause du résultat, seulement une variable corrélée qui aide à prédire.

## 6. Test de Feynman

- Pourquoi est-il interdit d'évaluer un modèle sur les données qui ont servi à l'entraîner ? Donne une analogie qui n'est pas celle du contrôle scolaire.
- Explique la différence entre `fit_transform` et `transform`, et pourquoi on ne les utilise pas de la même façon sur train et test.
- Pourquoi utiliser des features différentielles (équipe A moins équipe B) plutôt que les valeurs brutes des deux équipes ?
- Un modèle a 65 % d'accuracy. Est-ce bon ou mauvais ? Quelle info te manque pour répondre ?
- Comment une forêt aléatoire de 200 arbres arrive-t-elle à une seule prédiction ?

## 7. Pour aller plus loin

- Formation gratuite Pandas mentionnée dans le projet : [playlist YouTube Machine Learnia](https://www.youtube.com/watch?v=zZkNOdBWgFQ&list=PLO_fdPEVlfKqMDNmCFzQISI2H_nJcEDJq&index=17)
- Idées du notebook : donner un avantage terrain contrôlé aux pays hôtes, élargir la fenêtre de forme récente, tenter une simulation de Monte Carlo, ou prédire les 3 classes (victoire/nul/défaite) au lieu du binaire.
