"""Local development server.

Run from the backend/ directory:   python run.py
(For production, Vercel imports ``app`` from api/index.py instead.)
"""
from api.index import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
