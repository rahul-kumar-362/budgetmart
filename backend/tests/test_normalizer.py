from api.services.normalizer import normalize_product_name, parse_quantity


def test_weight_kg_to_grams():
    assert parse_quantity("Aashirvaad Atta 1 kg")["base_total"] == 1000


def test_volume_ml():
    q = parse_quantity("Amul Milk 500 ml")
    assert q["base_total"] == 500 and q["kind"] == "volume"


def test_volume_capital_litre():
    # "1L" oil must still parse as a litre.
    assert parse_quantity("Fortune Oil 1L")["base_total"] == 1000


def test_pack_of_counts_as_units():
    q = parse_quantity("Eggs Pack of 6")
    assert q["pack"] == 6 and q["kind"] == "count" and q["base_total"] == 6


def test_pack_multiplies_weight():
    q = parse_quantity("Lays Chips 50g Pack of 4")
    assert q["kind"] == "weight" and q["base_total"] == 200


def test_5g_phone_is_not_5_grams():
    # Regression: marketing token "5G" must not be read as a weight.
    assert parse_quantity("Samsung Galaxy 5G")["base_total"] is None


def test_label_contains_pack_and_size():
    label = parse_quantity("Milk 500 ml Pack of 2")["label"]
    assert "Pack Of 2" in label and "500 ml" in label


def test_normalize_collapses_whitespace_and_case():
    assert normalize_product_name("  Amul   MILK ") == "amul milk"
