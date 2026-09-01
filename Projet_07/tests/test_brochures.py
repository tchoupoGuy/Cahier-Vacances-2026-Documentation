def test_load_brochures_parses_all_pdfs(brochures):
    assert len(brochures) == 135


def test_brochures_have_expected_columns(brochures):
    assert list(brochures.columns) == ["ville", "hotel", "etoiles", "note", "avis", "prix_nuit", "texte", "resume"]


def test_resume_is_shorter_than_full_text(brochures):
    # Le résumé (présentation + avis) doit être un sous-ensemble du texte complet,
    # donc plus court en moyenne (liste d'équipements et pied de page en moins).
    assert (brochures["resume"].str.len() <= brochures["texte"].str.len()).all()


def test_prices_and_stars_were_extracted(brochures):
    assert brochures["etoiles"].between(1, 5).all()
    assert brochures["prix_nuit"].notna().all()
