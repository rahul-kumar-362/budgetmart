# 🛒 BudgetMart

**Real-time grocery price comparison for India — ranked by true price-per-unit, not just the sticker price.**

Search a product (e.g. *Amul Milk*) and BudgetMart shows live offers from across
Google Shopping, normalises each to a fair **price per 100 g / per litre / per
unit**, highlights the best *value*, and tells you how much you save versus the
priciest option.

> Runs out of the box with **zero setup** — no API key, no database, no Redis.
> With nothing configured it serves clearly-labelled **sample data (demo mode)**;
> add a SerpApi key for live prices.

---

## ✨ Features

- **Live prices** from Google Shopping via SerpApi (`google_shopping` engine).
- **Price-per-unit intelligence** — compares a 500 ml pack and a 1 L pack fairly.
- **Savings indicator** — "Save ₹18 (22%) vs priciest".
- **Demo mode** — runs with no API key; great for cloning, screenshots, demos.
- **Graceful degradation** — if the live quota is exhausted, falls back to sample data instead of a hard error.
- **Price history** (optional) — set `DATABASE_URL` to record snapshots and expose `/history`.
- **Persistent caching** — Redis (e.g. Upstash) in production, in-memory locally.
- **Hardened** — CORS allowlist, per-IP rate limiting, input validation, XSS-safe rendering.

## 🧱 Tech stack

| Layer    | Choice |
|----------|--------|
| Frontend | TypeScript (no framework), compiled with `tsc` to a single dependency-free script |
| Backend  | Python + Flask (application-factory pattern) |
| Data     | SerpApi (live) · async sample-data generators (demo) |
| Cache    | Flask-Caching — Redis in prod, SimpleCache locally |
| DB       | SQLAlchemy — Postgres in prod, SQLite locally (optional) |
| Limits   | Flask-Limiter |
| Deploy   | Vercel serverless (`@vercel/python`) |
| CI       | GitHub Actions — pytest + TypeScript typecheck |

## 🗂️ Architecture

```
frontend/                 static site (TypeScript -> dist/main.js)
  src/main.ts             all UI logic, type-safe, XSS-safe (textContent)
  index.html  style.css
  dist/main.js            committed build output (no bundler needed)

backend/
  api/index.py            Vercel entry: app = create_app()
  api/app_factory.py      builds + wires the Flask app
  api/config.py           all settings from env vars (safe defaults)
  api/extensions.py       cache / cors / db / limiter singletons
  api/routes.py           /  /health  /search  /history
  api/models.py           PriceSnapshot (price history)
  api/services/
    serp_service.py       live Google Shopping fetch + parse
    demo_service.py       runs the 3 platform mocks concurrently (asyncio.gather)
    platforms.py          BigBasket / Blinkit / Instamart sample generators
    normalizer.py         quantity parsing (single source of truth)
    pricing.py            price-per-unit + savings + best-value
  tests/                  pytest suite
```

**Request flow:** browser → `GET /search?product=&location=` → validate → cache
lookup → SerpApi (or demo) → `pricing.enrich()` adds unit price + savings → cache
the success → (optionally persist a snapshot) → JSON → client renders cards.

## 🚀 Run locally

### Backend
```bash
cd backend
python -m venv ../.venv
../.venv/Scripts/activate        # Windows  (source ../.venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python run.py                    # http://127.0.0.1:5000  (demo mode if no key)
```

### Frontend
```bash
cd frontend
npm install
npm run build                    # compiles src/ -> dist/main.js
# then open index.html (or serve with any static server / VS Code Live Server)
```

## 🔑 Configuration

All optional — copy `.env.example` to `backend/.env` and set what you need:

| Variable          | Effect |
|-------------------|--------|
| `SERPAPI_KEY`     | enables live prices (else demo mode) |
| `REDIS_URL`       | persistent cache (e.g. Upstash) instead of in-memory |
| `DATABASE_URL`    | enables price history + `/history` |
| `ALLOWED_ORIGINS` | CORS allowlist (default `*`) |
| `RATELIMIT_SEARCH`| per-IP search cap (default `20 per minute`) |
| `DEMO_MODE`       | force sample data even with a key |

## 🌐 API

| Endpoint | Description |
|----------|-------------|
| `GET /`        | status + active mode |
| `GET /health`  | health check |
| `GET /search?product=&location=` | compared offers with unit price + savings |
| `GET /history?product=` | price snapshots over time (needs `DATABASE_URL`) |

## ✅ Tests

```bash
cd backend && pytest          # 24 tests: normalizer, pricing, parsing, routes
cd frontend && npm run typecheck
```

## ☁️ Deploy

See [`DEPLOYMENT.md`](DEPLOYMENT.md). Backend and frontend deploy as two Vercel
projects from this repo (root dirs `backend/` and `frontend/`).
