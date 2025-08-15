from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import validates, relationship

from .db import Base


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_location = Column(String(64), nullable=False)  # 'Storage' or 'Show'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to items in this batch
    items = relationship("Item", back_populates="batch")


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
    brand = Column(String(64), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    location = Column(String(64), nullable=True)  # Changed to match dropdown options
    notes = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    description = Column(Text, nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to batch
    batch = relationship("Batch", back_populates="items")

    @validates("quantity")
    def validate_quantity(self, _key, value):  # noqa: D401
        if value is None:
            return 0
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        return value

    @validates("location")
    def validate_location(self, _key, value):
        if value and value not in ["Storage", "Show"]:
            raise ValueError("Location must be either 'Storage' or 'Show'")
        return value


class ScanEvent(Base):
    __tablename__ = "scan_events"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)