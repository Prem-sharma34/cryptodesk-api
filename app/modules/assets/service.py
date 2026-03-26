from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.modules.assets.models import Asset
from app.modules.assets.schemas import AssetCreate, AssetUpdate
from app.utils.cache import cache_get, cache_set, cache_delete
from app.utils.logger import assets_logger  # ← added

CACHE_KEY = "assets:all"
CACHE_TTL = 300  # 5 minutes


def list_assets(db: Session):
    cached = cache_get(CACHE_KEY)
    if cached is not None:
        assets_logger.info("Cache hit", extra={"key": CACHE_KEY})
        return cached

    assets_logger.info("Cache miss — querying DB", extra={"key": CACHE_KEY})
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
    return assets


def get_asset(asset_id: str, db: Session) -> Asset:
    asset = db.query(Asset).filter(
        Asset.id == asset_id, Asset.is_active == True
    ).first()
    if not asset:
        assets_logger.warning(
            "Asset not found",
            extra={"asset_id": asset_id}
        )
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


def create_asset(data: AssetCreate, db: Session) -> Asset:
    if db.query(Asset).filter(Asset.symbol == data.symbol.upper()).first():
        assets_logger.warning(
            "Duplicate asset symbol",
            extra={"symbol": data.symbol.upper()}
        )
        raise HTTPException(status_code=409, detail="Asset symbol already exists")

    asset = Asset(
        symbol=data.symbol.upper(),
        name=data.name,
        description=data.description
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    cache_delete(CACHE_KEY)

    assets_logger.info(
        "Asset created",
        extra={"asset_id": str(asset.id), "symbol": asset.symbol, "asset_name": asset.name}
    )

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

    assets_logger.info(
    "Asset updated",
    extra={"asset_id": str(asset.id), "symbol": asset.symbol}
    )

    return asset


def delete_asset(asset_id: str, db: Session) -> Asset:
    asset = get_asset(asset_id, db)
    asset.is_active = False
    db.commit()
    db.refresh(asset)
    cache_delete(CACHE_KEY)

    assets_logger.info(
        "Asset soft-deleted",
        extra={"asset_id": str(asset.id), "symbol": asset.symbol}
    )

    return asset