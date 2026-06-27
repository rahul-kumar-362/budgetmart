"""DEMO MODE orchestrator.

Runs the three sample-data platform generators concurrently. Lets the whole app
run with NO SerpApi key -- so anyone can clone and try it, and so the UI never
shows a hard error when the live quota is exhausted (graceful degradation).
"""
import asyncio

from api.services.normalizer import normalize_product_name
from api.services.platforms import fetch_bigbasket, fetch_blinkit, fetch_instamart


async def _gather(query: str, normalized: str) -> list[dict]:
    results = await asyncio.gather(
        fetch_bigbasket(query, normalized),
        fetch_blinkit(query, normalized),
        fetch_instamart(query, normalized),
        return_exceptions=True,
    )
    return [r for r in results if isinstance(r, dict)]


def fetch_demo_data(query: str, location: str = "India") -> list[dict]:
    """Synchronous entry point (safe to call from a WSGI Flask route)."""
    normalized = normalize_product_name(query)
    return asyncio.run(_gather(query, normalized))
