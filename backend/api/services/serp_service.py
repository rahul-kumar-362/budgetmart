"""Live data source: Google Shopping via SerpApi."""
import logging
import re

from serpapi import GoogleSearch

from api.services.normalizer import parse_quantity

logger = logging.getLogger(__name__)


def _query_tokens(query: str) -> list[str]:
    """Significant words (>=3 chars) from the query, for relevance filtering."""
    return [t for t in re.split(r"[^a-z0-9]+", query.lower()) if len(t) >= 3]


def _is_relevant(title: str, tokens: list[str]) -> bool:
    if not tokens:
        return True
    low = title.lower()
    return any(tok in low for tok in tokens)


def fetch_real_shopping_data(
    query: str,
    location: str = "India",
    api_key: str = "",
    max_results: int = 12,
) -> list[dict]:
    """Fetch live pricing from Google Shopping.

    Returns a list of raw result dicts (each carries an internal ``_quantity``
    used later by the pricing layer). Returns ``[]`` on any error so the caller
    can decide how to degrade.
    """
    if not api_key:
        logger.warning("SerpApi called without an API key")
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "gl": "in",
        "hl": "en",
        "location": location,
    }

    try:
        results = GoogleSearch(params).get_dict()
    except Exception as exc:  # network / quota / parse errors
        logger.error("SerpApi request failed: %s", exc)
        return []

    if results.get("error"):
        logger.error("SerpApi returned error: %s", results["error"])
        return []

    parsed: list[dict] = []
    for item in results.get("shopping_results", []):
        price = item.get("extracted_price")
        title = item.get("title", query)
        quantity = parse_quantity(title)
        parsed.append(
            {
                "platform": item.get("source", "Unknown Store"),
                "product_name": title,
                "quantity": quantity["label"],
                "price": price,
                "delivery": item.get("delivery", "Fees calculated at checkout"),
                "stock": price is not None,
                "product_url": item.get("link") or item.get("product_link") or "#",
                "image_url": item.get("thumbnail", ""),
                "demo": False,
                "_quantity": quantity,
            }
        )

    # Drop loosely-matched junk (titles missing every query word). Fall back to
    # the unfiltered list if the filter would leave us with nothing.
    tokens = _query_tokens(query)
    relevant = [p for p in parsed if _is_relevant(p["product_name"], tokens)]
    chosen = relevant or parsed
    return chosen[:max_results]
