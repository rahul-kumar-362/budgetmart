from api.services import serp_service


class _FakeSearch:
    """Stand-in for serpapi.GoogleSearch so tests never hit the network."""

    payload: dict = {}

    def __init__(self, params):
        self.params = params

    def get_dict(self):
        return type(self).payload


def _patch(monkeypatch, payload):
    _FakeSearch.payload = payload
    monkeypatch.setattr(serp_service, "GoogleSearch", _FakeSearch)


def test_parses_fields_and_quantity(monkeypatch):
    _patch(
        monkeypatch,
        {
            "shopping_results": [
                {
                    "title": "Amul Milk 500 ml",
                    "extracted_price": 34.0,
                    "source": "BigBasket",
                    "link": "https://bigbasket.com/x",
                    "thumbnail": "https://img/x.jpg",
                    "delivery": "Free delivery",
                },
                {"title": "Amul Gold Milk 1 L", "extracted_price": 60.0, "source": "Store"},
                {"title": "Amul Milk (no price listed)", "source": "X"},
            ]
        },
    )
    out = serp_service.fetch_real_shopping_data("amul milk", api_key="key")
    assert len(out) == 3
    assert out[0]["price"] == 34.0 and out[0]["stock"] is True
    assert out[0]["_quantity"]["base_total"] == 500
    assert out[1]["_quantity"]["base_total"] == 1000  # 1 L -> 1000 ml
    # No price -> out of stock.
    assert out[2]["stock"] is False and out[2]["price"] is None


def test_irrelevant_results_are_filtered(monkeypatch):
    _patch(
        monkeypatch,
        {
            "shopping_results": [
                {"title": "Amul Milk 1 L", "extracted_price": 60, "source": "A"},
                {"title": "Phone charger cable", "extracted_price": 199, "source": "B"},
                {"title": "Amul Taaza 500 ml", "extracted_price": 27, "source": "C"},
            ]
        },
    )
    out = serp_service.fetch_real_shopping_data("amul milk", api_key="key")
    titles = [r["product_name"] for r in out]
    assert "Phone charger cable" not in titles
    assert len(out) == 2


def test_filter_falls_back_when_nothing_matches(monkeypatch):
    # If no title contains a query word, keep the raw list rather than return empty.
    _patch(monkeypatch, {"shopping_results": [{"title": "Generic item", "extracted_price": 10, "source": "X"}]})
    out = serp_service.fetch_real_shopping_data("zzzproduct", api_key="key")
    assert len(out) == 1


def test_no_api_key_returns_empty():
    assert serp_service.fetch_real_shopping_data("milk", api_key="") == []


def test_serpapi_error_returns_empty(monkeypatch):
    _patch(monkeypatch, {"error": "rate limit exceeded"})
    assert serp_service.fetch_real_shopping_data("milk", api_key="key") == []


def test_max_results_is_respected(monkeypatch):
    _patch(monkeypatch, {"shopping_results": [{"title": f"item {i}", "extracted_price": i} for i in range(50)]})
    out = serp_service.fetch_real_shopping_data("x", api_key="key", max_results=5)
    assert len(out) == 5


def test_malicious_title_passes_through_unmodified(monkeypatch):
    # The backend treats titles as DATA; escaping is the frontend's job
    # (it renders via textContent, never innerHTML).
    payload = '<img src=x onerror="alert(1)">'
    _patch(monkeypatch, {"shopping_results": [{"title": payload, "extracted_price": 10, "source": "S"}]})
    out = serp_service.fetch_real_shopping_data("x", api_key="key")
    assert out[0]["product_name"] == payload
