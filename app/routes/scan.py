from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan", response_model=schemas.ScanResponse)
def scan_barcode(payload: schemas.ScanRequest, db: Session = Depends(get_db)):
    barcode = payload.barcode.strip()
    increment = payload.increment or 1

    print(f"Scan request received for barcode: {barcode}")

    item = crud.get_item_by_barcode(db, barcode)
    is_new = False
    
    if item:
        print(f"Found existing item: {item.name} (ID: {item.id})")
        # Don't automatically increment - let the frontend handle the quantity update
        print(f"Existing item found: {item.name} (qty {item.quantity})")
    else:
        print(f"No existing item found, creating basic item...")
        # Create a basic item with just barcode and quantity
        item = crud.create_item(db, barcode=barcode, quantity=increment)
        is_new = True
        print(f"Created basic item with ID: {item.id}")

    crud.create_scan_event(db, barcode=barcode)
    return schemas.ScanResponse(item=item, is_new=is_new)


@router.post("/items/update-quantity", response_model=schemas.ItemRead)
def update_item_quantity(payload: schemas.QuantityUpdateRequest, db: Session = Depends(get_db)):
    print(f"Updating quantity for barcode: {payload.barcode}")
    
    item = crud.get_item_by_barcode(db, payload.barcode)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Calculate new quantity based on action
    current_quantity = item.quantity or 0
    if payload.action == "add":
        new_quantity = current_quantity + payload.quantity
    elif payload.action == "sell":
        new_quantity = current_quantity - payload.quantity
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Cannot sell more items than available in inventory")
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'add' or 'sell'")
    
    print(f"Updating {item.name}: {current_quantity} -> {new_quantity} ({payload.action} {payload.quantity})")
    
    # Update the item quantity
    updated_item = crud.update_item(db, item, quantity=new_quantity)
    
    # Create scan event
    crud.create_scan_event(db, barcode=payload.barcode)
    
    return updated_item


@router.post("/items/new", response_model=schemas.ItemRead)
def create_new_item(item_data: schemas.ItemCreate, db: Session = Depends(get_db)):
    print(f"Processing new item request for barcode: {item_data.barcode}")
    
    # Check if item already exists
    existing_item = crud.get_item_by_barcode(db, item_data.barcode)
    
    if existing_item:
        print(f"Found existing item with ID {existing_item.id}, updating...")
        # Update the existing item with the new details
        updated_item = crud.update_item(
            db,
            existing_item,
            name=item_data.name,
            game=item_data.game,
            set_name=item_data.set_name,
            brand=item_data.brand,
            quantity=item_data.quantity,
            location=item_data.location,
            notes=item_data.notes,
            price=float(item_data.price) if item_data.price else None,
            description=item_data.description,
        )
        print(f"Item updated successfully: {updated_item.name}")
        return updated_item
    
    print(f"No existing item found, creating new item...")
    # Create new item with all provided details if it doesn't exist
    item = crud.create_item(
        db,
        barcode=item_data.barcode,
        name=item_data.name,
        game=item_data.game,
        set_name=item_data.set_name,
        brand=item_data.brand,
        quantity=item_data.quantity,
        location=item_data.location,
        notes=item_data.notes,
        price=float(item_data.price) if item_data.price else None,
        description=item_data.description,
    )
    
    # Create scan event
    crud.create_scan_event(db, barcode=item_data.barcode)
    
    print(f"New item created successfully: {item.name}")
    return item