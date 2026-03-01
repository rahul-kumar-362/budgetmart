import asyncio
import random
from .normalizer import get_base_pricing, generate_mock_data

async def fetch_blinkit_data(query: str, normalized_query: str) -> dict:
    """
    Simulates async scraping from Blinkit.
    In a real-world scenario, this would use Playwright to navigate,
    wait for selectors, parse DOM, and extract pricing/stock.
    """
    # Simulate network/scraping delay (0.5s to 1.5s)
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    base_price = get_base_pricing(normalized_query)
    
    # Blinkit might be slightly cheaper or expensive
    data = generate_mock_data(query, "Blinkit", base_price, stock_chance=0.9)
    return data
