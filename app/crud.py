from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from . import models


def get_item_by_id(db: Session, item_id: int) -> models.Item | None:
    return db.get(models.Item, item_id)


def get_item_by_barcode(db: Session, barcode: str) -> models.Item | None:
    if not barcode:
        return None
    stmt = select(models.Item).where(models.Item.barcode == barcode)
    return db.execute(stmt).scalars().first()


def list_items(db: Session, limit: int = 500, offset: int = 0) -> list[models.Item]:
    stmt = select(models.Item).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


def create_item(
    db: Session,
    *,
    barcode: str | None,
    name: str | None = None,
    game: str | None = None,
    set_name: str | None = None,
    number_in_set: str | None = None,
    quantity: int = 0,
    location: str | None = None,
    notes: str | None = None,
    price: float | None = None,
    description: str | None = None,
) -> models.Item:
    item = models.Item(
        barcode=barcode,
        name=name,
        game=game,
        set_name=set_name,
        number_in_set=number_in_set,
        quantity=quantity,
        location=location,
        notes=notes,
        price=price,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: models.Item, **updates) -> models.Item:
    for key, value in updates.items():
        if value is not None and hasattr(item, key):
            setattr(item, key, value)
    item.updated_at = datetime.utcnow()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def increment_item_quantity(db: Session, item: models.Item, by: int = 1) -> models.Item:
    item.quantity = (item.quantity or 0) + by
    item.updated_at = datetime.utcnow()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_scan_event(db: Session, barcode: str) -> models.ScanEvent:
    event = models.ScanEvent(barcode=barcode, created_at=datetime.utcnow())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event