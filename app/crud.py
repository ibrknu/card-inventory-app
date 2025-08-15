from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas


def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_item_by_barcode(db: Session, barcode: str):
    return db.query(models.Item).filter(models.Item.barcode == barcode).first()


def get_items(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.Item)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            models.Item.name.ilike(search_term) |
            models.Item.game.ilike(search_term) |
            models.Item.set_name.ilike(search_term) |
            models.Item.brand.ilike(search_term) |
            models.Item.barcode.ilike(search_term)
        )
    return query.offset(skip).limit(limit).all()


def create_item(db: Session, **kwargs):
    db_item = models.Item(**kwargs)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item: models.Item, **kwargs):
    for key, value in kwargs.items():
        if hasattr(item, key):
            setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item


def increment_item_quantity(db: Session, item: models.Item, by: int = 1):
    item.quantity += by
    db.commit()
    db.refresh(item)
    return item


def create_scan_event(db: Session, barcode: str):
    db_scan_event = models.ScanEvent(barcode=barcode)
    db.add(db_scan_event)
    db.commit()
    db.refresh(db_scan_event)
    return db_scan_event


# Batch CRUD operations
def get_batch(db: Session, batch_id: int):
    return db.query(models.Batch).filter(models.Batch.id == batch_id).first()


def get_active_batches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Batch).filter(models.Batch.is_active == True).offset(skip).limit(limit).all()


def get_all_batches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Batch).offset(skip).limit(limit).all()


def create_batch(db: Session, **kwargs):
    db_batch = models.Batch(**kwargs)
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def update_batch(db: Session, batch: models.Batch, **kwargs):
    for key, value in kwargs.items():
        if hasattr(batch, key):
            setattr(batch, key, value)
    db.commit()
    db.refresh(batch)
    return batch


def delete_batch(db: Session, batch_id: int):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if batch:
        # Remove batch_id from all items in this batch
        db.query(models.Item).filter(models.Item.batch_id == batch_id).update({"batch_id": None})
        db.delete(batch)
        db.commit()
    return batch


def add_item_to_batch(db: Session, barcode: str, batch_id: int, quantity: int = 1):
    """Add an item to a batch and update its location to the batch target location"""
    item = get_item_by_barcode(db, barcode)
    if not item:
        return None
    
    batch = get_batch(db, batch_id)
    if not batch or not batch.is_active:
        return None
    
    # Update item to be part of the batch and set location to batch target
    item.batch_id = batch_id
    item.location = batch.target_location
    item.quantity += quantity
    
    db.commit()
    db.refresh(item)
    return item


def transfer_batch_items(db: Session, batch_id: int):
    """Transfer all items in a batch to their target location and remove from batch"""
    batch = get_batch(db, batch_id)
    if not batch:
        return None
    
    # Update all items in the batch to have the target location and remove batch_id
    items_updated = db.query(models.Item).filter(models.Item.batch_id == batch_id).update({
        "location": batch.target_location,
        "batch_id": None
    })
    
    # Deactivate the batch
    batch.is_active = False
    
    db.commit()
    return {"batch": batch, "items_transferred": items_updated}


def cancel_batch(db: Session, batch_id: int):
    """Cancel a batch by removing batch_id from all items"""
    batch = get_batch(db, batch_id)
    if not batch:
        return None
    
    # Remove batch_id from all items in this batch
    items_updated = db.query(models.Item).filter(models.Item.batch_id == batch_id).update({"batch_id": None})
    
    # Deactivate the batch
    batch.is_active = False
    
    db.commit()
    return {"batch": batch, "items_removed": items_updated}


def get_batch_items(db: Session, batch_id: int):
    """Get all items in a specific batch"""
    return db.query(models.Item).filter(models.Item.batch_id == batch_id).all()


def get_batch_stats(db: Session, batch_id: int):
    """Get statistics for a batch including item count"""
    item_count = db.query(func.count(models.Item.id)).filter(models.Item.batch_id == batch_id).scalar()
    return {"item_count": item_count}