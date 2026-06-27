"""Central configuration, loaded entirely from environment variables.

Everything optional has a safe local-dev default, so the app boots with ZERO
external services (no Redis, no database, no SerpApi key). Flip features on in
production by setting the matching environment variable in the Vercel dashboard.
"""
import os

from dotenv import load_dotenv

# Load a local .env during development. In production (Vercel) the variables are
# injected by the platform, so a missing .env file is fine.
load_dotenv()


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    # --- SerpApi (live data) -------------------------------------------------
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()

    # --- Cache ---------------------------------------------------------------
    # Use Redis (e.g. Upstash) when REDIS_URL is set, otherwise fall back to an
    # in-process dict. SimpleCache is fine locally but does NOT persist across
    # Vercel cold starts, which is exactly why we prefer Redis in production.
    CACHE_REDIS_URL = (os.getenv("REDIS_URL") or os.getenv("CACHE_REDIS_URL") or "").strip()
    CACHE_TYPE = "RedisCache" if CACHE_REDIS_URL else "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

    # --- Database (optional: enables price history) --------------------------
    # Local dev:  sqlite:///budgetmart.db   Production: postgresql://...
    # If unset, history is simply disabled and search still works.
    DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- CORS ----------------------------------------------------------------
    # Comma-separated allowlist. Defaults to "*" for easy local dev; lock this
    # down to your frontend origin in production.
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").strip()

    # --- Rate limiting -------------------------------------------------------
    # Protects the limited SerpApi quota from a single abusive client.
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "60 per hour")
    RATELIMIT_SEARCH = os.getenv("RATELIMIT_SEARCH", "20 per minute")
    RATELIMIT_STORAGE_URI = CACHE_REDIS_URL or "memory://"

    # --- Behaviour knobs -----------------------------------------------------
    MAX_QUERY_LEN = int(os.getenv("MAX_QUERY_LEN", "100"))
    MAX_LOCATION_LEN = int(os.getenv("MAX_LOCATION_LEN", "80"))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", "12"))

    # Force sample data even if a key exists (handy for demos/screenshots).
    DEMO_MODE_FORCED = _as_bool(os.getenv("DEMO_MODE", ""))

    @property
    def database_enabled(self) -> bool:
        return bool(self.DATABASE_URL)

    @property
    def live_enabled(self) -> bool:
        """True when we have a key AND demo mode isn't forced."""
        return bool(self.SERPAPI_KEY) and not self.DEMO_MODE_FORCED

    def as_flask_config(self) -> dict:
        cfg = {
            "CACHE_TYPE": self.CACHE_TYPE,
            "CACHE_DEFAULT_TIMEOUT": self.CACHE_DEFAULT_TIMEOUT,
            "SQLALCHEMY_TRACK_MODIFICATIONS": self.SQLALCHEMY_TRACK_MODIFICATIONS,
            "RATELIMIT_DEFAULT": self.RATELIMIT_DEFAULT,
            "RATELIMIT_STORAGE_URI": self.RATELIMIT_STORAGE_URI,
        }
        if self.CACHE_REDIS_URL:
            cfg["CACHE_REDIS_URL"] = self.CACHE_REDIS_URL
        if self.DATABASE_URL:
            cfg["SQLALCHEMY_DATABASE_URI"] = self.DATABASE_URL
        return cfg
