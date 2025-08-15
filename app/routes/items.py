from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from .. import crud, schemas, models

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("/", response_model=List[schemas.ItemRead])
def list_items(
    limit: int = Query(500, ge=1, le=5000), 
    offset: int = Query(0, ge=0), 
    search: str = Query(None, description="Search term for name, game, set, or barcode"),
    db: Session = Depends(get_db)
):
    if search:
        return crud.get_items(db, skip=offset, limit=limit, search=search)
    return crud.get_items(db, skip=offset, limit=limit)


@router.get("/{item_id}", response_model=schemas.ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=schemas.ItemRead)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    if payload.barcode:
        existing = crud.get_item_by_barcode(db, payload.barcode)
        if existing:
            raise HTTPException(status_code=409, detail="Item with this barcode already exists")
    
    item_data = payload.dict()
    if payload.price:
        item_data["price"] = float(payload.price)
    
    item = crud.create_item(db, **item_data)
    return item


@router.patch("/{item_id}", response_model=schemas.ItemRead)
def update_item(item_id: int, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = payload.dict(exclude_unset=True)
    if payload.price:
        update_data["price"] = float(payload.price)
    
    updated = crud.update_item(db, item, **update_data)
    return updated


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.delete_item(db, item_id)
    return {"message": "Item deleted successfully"}