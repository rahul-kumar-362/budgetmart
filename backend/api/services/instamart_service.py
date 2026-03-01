import asyncio
import random
from .normalizer import get_base_pricing, generate_mock_data

async def fetch_instamart_data(query: str, normalized_query: str) -> dict:
    """
    Simulates async scraping from Swiggy Instamart.
    """
    # Simulate network/scraping delay (0.6s to 1.8s)
    await asyncio.sleep(random.uniform(0.6, 1.8))
    
    base_price = get_base_pricing(normalized_query)
    
    # Instamart has slightly different base pricing dynamics
    data = generate_mock_data(query, "Instamart", base_price, stock_chance=0.85)
    return data
