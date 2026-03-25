import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AssetCreate(BaseModel):
    symbol: str
    name: str
    description: Optional[str] = None


class AssetUpdate(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class AssetResponse(BaseModel):
    id: uuid.UUID
    symbol: str
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True