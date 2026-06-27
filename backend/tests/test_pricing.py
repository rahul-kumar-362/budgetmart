from api.services import pricing


def test_unit_price_weight_per_100g():
    up, basis = pricing.unit_price(50, {"kind": "weight", "base_total": 200})
    assert up == 25.0 and basis == "100g"  # 50 / 200g * 100


def test_unit_price_volume_per_litre():
    up, basis = pricing.unit_price(60, {"kind": "volume", "base_total": 500})
    assert up == 120.0 and basis == "L"  # 60 / 500ml * 1000


def test_unit_price_uncomputable():
    assert pricing.unit_price(None, {"kind": "weight", "base_total": 200}) == (None, None)
    assert pricing.unit_price(50, {"kind": None, "base_total": None}) == (None, None)


def test_best_value_uses_unit_price_not_sticker():
    # B is cheaper on the shelf (Rs.30) but worse per gram than A (Rs.10 vs 15 /100g).
    results = [
        {"platform": "A", "price": 50, "stock": True, "_quantity": {"kind": "weight", "base_total": 500}},
        {"platform": "B", "price": 30, "stock": True, "_quantity": {"kind": "weight", "base_total": 200}},
    ]
    summary = pricing.enrich(results)
    assert summary["best_platform"] == "A"
    a = next(r for r in results if r["platform"] == "A")
    b = next(r for r in results if r["platform"] == "B")
    assert a["is_best_value"] is True and b["is_best_value"] is False
    assert a["unit_price"] == 10.0 and b["unit_price"] == 15.0
    assert b["savings_vs_max"] == 20  # vs the most expensive (Rs.50)


def test_internal_quantity_key_is_stripped():
    results = [{"platform": "A", "price": 10, "stock": True, "_quantity": {"kind": "count", "base_total": 1}}]
    pricing.enrich(results)
    assert "_quantity" not in results[0]
