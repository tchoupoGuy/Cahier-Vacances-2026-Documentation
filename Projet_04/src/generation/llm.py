"""Chargement et appel du modèle de génération de texte."""

from __future__ import annotations

GENERATION_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"


def load_generator(model_name: str = GENERATION_MODEL):
    """Charge un pipeline de génération de texte Hugging Face.

    Import local (comme dans embedder.py) : le reste du package n'a pas
    besoin de `transformers` pour être testé.
    """
    import transformers
    from transformers import pipeline

    transformers.logging.set_verbosity_error()
    return pipeline("text-generation", model=model_name)


def ask_llm(generator, prompt: str, max_new_tokens: int = 80) -> str:
    """Envoie un message brut au LLM (mode chat) et renvoie sa réponse."""
    conversation = generator(
        [{"role": "user", "content": prompt}], max_new_tokens=max_new_tokens, do_sample=False
    )
    return conversation[0]["generated_text"][-1]["content"]


def generate_from_prompt(generator, prompt: str, max_length: int = 200) -> str:
    """Génère une réponse à partir d'un prompt texte déjà assemblé (rôle + contexte + question)."""
    return generator(prompt, max_length=max_length)[0]["generated_text"]
