import sys
from serpapi import GoogleSearch

def test_serpapi_location():
    params = {
      "engine": "google_shopping",
      "q": "amul chocolate",
      "api_key": "0f91d9e6d9f61409ef5b5ebf23dda580ad4f4feaed63e3ed5252590164228995",
      "gl": "in",
      "hl": "en",
      "location": "411062"
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        shopping_results = results.get("shopping_results", [])
        print(f"Found {len(shopping_results)} items.")
        if "error" in results:
            print("API Error:", results["error"])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_serpapi_location()
