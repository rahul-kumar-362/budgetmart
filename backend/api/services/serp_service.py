from serpapi import GoogleSearch
import asyncio
import re
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY", "")

def fetch_real_shopping_data(query: str, location: str = "India") -> list[dict]:
    """
    Fetches real-time pricing and availability from Google Shopping using SerpApi.
    Supports a location string (e.g. "Mumbai", "110001", "India").
    """
    params = {
      "engine": "google_shopping",
      "q": query,
      "api_key": API_KEY,
      "gl": "in",
      "hl": "en",
      "location": location,
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        shopping_results = results.get("shopping_results", [])

        
        parsed_data = []
        for item in shopping_results[:12]:  # Limit to top 12 results
            # Extract numbers from price if necessary, though extracted_price gives floats
            price = item.get("extracted_price")
            source = item.get("source", "Unknown Store")
            
            # Simple stock logic: if there's a price, it's generally in stock, unless explicitly stated otherwise
            # SerpApi doesn't always expose direct "OOS" unless in delivery text. We assume True.
            
            # Use direct merchant link if available, fallback to google shopping product link
            product_url = item.get("link") or item.get("product_link") or "#"
            
            # Extract quantity
            raw_title = item.get("title", query)
            found_qty = []
            
            # Match packs/sets first
            pack_match = re.search(r'((?:pack|set)\s+of\s+\d+)', raw_title, re.IGNORECASE)
            if pack_match:
                found_qty.append(pack_match.group(1).title())
                
            # Match standard units (weight/volume/pieces)
            weight_match = re.search(r'(\d+(?:\.\d+)?\s*(?:ml|l|litre|litres|g|kg|gm|piece|pieces|pc|pcs|unit|units))\b', raw_title, re.IGNORECASE)
            if weight_match:
                found_qty.append(weight_match.group(1).lower().strip())
                
            quantity_str = " | ".join(found_qty)
            
            parsed_data.append({
                "platform": source,
                "product_name": raw_title,
                "quantity": quantity_str,
                "price": price,
                "delivery": item.get("delivery", "Fees calculated at checkout"),
                "stock": True if price else False,
                "product_url": product_url,
                "image_url": item.get("thumbnail", "")
            })
            
        return parsed_data
    except Exception as e:
        print(f"SerpApi Error: {e}")
        return []
