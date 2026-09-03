# Projet 04 — RAG & LLM : l'assistant virtuel de l'Hôtel Le Belvédère

Source : `Cahier-Vacances-2026/Projet_04/projet_04.ipynb`

## 🎯 En une phrase

Un modèle de langage qui ne connaît pas ta documentation invente des réponses plausibles mais fausses ; le RAG lui donne d'abord les bons passages à lire, pour qu'il réponde avec de vraies sources au lieu de deviner.

## 1. Explique-le à un enfant de 12 ans

Un modèle de langage (un LLM, comme ceux derrière ChatGPT) est un peu comme un élève très cultivé, mais qui n'a jamais mis les pieds dans l'hôtel dont tu lui parles. Si tu lui demandes "avez-vous un spa ?", il va deviner une réponse crédible, un peu comme un élève qui invente une réponse à l'examen plutôt que de dire "je ne sais pas" — c'est ce qu'on appelle une **hallucination**.

La solution la plus bête serait de lui donner tout le classeur de règlement de l'hôtel à chaque question. Ça marche un peu mieux, mais c'est lent (il doit tout relire à chaque fois) et ça devient impossible si le classeur fait 500 pages.

La vraie solution, le RAG, imite ce que ferait un bon réceptionniste humain : pour répondre à une question sur le wifi, il n'ouvre pas le classeur entier, il va directement à la bonne page. Comment une machine trouve "la bonne page" ? En transformant chaque texte en une suite de nombres qui capture son *sens* (un embedding), un peu comme un code postal du sens : deux textes qui veulent dire la même chose, même avec des mots différents, ont des codes très proches. On calcule ainsi à l'avance le "code" de chaque page de documentation, puis, à chaque question, on calcule le code de la question et on va chercher les pages dont le code est le plus proche.

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **LLM** (grand modèle de langage) | Un programme entraîné à prédire la suite d'un texte, capable de générer des réponses | Un élève qui a lu énormément de textes et devine la suite la plus probable |
| **Hallucination** | Une réponse inventée, présentée avec assurance comme si elle était vraie | Un élève qui invente une date plutôt que d'avouer qu'il ne sait pas |
| **Prompt** | Le texte complet envoyé au modèle (rôle, contexte, question, consignes) | La feuille de consigne donnée à l'élève avant qu'il ne rédige sa réponse |
| **Contexte / fenêtre de contexte** | La quantité de texte que le modèle peut lire en une fois | La taille du bureau de l'élève : combien de pages il peut avoir sous les yeux en même temps |
| **RAG** (Retrieval-Augmented Generation) | Chercher les passages pertinents AVANT de générer la réponse, puis ne donner que ceux-là au modèle | Le réceptionniste qui va chercher la bonne page du classeur avant de répondre au client |
| **Chunk** | Un petit morceau de document (quelques paragraphes), unité de base pour la recherche | Une fiche du classeur, une par sujet |
| **Embedding** | Un vecteur de nombres qui représente le sens d'un texte | Un "code postal du sens" : deux textes proches en signification ont des codes proches, même sans mots communs |
| **Similarité cosinus** | Une mesure (entre -1 et 1) de la proximité entre deux vecteurs d'embedding | Mesurer à quel point deux flèches pointent dans la même direction |
| **Base de données vectorielle** | Un stockage optimisé pour chercher rapidement les vecteurs les plus proches d'un vecteur donné | Le tiroir à fiches organisé pour retrouver instantanément les fiches les plus pertinentes |
| **Chunking par fenêtre glissante** | Découper un texte par TAILLE fixe (avec chevauchement), plutôt que par structure (page, section) | Utile quand le document n'a pas de découpage naturel en petites unités mono-sujet, contrairement aux rubriques du Belvédère |
| **Gradio** | Bibliothèque Python qui transforme une fonction en interface web, avec un lien de partage temporaire en option | Le raccourci pour donner un "visage" et une adresse publique à un script qui, sinon, ne tourne que dans un terminal |

## 3. Comment ça marche, en détail

Le projet avance en trois actes délibérément progressifs :

1. **Acte 1 — le LLM "tout nu".** On interroge un modèle de langage générique sur l'hôtel, sans lui donner aucune information. Il répond quand même, avec assurance, souvent en inventant. Ça démontre le problème avant de le résoudre.
2. **Acte 2 — tout dans le prompt.** On extrait le texte de 5 PDF (avec `pypdf`), on les met en forme en Markdown (les LLM ont beaucoup vu de Markdown à l'entraînement et s'y retrouvent mieux), puis on colle l'intégralité de cette documentation dans le prompt à chaque question. Les réponses s'améliorent nettement, mais l'approche a trois limites : c'est lent (tout relire à chaque fois), ça ne passe pas à l'échelle (impossible avec des milliers de pages), et question confidentialité, envoyer tout un corpus sensible à un service externe peut être inacceptable pour certaines organisations.
3. **Acte 3 — le vrai RAG.** On transforme chaque rubrique de documentation (chunk) en embedding avec `sentence-transformers`, on transforme aussi la question du client en embedding, et on calcule la similarité entre la question et chaque chunk. On ne garde que les chunks les plus pertinents pour les glisser dans le prompt — la documentation "ciblée" plutôt que "complète". Le modèle répond alors plus juste, plus vite, et peut honnêtement dire "je ne sais pas" quand rien de pertinent n'est trouvé (grâce à une consigne explicite dans le prompt qui l'y autorise).

## 4. Le code clé, annoté

```python
from transformers import pipeline

# Un LLM léger, prêt à générer du texte en une ligne
generator = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")
```

```python
# Le prompt assemble 4 ingrédients dans un ordre précis
prompt = f"{ROLE}\n\n{context}\n\nQuestion d'un client : {question}\n{CONSIGNE}"
# ROLE      : qui doit incarner le modèle
# context   : la documentation (complète en Acte 2, filtrée en Acte 3)
# question  : la question du client
# CONSIGNE  : l'interdiction explicite d'inventer, qui offre une porte de sortie honnête
```

```python
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # modèle multilingue, français inclus

# On encode une fois pour toutes les 15 rubriques de la doc (la "base vectorielle")
chunk_embeddings = embedder.encode(
    pages["section"].tolist(),
    normalize_embeddings=True,   # vecteurs de longueur 1 : la similarité devient un simple produit scalaire
)
```

```python
# À chaque question : encoder la question, puis chercher les chunks les plus proches
question_embedding = embedder.encode([question], normalize_embeddings=True)
similarités = chunk_embeddings @ question_embedding.T   # produit scalaire = similarité cosinus
meilleurs_chunks = similarités.flatten().argsort()[::-1][:k]  # les k passages les plus pertinents
```

## 5. Les pièges et questions qui bloquent

- **"Tout dans le prompt" n'est pas un RAG.** C'est une étape intermédiaire utile pour comprendre le problème, mais le vrai RAG ajoute une étape de *recherche* qui sélectionne les passages avant de les donner au modèle.
- **La recherche par mots-clés échouerait ici.** Un client qui demande "acceptez-vous les chiens ?" ne trouverait rien si la doc parle d'"animaux domestiques" avec une recherche mot à mot. Les embeddings comparent le sens, pas l'orthographe — c'est tout leur intérêt.
- **Normaliser les embeddings n'est pas un détail cosmétique.** Sans `normalize_embeddings=True`, le simple produit scalaire ne serait plus équivalent à la similarité cosinus, et les longueurs de vecteurs fausseraient la comparaison.
- **La consigne anti-hallucination doit être explicite.** Le modèle ne "sait" pas spontanément qu'il doit refuser de répondre hors documentation ; c'est une instruction du prompt qui le lui permet.
- **Un `numpy` suffit à 15 chunks, pas à un million.** Le notebook le précise : en production, on utiliserait une vraie base vectorielle (FAISS, Chroma, Pinecone) capable de chercher parmi des millions de vecteurs en millisecondes.

## 6. Test de Feynman

- Pourquoi un LLM générique "invente"-t-il des réponses sur un sujet qu'il ne connaît pas, plutôt que de dire "je ne sais pas" ?
- Explique la différence entre "tout mettre dans le prompt" et un vrai RAG, et donne une situation où la première approche suffirait quand même.
- Comment un embedding permet-il de retrouver "animaux domestiques" à partir de la question "acceptez-vous les chiens ?" alors qu'aucun mot n'est commun ?
- À quoi sert la normalisation des embeddings avant de calculer une similarité par produit scalaire ?
- Pourquoi la confidentialité est-elle un argument en faveur du RAG face aux API de LLM géants ?
- `chunk_pages` (fenêtre glissante) et `load_pages` (par page) produisent les mêmes colonnes en sortie. Pourquoi ce choix de conception permet-il de changer de stratégie de chunking sans toucher à `VectorStore` ni à `rag_pipeline.py` ?
- Pourquoi `webapp/app.py` n'active-t-il jamais `--share` par défaut, même si Gradio le permettrait en une ligne ?

## 7. Pour aller plus loin

- Remplacer le tableau `numpy` par une vraie base vectorielle (FAISS ou Chroma) et comparer les temps de recherche sur un corpus plus gros.
- Essayer un modèle de génération plus costaud (un Qwen plus grand, Mistral, ou une API comme Claude) et comparer la qualité des réponses.
- **Fait** : deux évolutions ajoutées après un atelier Machine Learnia distinct (RAG sur une franchise de salles de sport fictive) qui utilisait exactement le même schéma (LLM nu → hallucination → RAG → réponse sourcée) — plutôt que dupliquer ce projet, ses deux vrais apports ont été greffés ici :
  - `src/ingestion/chunking.py` — un découpage par fenêtre glissante (taille fixe + chevauchement), alternative au découpage par page de `pdf_loader.py`. Utile dès qu'un document est long et continu, sans repères structurels comme les rubriques du Belvédère.
  - `webapp/app.py` — une interface Gradio par-dessus `answer_with_rag`, avec un lien public optionnel (`--share`, jamais activé par défaut).
