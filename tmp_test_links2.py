import json
from serpapi import GoogleSearch

def test_serpapi_delivery():
    params = {
      "engine": "google_shopping",
      "q": "Amul Milk",
      "api_key": "0f91d9e6d9f61409ef5b5ebf23dda580ad4f4feaed63e3ed5252590164228995",
      "gl": "in",
      "hl": "en",
      "location": "411062"
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    shopping_results = results.get("shopping_results", [])
    
    for item in shopping_results[:3]:
        print("title:", item.get("title"))
        print("price:", item.get("price"))
        print("delivery:", item.get("delivery"))
        print("---")

if __name__ == "__main__":
    test_serpapi_delivery()
