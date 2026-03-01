import re

def extract_all_quantities(title):
    found = []
    
    # 1. Match packs/sets first
    pack_match = re.search(r'((?:pack|set)\s+of\s+\d+)', title, re.IGNORECASE)
    if pack_match:
        found.append(pack_match.group(1).title())
        
    # 2. Match standard units (weight/volume/pieces)
    weight_match = re.search(r'(\d+(?:\.\d+)?\s*(?:ml|l|litre|litres|g|kg|gm|piece|pieces|pc|pcs|unit|units))\b', title, re.IGNORECASE)
    if weight_match:
        # Don't add 'piece' if 'pack of' is already there to avoid redundancy
        found.append(weight_match.group(1).lower().strip())
        
    return " | ".join(found)

titles = [
    "Amul Dark Chocolate Gable Top 100 Gm",
    "Amul Velvett Milk Chocolate, 150 g | Pack of 2",
    "Amul Milk Chocolate",
    "Apples 500 gm (Set of 6)",
    "2 x 500ml milk"
]

for t in titles:
    print(f"[{extract_all_quantities(t):>20}] | {t}")
