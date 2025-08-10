from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint, Numeric
from sqlalchemy.orm import validates

from .db import Base


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("barcode", name="uq_items_barcode"),
    )

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(64), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    game = Column(String(64), nullable=True)
    set_name = Column(String(128), nullable=True)
    number_in_set = Column(String(64), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    location = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    @validates("quantity")
    def validate_quantity(self, _key, value):  # noqa: D401
        if value is None:
            return 0
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        return value


class ScanEvent(Base):
    __tablename__ = "scan_events"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)