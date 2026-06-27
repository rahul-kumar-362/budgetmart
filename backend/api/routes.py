"""HTTP routes. Thin layer: validate input, pick a data source, enrich, cache."""
import logging

from flask import Blueprint, jsonify, request

from api.config import Config
from api.extensions import cache, db, limiter
from api.services import pricing
from api.services.demo_service import fetch_demo_data
from api.services.serp_service import fetch_real_shopping_data

logger = logging.getLogger(__name__)
bp = Blueprint("api", __name__)
config = Config()


@bp.route("/")
def home():
    return jsonify(
        {
            "project": "BudgetMart",
            "status": "ok",
            "mode": "live" if config.live_enabled else "demo",
            "history_enabled": config.database_enabled,
            "endpoints": ["/health", "/search?product=&location=", "/history?product="],
        }
    )


@bp.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@bp.route("/search")
@limiter.limit(config.RATELIMIT_SEARCH)
def search():
    query = (request.args.get("product", "") or "").strip()
    location = (request.args.get("location", "India") or "").strip() or "India"

    if not query:
        return jsonify({"error": "Please provide a search product"}), 400
    if len(query) > config.MAX_QUERY_LEN:
        return jsonify({"error": f"Query too long (max {config.MAX_QUERY_LEN} characters)"}), 400
    location = location[: config.MAX_LOCATION_LEN]

    use_live = config.live_enabled
    cache_key = f"{'live' if use_live else 'demo'}:{query.lower()}:{location.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify({**cached, "cached": True})

    mode = "demo"
    results: list[dict] = []
    if use_live:
        results = fetch_real_shopping_data(
            query, location, api_key=config.SERPAPI_KEY, max_results=config.MAX_RESULTS
        )
        mode = "live"
        if not results:
            # Graceful degradation: a quota/outage shows sample data, not a dead end.
            logger.info("Live fetch empty for %r, falling back to demo data", query)
            results = fetch_demo_data(query, location)
            mode = "demo-fallback"
    else:
        results = fetch_demo_data(query, location)

    if not results:
        return jsonify({"error": "No matching product found"}), 404

    summary = pricing.enrich(results)
    payload = {
        "query": query,
        "location": location,
        "mode": mode,
        "is_demo": mode != "live",
        "results": results,
        "cached": False,
        **summary,
    }

    # Only successful, non-empty responses are cached -- never an error.
    cache.set(cache_key, payload, timeout=config.CACHE_DEFAULT_TIMEOUT)
    _persist(query, results)
    return jsonify(payload)


@bp.route("/history")
def history():
    if not config.database_enabled:
        return (
            jsonify({"enabled": False, "error": "Price history disabled (set DATABASE_URL)"}),
            503,
        )
    product = (request.args.get("product", "") or "").strip().lower()
    if not product:
        return jsonify({"error": "Please provide a product"}), 400

    from api.models import PriceSnapshot

    rows = (
        PriceSnapshot.query.filter_by(search_query=product)
        .order_by(PriceSnapshot.captured_at.asc())
        .limit(500)
        .all()
    )
    series: dict[str, list] = {}
    for row in rows:
        series.setdefault(row.platform, []).append(
            {
                "captured_at": row.captured_at.isoformat() if row.captured_at else None,
                "price": row.price,
                "unit_price": row.unit_price,
            }
        )
    return jsonify({"product": product, "enabled": True, "points": len(rows), "series": series})


def _persist(query: str, results: list[dict]) -> None:
    """Best-effort price-history write. Never breaks a search if the DB is down."""
    if not config.database_enabled:
        return
    try:
        from api.models import PriceSnapshot

        db.session.add_all(
            PriceSnapshot(
                search_query=query.lower(),
                platform=r.get("platform", "Unknown"),
                product_name=r.get("product_name"),
                price=r.get("price"),
                unit_price=r.get("unit_price"),
                unit_basis=r.get("unit_basis"),
                in_stock=bool(r.get("stock")),
            )
            for r in results
        )
        db.session.commit()
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        logger.error("Failed to persist price snapshots: %s", exc)
