"""Pytest fixtures. Environment is set BEFORE importing the app so the
module-level Config() snapshot picks up demo mode and a relaxed rate limit."""
import os

# Force a deterministic test environment (no live key, no DB, no rate limit).
os.environ.pop("SERPAPI_KEY", None)
os.environ.pop("DATABASE_URL", None)
os.environ["DEMO_MODE"] = "true"
os.environ["RATELIMIT_SEARCH"] = "1000 per minute"

import pytest  # noqa: E402

from api.app_factory import create_app  # noqa: E402


@pytest.fixture()
def app():
    application = create_app()
    application.config.update(TESTING=True)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()
