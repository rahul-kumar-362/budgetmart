import re
import json
from serpapi import GoogleSearch

def extract_quantity(title):
    # Enhanced regex to capture multipacks and various units
    patterns = [
        r'(\d+\s*(?:x|\*)\s*\d+(?:\.\d+)?\s*(?:ml|l|litre|litres|g|kg|gm|piece|pieces|pc|pcs|pack|pk|unit|units))\b', # e.g. 2 x 500ml
        r'((?:pack of|set of)\s*\d+.*)', # e.g. Pack of 4
        r'(\d+(?:\.\d+)?\s*(?:ml|l|litre|litres|g|kg|gm|piece|pieces|pc|pcs|pack|pk|unit|units))\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""

def test_serpapi_choc():
    params = {
      "engine": "google_shopping",
      "q": "amul chocolate",
      "api_key": "0f91d9e6d9f61409ef5b5ebf23dda580ad4f4feaed63e3ed5252590164228995",
      "gl": "in",
      "hl": "en",
      "location": "411062"
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    shopping_results = results.get("shopping_results", [])
    
    for item in shopping_results[:10]:
        title = item.get("title", "")
        print(f"[{extract_quantity(title):>15}] | {title}")

if __name__ == "__main__":
    test_serpapi_choc()
