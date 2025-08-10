from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    barcode: Optional[str] = Field(default=None, max_length=64)
    name: Optional[str] = None
    game: Optional[str] = None
    set_name: Optional[str] = None
    number_in_set: Optional[str] = None
    quantity: Optional[int] = 0
    location: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    game: Optional[str] = None
    set_name: Optional[str] = None
    number_in_set: Optional[str] = None
    quantity: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None


class ItemRead(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    barcode: str
    increment: int = 1


class ScanResponse(BaseModel):
    item: ItemRead
    is_new: bool


class UnrecognizedBarcodeResponse(BaseModel):
    barcode: str
    message: str = "Barcode not found in database"


class NewItemCreate(BaseModel):
    barcode: str
    name: Optional[str] = None
    game: Optional[str] = None
    set_name: Optional[str] = None
    number_in_set: Optional[str] = None
    quantity: int = 1
    location: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None


class ScanEventRead(BaseModel):
    id: int
    barcode: str
    created_at: datetime

    class Config:
        from_attributes = True