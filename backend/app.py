from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache

from services.serp_service import fetch_real_shopping_data

app = Flask(__name__)
CORS(app)   # allows frontend to talk to backend

# Cache configuration (5 minutes TTL for search results to avoid hitting SerpApi limits quickly)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

@app.route("/")
def home():
    return jsonify({
        "project": "BudgetMart",
        "status": "Backend Running Successfully 🚀 (SerpApi Enabled)"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

# SEARCH API
@app.route("/search")
@cache.cached(query_string=True)
async def search():
    query = request.args.get("product", "").strip()
    location = request.args.get("location", "India").strip()
    
    if not query:
        return jsonify({"error": "Please provide a search product"}), 400
        
    print(f"Fetching real-time Google Shopping data for: {query} in {location}")
    
    # Execute the unified SerpApi fetch
    results = await fetch_real_shopping_data(query, location)
            
    if not results:
        return jsonify({"error": "No matching product found or rate limit blocked"}), 404

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=5000)