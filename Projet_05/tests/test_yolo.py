from src.data.yolo import SPECIES, dominant_species, read_yolo_boxes


def test_read_yolo_boxes_converts_fractions_to_pixels(tmp_path):
    label_path = tmp_path / "photo.txt"
    # classe 4 (GoldFish), boîte centrée au milieu de l'image, moitié de sa taille
    label_path.write_text("4 0.5 0.5 0.5 0.5\n")

    boxes, labels = read_yolo_boxes(str(label_path), width=100, height=200)

    assert labels == [4]
    assert boxes == [[25.0, 50.0, 75.0, 150.0]]


def test_read_yolo_boxes_ignores_lines_with_wrong_field_count(tmp_path):
    label_path = tmp_path / "photo.txt"
    # la 2e ligne n'a pas 5 champs (classe + 4 coordonnées) : elle doit être ignorée
    label_path.write_text("4 0.5 0.5 0.5 0.5\nligne malformee\n")

    boxes, labels = read_yolo_boxes(str(label_path), width=100, height=100)

    assert len(boxes) == 1
    assert len(labels) == 1


def test_dominant_species_picks_most_frequent_class(tmp_path):
    label_path = tmp_path / "photo.txt"
    # deux ClownFish (classe 3) et un GoldFish (classe 4) : ClownFish domine
    label_path.write_text(
        "3 0.1 0.1 0.1 0.1\n"
        "3 0.2 0.2 0.1 0.1\n"
        "4 0.3 0.3 0.1 0.1\n"
    )

    assert dominant_species(str(label_path)) == "ClownFish"
    assert SPECIES[3] == "ClownFish"


def test_dominant_species_returns_none_for_empty_file(tmp_path):
    label_path = tmp_path / "empty.txt"
    label_path.write_text("")

    assert dominant_species(str(label_path)) is None
