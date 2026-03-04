# BudgetMart

Real-time grocery price comparison aggregator for the Indian market. Search for any product and instantly compare prices across multiple online grocery platforms.

## Features

- **Real-time price comparison** — Fetches live prices from Google Shopping via SerpAPI
- **Location-aware search** — Filter results by city or zip code
- **Best price highlight** — The cheapest in-stock item is automatically highlighted
- **Sort options** — Sort by price (low to high) or availability
- **Stock status** — Out-of-stock items are visually distinguished
- **Quantity extraction** — Automatically parses pack sizes, weights, and volumes from product titles
- **Responsive design** — Works on desktop and mobile

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python, Flask, Flask-CORS, Flask-Caching |
| Data Source | [SerpAPI](https://serpapi.com/) (Google Shopping) |
| Hosting | [Vercel](https://vercel.com/) |

## Prerequisites

- Python 3.8+
- A [SerpAPI](https://serpapi.com/) API key (free tier available)

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/rahul-kumar-362/budgetmart.git
cd budgetmart
```

### 2. Set up the backend

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the `backend/` directory:

```
SERPAPI_KEY=your_serpapi_key_here
```

### 4. Start the backend

```bash
python backend/api/index.py
```

The server starts at `http://127.0.0.1:5000`.

### 5. Open the frontend

Open `frontend/index.html` in your browser. The frontend automatically detects `localhost` and connects to the local backend.

## API Endpoints

### `GET /`

Returns project status.

```json
{
  "project": "BudgetMart",
  "status": "Backend Running Successfully (SerpApi Enabled)"
}
```

### `GET /health`

Health check endpoint. Returns `200 OK`.

### `GET /search`

Search for grocery products.

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `product` | Yes | — | Product name to search (e.g., "Amul Milk") |
| `location` | No | `India` | City name or zip code (e.g., "Mumbai", "110001") |

**Example:**

```
GET /search?product=Amul+Milk&location=Mumbai
```

**Response:**

```json
[
  {
    "platform": "BigBasket",
    "product_name": "Amul Taaza Toned Fresh Milk 500 ml",
    "quantity": "500 ml",
    "price": 29,
    "delivery": "Free delivery",
    "stock": true,
    "product_url": "https://...",
    "image_url": "https://..."
  }
]
```

Results are cached for 5 minutes to reduce API usage.

## Project Structure

```
budgetmart/
├── frontend/
│   ├── index.html          # Main page
│   ├── script.js           # Search logic, API calls, card rendering
│   └── style.css           # Glassmorphism dark theme
├── backend/
│   ├── api/
│   │   ├── index.py        # Flask app with /search and /health routes
│   │   └── services/
│   │       ├── serp_service.py     # SerpAPI Google Shopping integration
│   │       └── normalizer.py       # Product name normalization
│   ├── requirements.txt
│   └── vercel.json         # Vercel deployment config
├── DEPLOYMENT.md           # Step-by-step Vercel deployment guide
└── start_app.cmd           # Windows startup script
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions on deploying to Vercel.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.
