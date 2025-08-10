from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from .. import crud, schemas, models

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("/", response_model=List[schemas.ItemRead])
def list_items(limit: int = Query(500, ge=1, le=5000), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return crud.list_items(db, limit=limit, offset=offset)


@router.get("/{item_id}", response_model=schemas.ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=schemas.ItemRead)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    if payload.barcode:
        existing = crud.get_item_by_barcode(db, payload.barcode)
        if existing:
            raise HTTPException(status_code=409, detail="Item with this barcode already exists")
    item = crud.create_item(
        db,
        barcode=payload.barcode,
        name=payload.name,
        game=payload.game,
        set_name=payload.set_name,
        number_in_set=payload.number_in_set,
        quantity=payload.quantity or 0,
        location=payload.location,
        notes=payload.notes,
        price=float(payload.price) if payload.price else None,
        description=payload.description,
    )
    return item


@router.patch("/{item_id}", response_model=schemas.ItemRead)
def update_item(item_id: int, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = crud.update_item(db, item, **payload.model_dump(exclude_unset=True))
    return updated