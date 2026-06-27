"""Pricing intelligence: the part that actually helps a shopper decide.

Two jobs:
  1. price-per-unit  -> compare a 500 ml pack and a 1 L pack fairly
  2. savings         -> "you save Rs.18 (22%) vs the most expensive option"

We pick the BEST VALUE by lowest price-per-unit (not lowest sticker price),
falling back to sticker price only when no quantity could be parsed.
"""
from typing import Optional

# How each measurement kind is presented to the user.
_BASIS = {
    "weight": (100.0, "100g"),   # Rs. per 100 g
    "volume": (1000.0, "L"),     # Rs. per litre
    "count": (1.0, "unit"),      # Rs. per piece
}


def unit_price(price: Optional[float], quantity: dict) -> tuple[Optional[float], Optional[str]]:
    """Return (price_per_basis, basis_label) or (None, None) if not computable."""
    if not price or price <= 0:
        return None, None
    kind = quantity.get("kind")
    base_total = quantity.get("base_total")
    if not kind or not base_total or base_total <= 0:
        return None, None
    multiplier, label = _BASIS[kind]
    return round(price / base_total * multiplier, 2), label


def enrich(results: list[dict]) -> dict:
    """Annotate each result with unit price + savings and flag the best value.

    Mutates and returns a summary dict. Each item gains:
      unit_price, unit_basis, savings_vs_max, savings_pct, is_best_value
    """
    for item in results:
        up, basis = unit_price(item.get("price"), item.get("_quantity", {}))
        item["unit_price"] = up
        item["unit_basis"] = basis

    in_stock = [r for r in results if r.get("stock") and r.get("price")]

    # Best value: lowest unit price if we have any; else lowest sticker price.
    best = None
    priced_by_unit = [r for r in in_stock if r.get("unit_price") is not None]
    pool = priced_by_unit or in_stock
    if pool:
        key = "unit_price" if priced_by_unit else "price"
        best = min(pool, key=lambda r: r[key])

    # Savings are measured against the most expensive in-stock option.
    max_price = max((r["price"] for r in in_stock), default=None)
    for item in results:
        item["is_best_value"] = item is best
        if item.get("stock") and item.get("price") and max_price and max_price > 0:
            saving = round(max_price - item["price"], 2)
            item["savings_vs_max"] = saving
            item["savings_pct"] = round(saving / max_price * 100)
        else:
            item["savings_vs_max"] = None
            item["savings_pct"] = None
        item.pop("_quantity", None)  # internal helper, not part of the API

    return {
        "count": len(results),
        "in_stock_count": len(in_stock),
        "best_platform": best.get("platform") if best else None,
        "cheapest_price": best.get("price") if best else None,
        "cheapest_unit_price": best.get("unit_price") if best else None,
        "cheapest_unit_basis": best.get("unit_basis") if best else None,
    }
