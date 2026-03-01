import re

def extract_quantity(title):
    # Regex to find quantity patterns like 500ml, 1 kg, 200 g, 1L, etc.
    # Matches a number (with optional decimal), optional space, and a unit.
    pattern = r'(\d+(?:\.\d+)?\s*(?:ml|l|litre|litres|g|kg|gm|piece|pieces|pc|pcs|pack|pk|unit|units))\b'
    match = re.search(pattern, title, re.IGNORECASE)
    if match:
        return match.group(1).lower().strip()
    return "1 Unit" # Fallback

titles = [
    "Amul Milk 500 ml",
    "Britannia Good Day 600g",
    "Onion 1kg",
    "Amul Slim N Trim Skimmed Milk",
    "Fortune Refined Soyabean Oil 1 Litre",
    "Eggs 6 pieces",
    "Apples 500 gm",
    "Coca Cola 2.25L"
]

for t in titles:
    print(f"{t} -> {extract_quantity(t)}")
