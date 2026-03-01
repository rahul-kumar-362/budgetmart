import sys
from serpapi import GoogleSearch
import json
import urllib.parse as urlparse

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
        
        for item in shopping_results[:3]:
            raw_link = item.get("link", "#")
            clean_link = raw_link
            
            # If it's a Google redirect link, extract the target URL
            if "google.com/url" in raw_link:
                parsed = urlparse.urlparse(raw_link)
                query_params = urlparse.parse_qs(parsed.query)
                if "url" in query_params:
                    clean_link = query_params["url"][0]
                elif "q" in query_params:
                    clean_link = query_params["q"][0]
                    
            print(f"STORE: {item.get('source')}")
            print(f"RAW: {raw_link}")
            print(f"CLEAN: {clean_link}\n")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_serpapi()
