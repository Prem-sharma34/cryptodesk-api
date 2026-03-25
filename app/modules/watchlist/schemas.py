import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WatchlistItemCreate(BaseModel):
    asset_id: uuid.UUID
    notes: Optional[str] = None


class WatchlistItemUpdate(BaseModel):
    notes: Optional[str] = None


class AssetInWatchlist(BaseModel):
    id: uuid.UUID
    symbol: str
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class WatchlistItemResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    notes: Optional[str]
    created_at: datetime
    asset: AssetInWatchlist

    class Config:
        from_attributes = True