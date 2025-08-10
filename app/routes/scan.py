from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import crud, schemas

router = APIRouter(prefix="/api", tags=["scan"])


@router.post("/scan", response_model=schemas.ScanResponse)
def scan_barcode(payload: schemas.ScanRequest, db: Session = Depends(get_db)):
    barcode = payload.barcode.strip()
    increment = payload.increment or 1

    item = crud.get_item_by_barcode(db, barcode)
    is_new = False
    
    if item:
        item = crud.increment_item_quantity(db, item, by=increment)
    else:
        # Create a basic item with just barcode and quantity
        item = crud.create_item(db, barcode=barcode, quantity=increment)
        is_new = True

    crud.create_scan_event(db, barcode=barcode)
    return schemas.ScanResponse(item=item, is_new=is_new)


@router.post("/items/new", response_model=schemas.ItemRead)
def create_new_item(item_data: schemas.NewItemCreate, db: Session = Depends(get_db)):
    # Check if item already exists
    existing_item = crud.get_item_by_barcode(db, item_data.barcode)
    if existing_item:
        raise HTTPException(status_code=400, detail="Item with this barcode already exists")
    
    # Create new item with all provided details
    item = crud.create_item(
        db,
        barcode=item_data.barcode,
        name=item_data.name,
        game=item_data.game,
        set_name=item_data.set_name,
        number_in_set=item_data.number_in_set,
        quantity=item_data.quantity,
        location=item_data.location,
        notes=item_data.notes,
        price=float(item_data.price) if item_data.price else None,
        description=item_data.description,
    )
    
    # Create scan event
    crud.create_scan_event(db, barcode=item_data.barcode)
    
    return item