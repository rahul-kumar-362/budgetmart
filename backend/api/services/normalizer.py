"""Product-name and quantity normalisation.

The single source of truth for turning a messy product title like
"Amul Gold Milk 500 ml (Pack of 2)" into a structured quantity we can use to
compute a fair price-per-unit. Used by both the live SerpApi parser and the
demo data generator, so the two paths behave identically.
"""
import re

# Conversion of a unit token -> (kind, factor-to-base). Base units:
#   weight -> grams        volume -> millilitres        count -> pieces
_UNIT_MAP = {
    "kg": ("weight", 1000.0),
    "g": ("weight", 1.0),
    "gm": ("weight", 1.0),
    "gram": ("weight", 1.0),
    "grams": ("weight", 1.0),
    "l": ("volume", 1000.0),
    "litre": ("volume", 1000.0),
    "litres": ("volume", 1000.0),
    "ltr": ("volume", 1000.0),
    "ml": ("volume", 1.0),
    "piece": ("count", 1.0),
    "pieces": ("count", 1.0),
    "pc": ("count", 1.0),
    "pcs": ("count", 1.0),
    "unit": ("count", 1.0),
    "units": ("count", 1.0),
}

_PACK_RE = re.compile(r"(?:pack|set|combo)\s+of\s+(\d+)", re.IGNORECASE)
# Multi-letter units are case-insensitive. Bare "g" is matched lowercase-only so
# marketing tokens like "5G"/"4G" are NOT mistaken for 5 grams. "l"/"L" stays
# case-insensitive because a standalone capital "L" (1L oil) is a real quantity
# and there is no common false-positive token for it.
_QTY_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*"
    r"((?i:kg|gm|grams|gram|litres|litre|ltr|ml|l|pieces|piece|pcs|pc|units|unit)|g)\b"
)


def normalize_product_name(query: str) -> str:
    """Lowercase, collapse whitespace, and standardise a few common phrasings."""
    query = (query or "").lower().strip()
    query = query.replace("1/2 litre", "500ml").replace("half litre", "500ml")
    query = query.replace("1 kg", "1000g")
    return re.sub(r"\s+", " ", query)


def parse_quantity(title: str) -> dict:
    """Extract structured quantity info from a product title.

    Returns a dict with:
      label      -> human string, e.g. "Pack Of 2 | 500 ml"
      pack       -> int multiplier (1 when no pack found)
      kind       -> "weight" | "volume" | "count" | None
      base_total -> total amount in base units (grams / ml / pieces) or None
    """
    title = title or ""
    label_parts: list[str] = []

    pack = 1
    pack_match = _PACK_RE.search(title)
    if pack_match:
        pack = int(pack_match.group(1))
        label_parts.append(f"Pack Of {pack}")

    kind = None
    base_total = None
    qty_match = _QTY_RE.search(title)
    if qty_match:
        magnitude = float(qty_match.group(1))
        unit = qty_match.group(2).lower()
        kind, factor = _UNIT_MAP[unit]
        base_total = magnitude * factor * pack
        label_parts.append(f"{qty_match.group(1)} {unit}")
    elif pack > 1:
        # "Pack of 6" with no per-item size -> treat the pack as a count.
        kind = "count"
        base_total = float(pack)

    return {
        "label": " | ".join(label_parts),
        "pack": pack,
        "kind": kind,
        "base_total": base_total,
    }
