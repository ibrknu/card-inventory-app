from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..db import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.post("/", response_model=schemas.BatchRead)
def create_batch(batch_data: schemas.BatchCreate, db: Session = Depends(get_db)):
    """Create a new batch"""
    db_batch = crud.create_batch(db, **batch_data.dict())
    return db_batch


@router.get("/", response_model=List[schemas.BatchRead])
def list_batches(active_only: bool = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all batches, optionally filtering by active status"""
    if active_only:
        batches = crud.get_active_batches(db, skip=skip, limit=limit)
    else:
        batches = crud.get_all_batches(db, skip=skip, limit=limit)
    
    # Add item count to each batch
    result = []
    for batch in batches:
        stats = crud.get_batch_stats(db, batch.id)
        batch_dict = schemas.BatchRead.from_orm(batch)
        batch_dict.item_count = stats["item_count"]
        result.append(batch_dict)
    
    return result


@router.get("/{batch_id}", response_model=schemas.BatchWithItems)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    """Get a specific batch with all its items"""
    db_batch = crud.get_batch(db, batch_id=batch_id)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    items = crud.get_batch_items(db, batch_id)
    stats = crud.get_batch_stats(db, batch_id)
    
    batch_dict = schemas.BatchRead.from_orm(db_batch)
    batch_dict.item_count = stats["item_count"]
    
    return schemas.BatchWithItems(**batch_dict.dict(), items=items)


@router.put("/{batch_id}", response_model=schemas.BatchRead)
def update_batch(batch_id: int, batch_data: schemas.BatchUpdate, db: Session = Depends(get_db)):
    """Update a batch"""
    db_batch = crud.get_batch(db, batch_id=batch_id)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    updated_batch = crud.update_batch(db, db_batch, **batch_data.dict(exclude_unset=True))
    return updated_batch


@router.delete("/{batch_id}")
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    """Delete a batch and remove all items from it"""
    db_batch = crud.get_batch(db, batch_id=batch_id)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    crud.delete_batch(db, batch_id=batch_id)
    return {"message": "Batch deleted successfully"}


@router.post("/{batch_id}/scan", response_model=schemas.ScanResponse)
def scan_item_to_batch(batch_id: int, scan_data: schemas.BatchScanRequest, db: Session = Depends(get_db)):
    """Add an item to a batch by scanning its barcode"""
    if scan_data.batch_id != batch_id:
        raise HTTPException(status_code=400, detail="Batch ID mismatch")
    
    # Check if batch exists and is active
    batch = crud.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    if not batch.is_active:
        raise HTTPException(status_code=400, detail="Batch is not active")
    
    # Check if item exists
    item = crud.get_item_by_barcode(db, scan_data.barcode)
    is_new = False
    
    if item:
        # Item exists, add to batch
        item = crud.add_item_to_batch(db, scan_data.barcode, batch_id, scan_data.quantity)
        if not item:
            raise HTTPException(status_code=500, detail="Failed to add item to batch")
    else:
        # Item doesn't exist - return response indicating new item
        is_new = True
        # Don't create a generic item - let the frontend handle it
    
    # Create scan event
    crud.create_scan_event(db, scan_data.barcode)
    
    return schemas.ScanResponse(item=item if item else schemas.ItemRead(
        id=0,  # Placeholder
        barcode=scan_data.barcode,
        name="",
        game="",
        set_name="",
        brand="",
        quantity=0,
        location=batch.target_location,
        notes="",
        price=None,
        description="",
        batch_id=batch_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    ), is_new=is_new)


@router.post("/{batch_id}/add-item", response_model=schemas.ItemRead)
def add_item_to_batch_with_details(batch_id: int, item_data: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Add a new item to a batch with full details"""
    # Check if batch exists and is active
    batch = crud.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    if not batch.is_active:
        raise HTTPException(status_code=400, detail="Batch is not active")
    
    # Check if item already exists
    existing_item = crud.get_item_by_barcode(db, item_data.barcode)
    
    if existing_item:
        # Update existing item and add to batch
        updated_item = crud.update_item(
            db,
            existing_item,
            name=item_data.name,
            game=item_data.game,
            set_name=item_data.set_name,
            brand=item_data.brand,
            quantity=item_data.quantity,
            location=batch.target_location,  # Set to batch target location
            notes=item_data.notes,
            price=float(item_data.price) if item_data.price else None,
            description=item_data.description,
            batch_id=batch_id,  # Add to batch
        )
        print(f"Updated existing item and added to batch: {updated_item.name}")
        return updated_item
    
    # Create new item with batch information
    item = crud.create_item(
        db,
        barcode=item_data.barcode,
        name=item_data.name,
        game=item_data.game,
        set_name=item_data.set_name,
        brand=item_data.brand,
        quantity=item_data.quantity,
        location=batch.target_location,  # Set to batch target location
        notes=item_data.notes,
        price=float(item_data.price) if item_data.price else None,
        description=item_data.description,
        batch_id=batch_id,  # Add to batch
    )
    
    # Create scan event
    crud.create_scan_event(db, barcode=item_data.barcode)
    
    print(f"Created new item and added to batch: {item.name}")
    return item


@router.post("/{batch_id}/transfer")
def transfer_batch(batch_id: int, transfer_data: schemas.BatchTransferRequest, db: Session = Depends(get_db)):
    """Transfer or cancel a batch"""
    if transfer_data.batch_id != batch_id:
        raise HTTPException(status_code=400, detail="Batch ID mismatch")
    
    if transfer_data.action == "transfer":
        result = crud.transfer_batch_items(db, batch_id)
        if not result:
            raise HTTPException(status_code=404, detail="Batch not found")
        return {
            "message": f"Batch transferred successfully. {result['items_transferred']} items moved to {result['batch'].target_location}",
            "items_transferred": result["items_transferred"]
        }
    elif transfer_data.action == "cancel":
        result = crud.cancel_batch(db, batch_id)
        if not result:
            raise HTTPException(status_code=404, detail="Batch not found")
        return {
            "message": f"Batch cancelled successfully. {result['items_removed']} items removed from batch",
            "items_removed": result["items_removed"]
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'transfer' or 'cancel'")
