# Projet 04 — RAG & LLM : réécriture pro

Réécriture du notebook `Cahier-Vacances-2026/Projet_04/projet_04.ipynb` en petit projet RAG structuré comme en entreprise. Pour l'explication pédagogique (méthode Feynman), voir [`FEYNMAN.md`](./FEYNMAN.md).

## Pourquoi cette architecture

Un système RAG "pro" sépare toujours quatre étapes qu'un notebook enchaîne dans les mêmes cellules : **ingestion** (extraire le texte des documents), **embeddings** (les transformer en vecteurs), **retrieval** (retrouver les passages pertinents) et **génération** (produire la réponse). Ce découpage — le même que dans des frameworks comme LangChain ou LlamaIndex — permet de remplacer n'importe quelle brique (un autre parseur de documents, une vraie base vectorielle, un LLM plus gros) sans toucher aux autres.

```
Projet_04/
├── data/docs/*.pdf                  # les 5 documents de l'hôtel
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py             # PDF -> DataFrame (source, title, text)
│   │   └── formatter.py              # mise en forme Markdown des rubriques
│   ├── embeddings/
│   │   └── embedder.py               # chargement du modèle d'embedding
│   ├── retrieval/
│   │   └── vector_store.py           # VectorStore : indexe les chunks, recherche par similarité
│   ├── generation/
│   │   ├── prompt.py                 # ROLE, CONSIGNE, build_prompt
│   │   └── llm.py                    # chargement et appel du LLM
│   ├── rag_pipeline.py               # les deux approches : tout dans le prompt vs RAG
│   └── display.py                    # affichage joli question/réponse/sources
├── tests/
│   ├── fakes.py                      # embedder et générateur factices (pas de réseau requis)
│   └── test_*.py                     # ingestion, prompt, recherche vectorielle, pipeline RAG
├── main.py                           # construit l'assistant et répond aux 4 questions du notebook
└── pyproject.toml
```

## Installation et exécution

```bash
cd Projet_04
pip install -e ".[dev]"
python main.py           # nécessite un accès réseau (téléchargement des modèles Hugging Face)
pytest                   # ne nécessite AUCUN accès réseau (voir plus bas)
```

## Comment lire ce code

- **`VectorStore` (retrieval/vector_store.py) ne dépend d'aucun modèle précis.** Il reçoit un `embedder` en paramètre — n'importe quel objet avec une méthode `.encode(textes, normalize_embeddings=True)`. En production, c'est un `SentenceTransformer` ; dans les tests, c'est une doublure. C'est de l'injection de dépendance : ça permet de tester toute la mécanique de recherche sans télécharger de modèle ni avoir de GPU.
- **`tests/fakes.py` contient un `FakeEmbedder` et un `FakeGenerator`.** Le `FakeEmbedder` encode un texte en comptant la présence de quelques mots-clés (pas un vrai embedding sémantique, mais assez pour vérifier que la recherche retrouve bien la bonne rubrique). Le `FakeGenerator` imite l'interface du pipeline `transformers` sans rien télécharger. Résultat : `pytest` tourne entièrement hors-ligne.
- **`src/rag_pipeline.py` expose les deux approches du notebook côte à côte** (`answer_naive` pour l'acte 2, `answer_with_rag` pour l'acte 3), pour qu'on puisse les comparer facilement (temps de réponse, qualité) sans dupliquer la logique de prompt.
- **`src/generation/prompt.py` isole `build_prompt`** dans un module sans aucune dépendance lourde : c'est une simple fonction pure, testée avec une comparaison de chaîne exacte, comme le faisait l'assertion du notebook.
- **`main.py` nécessite un accès réseau** (téléchargement de `Qwen2.5-0.5B-Instruct` et du modèle d'embedding multilingue depuis Hugging Face) : c'est attendu, un vrai système RAG a besoin de ses modèles. Les tests, eux, n'en ont jamais besoin.

## Aller plus loin (idées d'évolution "pro")

- Remplacer `VectorStore` par une vraie base vectorielle (FAISS, Chroma) derrière la même interface `search(question, top_k)`.
- Ajouter un vrai découpage en chunks (chunking) pour des documents plus longs qu'une page.
- Exposer `answer_with_rag` derrière une API (FastAPI) pour brancher un vrai chatbot.
