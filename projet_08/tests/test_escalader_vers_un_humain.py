from src.data.database import query
from src.tools.escalader_vers_un_humain import escalader_vers_un_humain


def test_escalates_a_conversation_that_is_not_yet_escalated(conn):
    # Conversation 4 (seed.sql) : client 4, statut 'in_progress' au départ.
    avant = query(conn, "SELECT COUNT(*) AS n FROM support_messages WHERE conversation_id = %s", (4,))

    message = escalader_vers_un_humain(conn, 4, "score de confiance trop bas (0.42)")

    apres = query(conn, "SELECT COUNT(*) AS n FROM support_messages WHERE conversation_id = %s", (4,))
    statut = query(conn, "SELECT status FROM support_conversations WHERE id = %s", (4,))

    assert "transférée" in message
    assert int(apres["n"].iloc[0]) == int(avant["n"].iloc[0]) + 1
    assert statut["status"].iloc[0] == "escalated"


def test_guardrail_blocks_an_already_escalated_conversation(conn):
    # Conversation 5 (seed.sql) : déjà 'escalated' dans les données de seed.
    avant = query(conn, "SELECT COUNT(*) AS n FROM support_messages WHERE conversation_id = %s", (5,))

    message = escalader_vers_un_humain(conn, 5, "nouvelle raison")

    apres = query(conn, "SELECT COUNT(*) AS n FROM support_messages WHERE conversation_id = %s", (5,))

    assert "déjà" in message
    assert int(apres["n"].iloc[0]) == int(avant["n"].iloc[0])  # aucun message ajouté, pas de doublon


def test_unknown_conversation_does_not_crash(conn):
    message = escalader_vers_un_humain(conn, 999999, "raison")

    assert "introuvable" in message
