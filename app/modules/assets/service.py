from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.modules.assets.models import Asset
from app.modules.assets.schemas import AssetCreate, AssetUpdate
from app.utils.cache import cache_get, cache_set, cache_delete

CACHE_KEY = "assets:all"
CACHE_TTL = 300  # 5 minutes


def list_assets(db: Session):
    cached = cache_get(CACHE_KEY)
    if cached is not None:
        return cached  # raw list of dicts from cache

    assets = db.query(Asset).filter(Asset.is_active == True).all()
    serialized = [
        {
            "id": str(a.id),
            "symbol": a.symbol,
            "name": a.name,
            "description": a.description,
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat(),
        }
        for a in assets
    ]
    cache_set(CACHE_KEY, serialized, CACHE_TTL)
    return assets  # return ORM objects so response_model works


def get_asset(asset_id: str, db: Session) -> Asset:
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.is_active == True).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


def create_asset(data: AssetCreate, db: Session) -> Asset:
    if db.query(Asset).filter(Asset.symbol == data.symbol.upper()).first():
        raise HTTPException(status_code=400, detail="Asset symbol already exists")

    asset = Asset(symbol=data.symbol.upper(), name=data.name, description=data.description)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    cache_delete(CACHE_KEY)
    return asset


def update_asset(asset_id: str, data: AssetUpdate, db: Session) -> Asset:
    asset = get_asset(asset_id, db)
    if data.symbol:
        asset.symbol = data.symbol.upper()
    if data.name:
        asset.name = data.name
    if data.description is not None:
        asset.description = data.description

    db.commit()
    db.refresh(asset)
    cache_delete(CACHE_KEY)
    return asset


def delete_asset(asset_id: str, db: Session) -> Asset:
    asset = get_asset(asset_id, db)
    asset.is_active = False
    db.commit()
    db.refresh(asset)
    cache_delete(CACHE_KEY)
    return asset