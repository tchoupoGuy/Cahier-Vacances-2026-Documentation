from src.generation.prompt import CONSIGNE, ROLE, build_prompt


def test_build_prompt_matches_expected_template():
    context = "## Piscine\n\nLa piscine est ouverte de 8h à 20h."
    question = "La piscine est-elle chauffée ?"

    prompt = build_prompt(context, question)

    expected = f"{ROLE}\n\n{context}\n\nQuestion d'un client : {question}\n{CONSIGNE}"
    assert prompt == expected
