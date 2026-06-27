"""Flask extension singletons.

Created here (unbound) and wired to the app inside create_app(). This is the
standard application-factory pattern: it avoids circular imports and lets tests
build a fresh, isolated app per run.
"""
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

cache = Cache()
cors = CORS()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
