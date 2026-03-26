from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.modules.watchlist.models import WatchlistItem
from app.modules.assets.models import Asset
from app.modules.watchlist.schemas import WatchlistItemCreate, WatchlistItemUpdate
from app.utils.logger import watchlist_logger  # ← added


def get_watchlist(user_id: str, db: Session):
    items = (
        db.query(WatchlistItem)
        .options(joinedload(WatchlistItem.asset))
        .filter(WatchlistItem.user_id == user_id)
        .all()
    )

    watchlist_logger.info(
        "Watchlist fetched",
        extra={"user_id": user_id, "item_count": len(items)}
    )

    return items


def add_to_watchlist(
    user_id: str, data: WatchlistItemCreate, db: Session
) -> WatchlistItem:
    asset = db.query(Asset).filter(
        Asset.id == str(data.asset_id), Asset.is_active == True
    ).first()

    if not asset:
        watchlist_logger.warning(
            "Add to watchlist failed — asset not found",
            extra={"user_id": user_id, "asset_id": str(data.asset_id)}
        )
        raise HTTPException(status_code=404, detail="Asset not found or inactive")

    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.asset_id == str(data.asset_id),
    ).first()

    if existing:
        watchlist_logger.warning(
            "Duplicate watchlist entry attempt",
            extra={"user_id": user_id, "asset_id": str(data.asset_id)}
        )
        raise HTTPException(status_code=409, detail="Asset already in watchlist")

    item = WatchlistItem(
        user_id=user_id,
        asset_id=str(data.asset_id),
        notes=data.notes
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    watchlist_logger.info(
        "Watchlist item added",
        extra={"user_id": user_id, "asset_id": str(data.asset_id), "item_id": str(item.id)}
    )

    return (
        db.query(WatchlistItem)
        .options(joinedload(WatchlistItem.asset))
        .filter(WatchlistItem.id == item.id)
        .first()
    )


def update_watchlist_item(
    item_id: str, user_id: str, data: WatchlistItemUpdate, db: Session
) -> WatchlistItem:
    item = _get_owned_item(item_id, user_id, db)

    if data.notes is not None:
        item.notes = data.notes

    db.commit()
    db.refresh(item)

    watchlist_logger.info(
        "Watchlist item updated",
        extra={"item_id": item_id, "user_id": user_id}
    )

    return (
        db.query(WatchlistItem)
        .options(joinedload(WatchlistItem.asset))
        .filter(WatchlistItem.id == item.id)
        .first()
    )


def remove_from_watchlist(item_id: str, user_id: str, db: Session) -> None:
    item = _get_owned_item(item_id, user_id, db)
    db.delete(item)
    db.commit()

    watchlist_logger.info(
        "Watchlist item removed",
        extra={"item_id": item_id, "user_id": user_id}
    )


def _get_owned_item(item_id: str, user_id: str, db: Session) -> WatchlistItem:
    item = db.query(WatchlistItem).filter(WatchlistItem.id == item_id).first()

    if not item:
        watchlist_logger.warning(
            "Watchlist item not found",
            extra={"item_id": item_id, "user_id": user_id}
        )
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    if str(item.user_id) != user_id:
        watchlist_logger.warning(
            "Unauthorized watchlist access attempt",
            extra={"item_id": item_id, "requesting_user": user_id, "owner": str(item.user_id)}
        )
        raise HTTPException(status_code=403, detail="Not your watchlist item")

    return item