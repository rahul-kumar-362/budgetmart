"""Application factory: build, configure, and wire a Flask app.

Keeping construction in a function (rather than a module-level ``app``) lets
tests spin up isolated apps and makes the extension wiring explicit.
"""
import logging

from flask import Flask

from api.config import Config
from api.extensions import cache, cors, db, limiter
from api.routes import bp


def create_app(config: Config | None = None) -> Flask:
    config = config or Config()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config.update(config.as_flask_config())

    cache.init_app(app)
    limiter.init_app(app)

    if config.ALLOWED_ORIGINS.strip() == "*":
        origins = "*"
    else:
        origins = [o.strip() for o in config.ALLOWED_ORIGINS.split(",") if o.strip()]
    cors.init_app(app, resources={r"/*": {"origins": origins}})

    if config.database_enabled:
        db.init_app(app)
        with app.app_context():
            import api.models  # noqa: F401  (register models before create_all)

            db.create_all()
        app.logger.info("Database enabled; price history active")

    app.register_blueprint(bp)
    app.logger.info(
        "BudgetMart up | mode=%s | cache=%s | history=%s",
        "live" if config.live_enabled else "demo",
        config.CACHE_TYPE,
        config.database_enabled,
    )
    return app
