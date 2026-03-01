import sys
from serpapi import GoogleSearch
import json

def test_serpapi():
    params = {
      "engine": "google_shopping",
      "q": "Amul Milk",
      "api_key": "0f91d9e6d9f61409ef5b5ebf23dda580ad4f4feaed63e3ed5252590164228995",
      "gl": "in",
      "hl": "en",
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        shopping_results = results.get("shopping_results", [])
        
        if shopping_results:
            print(json.dumps(shopping_results[0], indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_serpapi()
