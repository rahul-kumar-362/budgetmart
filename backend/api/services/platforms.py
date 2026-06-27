"""Per-platform sample-data generators used by DEMO MODE.

These are intentionally async: each simulates the latency of scraping a real
storefront. demo_service runs all three concurrently with asyncio.gather, so
total time is the slowest single call (~1s) rather than their sum (~3s) -- the
exact pattern a real Playwright-based scraper would use.

Data here is clearly flagged ``"demo": True`` so the UI can label it as sample
data and never pass it off as a live price.
"""
import asyncio
import random

from api.services.normalizer import parse_quantity

# A small catalogue of believable base prices (Rupees) for common groceries.
_BASE_PRICES = {
    "milk": 33, "amul milk": 33, "bread": 40, "butter": 58, "eggs": 70,
    "coffee": 180, "nescafe": 220, "maggi": 14, "rice": 65, "basmati rice": 130,
    "flour": 45, "atta": 45, "sugar": 45, "salt": 25, "chips": 20, "lays": 20,
    "coke": 40, "pepsi": 38, "oil": 140, "tea": 120, "paneer": 95,
}

# Default pack size shown per platform so price-per-unit has something to chew on.
_DEFAULT_QTY = {"milk": "500 ml", "oil": "1 L", "rice": "1 kg", "atta": "1 kg"}


def _base_price(normalized: str) -> int:
    if normalized in _BASE_PRICES:
        return _BASE_PRICES[normalized]
    for key, price in _BASE_PRICES.items():
        if key in normalized:
            return price
    return random.randint(30, 220)


def _guess_qty(normalized: str) -> str:
    for key, qty in _DEFAULT_QTY.items():
        if key in normalized:
            return qty
    return "500 g"


def _make_item(query: str, normalized: str, platform: str, spread: float, stock_chance: float) -> dict:
    qty_str = _guess_qty(normalized)
    in_stock = random.random() < stock_chance
    base = _base_price(normalized)
    price = round(base * (1 + random.uniform(-spread, spread)))
    name = f"{query.title()} {qty_str}"
    quantity = parse_quantity(name)
    return {
        "platform": platform,
        "product_name": name,
        "quantity": quantity["label"],
        "price": price if in_stock else None,
        "delivery": "Free delivery" if random.random() < 0.5 else "Delivery in 15 min",
        "stock": in_stock,
        "product_url": f"https://www.{platform.lower().replace(' ', '')}.com/search?q={query.replace(' ', '+')}",
        "image_url": "",
        "demo": True,
        "_quantity": quantity,
    }


async def fetch_bigbasket(query: str, normalized: str) -> dict:
    await asyncio.sleep(random.uniform(0.3, 1.0))
    return _make_item(query, normalized, "BigBasket", spread=0.06, stock_chance=0.95)


async def fetch_blinkit(query: str, normalized: str) -> dict:
    await asyncio.sleep(random.uniform(0.2, 0.8))
    return _make_item(query, normalized, "Blinkit", spread=0.10, stock_chance=0.90)


async def fetch_instamart(query: str, normalized: str) -> dict:
    await asyncio.sleep(random.uniform(0.3, 0.9))
    return _make_item(query, normalized, "Swiggy Instamart", spread=0.08, stock_chance=0.85)
