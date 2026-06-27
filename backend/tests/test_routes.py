def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200 and res.get_json()["status"] == "healthy"


def test_home_reports_mode(client):
    data = client.get("/").get_json()
    assert data["project"] == "BudgetMart" and data["mode"] == "demo"


def test_search_demo_mode_shape(client):
    data = client.get("/search?product=amul milk&location=Mumbai").get_json()
    assert data["is_demo"] is True
    assert data["count"] >= 1
    assert isinstance(data["results"], list)
    # Every result carries the pricing-intelligence fields.
    for item in data["results"]:
        assert "unit_price" in item and "savings_vs_max" in item and "is_best_value" in item
    # Exactly one best-value flag.
    assert sum(1 for r in data["results"] if r["is_best_value"]) <= 1


def test_search_requires_product(client):
    assert client.get("/search?product=").status_code == 400
    assert client.get("/search").status_code == 400


def test_search_rejects_overlong_query(client):
    res = client.get("/search?product=" + "x" * 300)
    assert res.status_code == 400


def test_history_disabled_without_database(client):
    res = client.get("/history?product=milk")
    assert res.status_code == 503 and res.get_json()["enabled"] is False
