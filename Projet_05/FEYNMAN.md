# Projet 05 — Deep Learning & Vision : encadrer et nommer les poissons de l'aquarium

Source : `Cahier-Vacances-2026/Projet_05/projet_05.ipynb`

## 🎯 En une phrase

Plutôt que de réentraîner un réseau de neurones de vision depuis zéro (des jours de calcul), on prend un modèle déjà entraîné sur des millions d'images et on ne réajuste que sa dernière partie sur nos 13 espèces de poissons : c'est le fine-tuning.

## 1. Explique-le à un enfant de 12 ans

Imagine un expert qui a déjà vu des millions de photos et sait très bien repérer "il y a quelque chose ici" dans une image (une forme, un contour, une texture) — c'est un peu comme quelqu'un qui sait déjà très bien dessiner des cadres autour des objets sur une photo, sans savoir encore nommer ce qu'il y a dedans. On lui montre alors seulement des photos de poissons avec leurs noms, et on ne lui réapprend qu'une seule chose : "voici comment s'appellent ces 13 espèces". Le reste de son savoir-faire (repérer des formes, des contours) reste intact, on ne touche pas à cette partie-là, on l'a "gelée".

Ça marche parce que la détection d'objets se décompose en deux étapes : d'abord repérer des zones "qui ressemblent à quelque chose" dans l'image (n'importe quoi, peu importe quoi exactement), puis regarder chaque zone de plus près pour dire ce que c'est précisément. La première étape est un savoir-faire assez générique (les contours, les formes, ça se ressemble beaucoup d'un objet à l'autre), donc on la garde telle quelle. Seule la deuxième étape, très spécifique à nos poissons, a besoin d'être réentraînée.

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **Détection d'objets** | Repérer où sont les objets dans une image (des boîtes) ET dire ce qu'ils sont (une étiquette) | Encadrer chaque poisson sur la photo ET écrire son nom à côté |
| **Faster R-CNN** | Une architecture de détection en deux temps : proposer des zones candidates, puis les classifier | Un premier regard rapide qui dit "il y a peut-être quelque chose ici, ici et là", puis un second regard qui identifie précisément chaque zone |
| **Backbone** | La partie du réseau qui extrait des caractéristiques visuelles génériques (contours, textures, formes) | Les yeux entraînés de l'expert : il sait "voir" les formes, indépendamment du sujet |
| **Fine-tuning** | Réentraîner seulement une partie d'un modèle déjà entraîné, sur de nouvelles données | Apprendre un nouveau vocabulaire à quelqu'un qui sait déjà lire et écrire, sans lui réapprendre l'alphabet |
| **Geler des paramètres** (`requires_grad = False`) | Empêcher une partie du réseau d'être modifiée pendant l'entraînement | Mettre du scotch sur les réglages qu'on ne veut surtout pas toucher |
| **Loss** (perte) | Un nombre qui mesure à quel point le modèle se trompe ; l'entraînement cherche à le faire baisser | La note d'erreur du contrôle : plus elle est basse, mieux c'est |
| **Époque / boucle d'entraînement** | Un passage complet sur les données d'entraînement, avec ajustement des poids à chaque lot | Une série de fiches de révision, corrigées et ajustées une par une |
| **Score de confiance** | La probabilité que le modèle attribue à sa propre prédiction | À quel point l'expert est sûr de lui pour chaque zone repérée |

## 3. Comment ça marche, en détail

1. **On observe d'abord ce que le modèle pré-entraîné sait déjà faire**, avant tout entraînement sur nos données. Il sait détecter "un objet" en général (grâce à son pré-entraînement sur le jeu de données COCO), mais ne connaît pas nos 13 espèces de poissons.
2. **On prépare les données à "servir" au modèle** : les photos et leurs boîtes annotées (format YOLO, converti en coordonnées pixel), organisées en lots (batches).
3. **On adapte le modèle** : on gèle le `backbone` (`requires_grad = False` sur ses paramètres) pour préserver son savoir-faire visuel général, et on ne laisse entraînable que la tête de classification des boîtes (`roi_heads.box_predictor`), la seule partie vraiment concernée par nos 13 espèces.
4. **On écrit la boucle d'entraînement.** Particularité de ce modèle : en mode entraînement, `model(images, targets)` ne renvoie pas des prédictions mais un dictionnaire de 4 pertes différentes (classification, position des boîtes, "y a-t-il un objet", position proposée par le RPN). On les additionne pour obtenir une perte totale, qu'on rétropropage (`loss.backward()`) avant de mettre à jour les poids (`optimizer.step()`).
5. **On observe que certaines pertes baissent plus que d'autres.** Les pertes liées à la classification et à l'ajustement fin des boîtes baissent le plus, car ce sont les seules parties vraiment nouvelles pour le modèle ; celles liées à la simple détection "d'un objet quelconque" étaient déjà bien apprises par le pré-entraînement.
6. **On utilise le modèle fine-tuné** avec la même fonction `predict` qu'à l'étape d'observation initiale, mais cette fois avec les noms des 13 espèces de poissons.

## 4. Le code clé, annoté

```python
# Geler tout le backbone : on ne veut RIEN changer à son savoir-faire visuel général
for param in model.backbone.parameters():
    param.requires_grad = False
```

```python
model.train()  # mode entraînement : le modèle va renvoyer des pertes, pas des prédictions

for images, targets in data_loader:
    loss_dict = model(images, targets)      # 4 pertes différentes, une par sous-tâche
    loss = sum(loss_dict.values())          # on les additionne en une perte totale

    optimizer.zero_grad()   # on remet les gradients à zéro avant de recalculer
    loss.backward()         # rétropropagation : calcule comment ajuster chaque poids
    optimizer.step()        # applique la mise à jour des poids
```

```python
def predict(model, image_path, score_thresh=0.5):
    model.eval()
    with torch.no_grad():                    # pas besoin de calculer de gradients pour prédire
        prediction = model([image])[0]        # une liste d'un seul dictionnaire {"boxes", "labels", "scores"}
    mask = prediction["scores"] > score_thresh  # on ne garde que les prédictions sûres d'elles
    return prediction["boxes"][mask], prediction["labels"][mask], prediction["scores"][mask]
```

## 5. Les pièges et questions qui bloquent

- **Geler le backbone n'est pas un raccourci paresseux, c'est une stratégie.** Ça évite d'avoir besoin de millions d'images et de jours de calcul : on économise du temps et de la puissance de calcul en réutilisant un savoir-faire déjà acquis.
- **`model(images, targets)` ne se comporte pas pareil en `.train()` et en `.eval()`.** En entraînement, il renvoie des pertes ; en évaluation, il renvoie des prédictions. Confondre les deux modes est une source d'erreur fréquente.
- **4 pertes différentes, pas une seule.** Bien comprendre que `loss_classifier` et `loss_box_reg` concernent la partie qu'on entraîne vraiment (nos 13 espèces), alors que `loss_objectness` et `loss_rpn_box_reg` viennent d'une partie déjà largement acquise (repérer "un objet" en général).
- **Le score de confiance n'est pas la vérité, c'est une estimation.** Un seuil (`score_thresh`) trop bas laisse passer du bruit, trop haut fait rater de vraies détections — c'est un compromis à ajuster.
- **La difficulté annoncée (6/10) est normale.** C'est le premier projet du cahier où l'on "ouvre le capot" d'un vrai entraînement de réseau de neurones, sans le confort d'un `.fit()` unique de scikit-learn.

## 6. Test de Feynman

- Pourquoi geler le backbone permet-il d'entraîner un détecteur d'objets en quelques minutes sur un simple CPU, plutôt qu'en plusieurs jours ?
- Explique la différence entre ce que renvoie `model(images, targets)` en mode `.train()` et en mode `.eval()`.
- À quoi servent concrètement les 4 pertes différentes de Faster R-CNN, et pourquoi certaines baissent plus vite que d'autres pendant le fine-tuning ?
- Que se passe-t-il si le seuil de score de confiance (`score_thresh`) est fixé trop bas ? Trop haut ?
- Pourquoi la partie "repérer une zone qui ressemble à un objet" est-elle réutilisable d'un problème de vision à un autre, contrairement à la partie "nommer précisément l'objet" ?

## 7. Pour aller plus loin

- Mesurer objectivement le détecteur avec le **mAP** (`compute_map`, fourni dans `utils.py`), la métrique standard de la détection, plutôt que de juger "à l'œil".
- Entraîner sur l'intégralité des 6800 photos et davantage d'époques, idéalement sur Google Colab avec un GPU, et comparer le mAP obtenu.
