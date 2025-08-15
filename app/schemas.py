from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class ItemBase(BaseModel):
    barcode: Optional[str] = Field(default=None, max_length=64)
    name: Optional[str] = None
    game: Optional[str] = None
    set_name: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[int] = 0
    location: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    batch_id: Optional[int] = None

    @validator('location')
    def validate_location(cls, v):
        if v and v not in ["Storage", "Show"]:
            raise ValueError("Location must be either 'Storage' or 'Show'")
        return v


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    game: Optional[str] = None
    set_name: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    batch_id: Optional[int] = None

    @validator('location')
    def validate_location(cls, v):
        if v and v not in ["Storage", "Show"]:
            raise ValueError("Location must be either 'Storage' or 'Show'")
        return v


class ItemRead(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    barcode: str
    increment: Optional[int] = 1


class ScanResponse(BaseModel):
    item: ItemRead
    is_new: bool


class QuantityUpdateRequest(BaseModel):
    barcode: str
    action: str = Field(..., description="Action to perform: 'add' or 'sell'")
    quantity: int = Field(..., gt=0, description="Number of items to add or sell")


# Batch schemas
class BatchBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    target_location: str = Field(..., description="Target location for batch items")

    @validator('target_location')
    def validate_target_location(cls, v):
        if v not in ["Storage", "Show"]:
            raise ValueError("Target location must be either 'Storage' or 'Show'")
        return v


class BatchCreate(BatchBase):
    pass


class BatchUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    target_location: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('target_location')
    def validate_target_location(cls, v):
        if v and v not in ["Storage", "Show"]:
            raise ValueError("Target location must be either 'Storage' or 'Show'")
        return v


class BatchRead(BatchBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    item_count: Optional[int] = 0

    class Config:
        from_attributes = True


class BatchWithItems(BatchRead):
    items: List[ItemRead] = []


class BatchScanRequest(BaseModel):
    barcode: str
    batch_id: int
    quantity: int = Field(1, gt=0)


class BatchTransferRequest(BaseModel):
    batch_id: int
    action: str = Field(..., description="Action to perform: 'transfer' or 'cancel'")


class UnrecognizedBarcodeResponse(BaseModel):
    barcode: str
    message: str = "Barcode not found in database"


class ScanEventRead(BaseModel):
    id: int
    barcode: str
    created_at: datetime

    class Config:
        from_attributes = True