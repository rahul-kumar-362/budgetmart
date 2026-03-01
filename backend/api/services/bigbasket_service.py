import asyncio
import random
from .normalizer import get_base_pricing, generate_mock_data

async def fetch_bigbasket_data(query: str, normalized_query: str) -> dict:
    """
    Simulates async scraping from BigBasket.
    """
    # Simulate network/scraping delay (0.8s to 2.2s)
    await asyncio.sleep(random.uniform(0.8, 2.2))
    
    base_price = get_base_pricing(normalized_query)
    
    # BigBasket might have a slightly different stock chance
    data = generate_mock_data(query, "BigBasket", base_price, stock_chance=0.95)
    return data
