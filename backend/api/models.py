"""Database models.

Only used when DATABASE_URL is configured. Each search stores one row per
result so we can later chart how a product's price moves over time.
"""
from datetime import datetime, timezone

from api.extensions import db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PriceSnapshot(db.Model):
    __tablename__ = "price_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    # NB: attribute is `search_query`, not `query` -- a column named `query`
    # would shadow Flask-SQLAlchemy's Model.query interface and break reads.
    search_query = db.Column(db.String(120), index=True, nullable=False)
    platform = db.Column(db.String(120), nullable=False)
    product_name = db.Column(db.String(400))
    price = db.Column(db.Float)
    unit_price = db.Column(db.Float)          # normalised price per base unit
    unit_basis = db.Column(db.String(16))     # "100g" | "L" | "unit"
    in_stock = db.Column(db.Boolean, default=True)
    captured_at = db.Column(db.DateTime, default=_utcnow, index=True)

    def to_dict(self) -> dict:
        return {
            "query": self.search_query,
            "platform": self.platform,
            "product_name": self.product_name,
            "price": self.price,
            "unit_price": self.unit_price,
            "unit_basis": self.unit_basis,
            "in_stock": self.in_stock,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
        }
