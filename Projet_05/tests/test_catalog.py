from src.data.catalog import build_fish_dataframe, list_images


def _make_split(root, split, images_and_labels):
    """Crée une arborescence dataset_dir/split/{images,labels}/... minimale."""
    images_dir = root / split / "images"
    labels_dir = root / split / "labels"
    images_dir.mkdir(parents=True)
    labels_dir.mkdir(parents=True)
    for name, label_content in images_and_labels:
        (images_dir / f"{name}.jpg").write_bytes(b"")  # contenu factice, jamais lu ici
        if label_content is not None:
            (labels_dir / f"{name}.txt").write_text(label_content)


def test_list_images_lists_all_files_in_split(tmp_path):
    _make_split(tmp_path, "train", [("a", "4 0.5 0.5 0.2 0.2\n"), ("b", "3 0.5 0.5 0.2 0.2\n")])

    images = list_images(str(tmp_path), "train")

    assert len(images) == 2
    assert all(p.endswith(".jpg") for p in images)


def test_build_fish_dataframe_skips_images_without_labels(tmp_path):
    _make_split(
        tmp_path, "train",
        [("with_label", "4 0.5 0.5 0.2 0.2\n"), ("without_label", None)],
    )
    _make_split(tmp_path, "valid", [])
    _make_split(tmp_path, "test", [])

    df = build_fish_dataframe(str(tmp_path))

    assert len(df) == 1
    assert df.iloc[0]["species"] == "GoldFish"
    assert df.iloc[0]["split"] == "train"
