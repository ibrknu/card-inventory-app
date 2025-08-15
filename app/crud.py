from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Union, List

from . import models


def get_item_by_id(db: Session, item_id: int) -> Union[models.Item, None]:
    return db.get(models.Item, item_id)


def get_item_by_barcode(db: Session, barcode: str) -> Union[models.Item, None]:
    if not barcode:
        return None
    stmt = select(models.Item).where(models.Item.barcode == barcode)
    return db.execute(stmt).scalars().first()


def list_items(db: Session, limit: int = 500, offset: int = 0) -> List[models.Item]:
    stmt = select(models.Item).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


def search_items(db: Session, search_term: str, limit: int = 500, offset: int = 0) -> List[models.Item]:
    """Search items by name, game, set_name, or barcode"""
    from sqlalchemy import or_, func
    
    # Normalize search term (lowercase and remove extra spaces)
    search_term = search_term.lower().strip()
    
    # Create search patterns for different variations
    search_pattern = f"%{search_term}%"
    
    # Special handling for common game name variations
    game_variations = []
    if "pokemon" in search_term or "pokémon" in search_term:
        game_variations.extend(["pokemon", "pokémon", "Pokemon", "Pokémon"])
    if "magic" in search_term:
        game_variations.extend(["magic", "Magic", "Magic: The Gathering", "MTG"])
    if "yugioh" in search_term or "yu-gi-oh" in search_term:
        game_variations.extend(["yugioh", "yu-gi-oh", "Yu-Gi-Oh!", "YuGiOh"])
    
    # Build the search conditions
    conditions = [
        models.Item.name.ilike(search_pattern),
        models.Item.game.ilike(search_pattern),
        models.Item.set_name.ilike(search_pattern),
        models.Item.brand.ilike(search_pattern),
        models.Item.barcode.ilike(search_pattern),
        models.Item.description.ilike(search_pattern),
        models.Item.notes.ilike(search_pattern)
    ]
    
    # Add game variation conditions if we have any
    for variation in game_variations:
        conditions.append(models.Item.game.ilike(f"%{variation}%"))
    
    stmt = select(models.Item).where(or_(*conditions)).offset(offset).limit(limit)
    
    return list(db.execute(stmt).scalars().all())


def create_item(
    db: Session,
    *,
    barcode: Union[str, None],
    name: Union[str, None] = None,
    game: Union[str, None] = None,
    set_name: Union[str, None] = None,
    brand: Union[str, None] = None,
    quantity: int = 0,
    location: Union[str, None] = None,
    notes: Union[str, None] = None,
    price: Union[float, None] = None,
    description: Union[str, None] = None,
) -> models.Item:
    item = models.Item(
        barcode=barcode,
        name=name,
        game=game,
        set_name=set_name,
        brand=brand,
        quantity=quantity,
        location=location,
        notes=notes,
        price=price,
        description=description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: models.Item, **updates) -> models.Item:
    for key, value in updates.items():
        if value is not None and hasattr(item, key):
            setattr(item, key, value)
    item.updated_at = datetime.now(timezone.utc)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def increment_item_quantity(db: Session, item: models.Item, by: int = 1) -> models.Item:
    item.quantity = (item.quantity or 0) + by
    item.updated_at = datetime.now(timezone.utc)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_scan_event(db: Session, barcode: str) -> models.ScanEvent:
    event = models.ScanEvent(barcode=barcode, created_at=datetime.now(timezone.utc))
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def delete_item(db: Session, item: models.Item) -> None:
    """Delete an item from the database"""
    db.delete(item)
    db.commit()