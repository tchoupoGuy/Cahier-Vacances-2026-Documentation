# Projet 05 — Deep Learning & Vision : réécriture pro

Réécriture du notebook `Cahier-Vacances-2026/Projet_05/projet_05.ipynb` en petit projet de détection d'objets structuré comme en entreprise. Pour l'explication pédagogique (méthode Feynman), voir [`FEYNMAN.md`](./FEYNMAN.md).

## Pourquoi cette architecture

Un projet de vision par ordinateur "pro" sépare nettement les données (comment on lit et sert les images), le modèle (comment on l'adapte), l'entraînement (la boucle qui ajuste les poids), et l'inférence (comment on l'utilise ensuite) — quatre responsabilités que le notebook enchaînait dans les mêmes cellules. C'est ce qui permet, par exemple, de réutiliser exactement la même fonction `predict()` avant et après le fine-tuning, ou de changer de backbone sans toucher à la boucle d'entraînement.

```
Projet_05/
├── data/                             # dataset Kaggle téléchargé ici (non versionné)
├── checkpoints/                      # poids du modèle fine-tuné (fish_detector.pt)
├── src/
│   ├── data/
│   │   ├── yolo.py                   # parsing des annotations YOLO (pure logique, sans torch)
│   │   ├── catalog.py                # construit le tableau photo -> espèce dominante -> split
│   │   ├── dataset.py                # FishDetectionDataset (torch) + collate_fn
│   │   └── download.py               # téléchargement du dataset Kaggle
│   ├── models/
│   │   └── detector.py               # charge Faster R-CNN, gèle le backbone, adapte la tête
│   ├── training/
│   │   └── train.py                  # boucle d'entraînement (une epoch, plusieurs epochs)
│   ├── inference/
│   │   └── predict.py                # predict() générique + identify_fish() avec le modèle fine-tuné
│   ├── evaluation/
│   │   └── metrics.py                # mAP (mean Average Precision)
│   └── visualization/
│       └── plots.py                  # boîtes, comptage par espèce, courbes de loss
├── tests/                            # yolo.py et catalog.py (sans torch) + detector.py (si torch dispo)
├── main.py                           # pipeline complet : télécharge, fine-tune, sauvegarde
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_05
pip install -e ".[dev]"
python main.py           # télécharge le dataset (~350 Mo) et fine-tune (quelques minutes en CPU)
pytest                   # voir la note ci-dessous sur ce qui est testable sans torch
```

**Note sur les tests.** `src/data/yolo.py` et `src/data/catalog.py` ne dépendent que de Python standard et de pandas : ils sont testés à 100 % avec des fichiers d'annotation synthétiques, aucun réseau ni GPU requis. Les modules qui dépendent de `torch`/`torchvision` (`dataset.py`, `models/detector.py`, `training/`, `inference/`) sont conçus pour être testés de la même façon dans un environnement qui les a installés — `tests/test_detector.py` utilise `pytest.importorskip("torch")` et construit le modèle avec `pretrained=False` pour vérifier la logique de gel/adaptation sans télécharger de poids. Comme le notebook d'origine le recommande déjà (« si ta machine peine, importe ce code sur Google Colab »), ce projet est le plus lourd des six en dépendances.

## Comment lire ce code

- **`src/data/yolo.py` est volontairement indépendant de PyTorch.** Parser un fichier d'annotation est une pure question de texte et d'arithmétique ; l'isoler permet de le tester intégralement sans environnement GPU.
- **`src/models/detector.py` sépare le chargement (`load_pretrained`) de l'adaptation (`build_model`).** `build_model(pretrained=False)` construit la même architecture sans télécharger de poids : c'est ce qui permet de tester "le backbone est bien gelé" et "la tête a le bon nombre de sorties" hors-ligne.
- **`src/inference/predict.py` expose une fonction `predict()` générique** (utilisée telle quelle sur le modèle COCO brut, puis sur le modèle fine-tuné) et une fonction `identify_fish()` qui ne fait que décaler les indices d'espèces (`label 1 -> SPECIES[0]`, à cause de la classe "fond" réservée à l'indice 0).
- **`src/training/train.py` isole la boucle d'entraînement du reste** : `train_one_epoch` fait une passe, `train` l'enchaîne sur plusieurs epochs et construit l'historique de pertes utilisé ensuite pour le graphique.

## Aller plus loin (idées d'évolution "pro")

- Mesurer le modèle avec le mAP (`src/evaluation/metrics.py`) plutôt qu'à l'œil.
- Entraîner sur l'intégralité du dataset et plus d'epochs, sur GPU (Colab ou cloud).
- Ajouter de la data augmentation (`torchvision.transforms.v2`) dans le pipeline de `FishDetectionDataset`.
