import re

def normalize_product_name(query: str) -> str:
    """
    Normalizes a product name by lowercasing, stripping extra whitespace,
    and removing common filler words or standardizing units.
    """
    query = query.lower().strip()
    # Replace common variations
    query = query.replace("1/2 litre", "500ml")
    query = query.replace("half litre", "500ml")
    query = query.replace("1 kg", "1000g")
    
    # Remove extra spaces
    query = re.sub(r'\s+', ' ', query)
    
    return query

def generate_mock_data(query: str, platform_name: str, base_price: float, stock_chance: float = 0.9) -> dict:
    """
    Generates realistic mock data for the given platform.
    """
    import random
    
    # Simulate an Out of Stock scenario
    is_in_stock = random.random() < stock_chance
    
    # Introduce small price variations between platforms (+/- 10%)
    price_variation = base_price * random.uniform(-0.1, 0.1)
    final_price = round(base_price + price_variation)
    
    return {
        "platform": platform_name,
        "product_name": query.title(),
        "price": final_price if is_in_stock else None,
        "stock": is_in_stock,
        "product_url": f"https://www.{platform_name.lower()}.com/search?q={query.replace(' ', '+')}"
    }

def get_base_pricing(normalized_query: str) -> float:
    """
    Determine a basic authentic fake base price based on item keywords.
    """
    db = {
        "milk": 30,
        "amul milk": 33,
        "bread": 40,
        "britannia bread": 45,
        "butter": 55,
        "amul butter": 60,
        "eggs": 70,
        "coffee": 150,
        "nescafe": 200,
        "maggi": 14,
        "yippee": 12,
        "rice": 60,
        "basmati rice": 120,
        "flour": 40,
        "sugar": 45,
        "salt": 25,
        "tata salt": 28,
        "chips": 20,
        "lays": 20,
        "kurkure": 20,
        "coke": 40,
        "pepsi": 38
    }
    
    # Try exact match
    if normalized_query in db:
        return db[normalized_query]
        
    # Try partial match
    for key, price in db.items():
        if key in normalized_query:
            return price
            
    # Default base price for an unknown item
    import random
    return random.randint(30, 250)
