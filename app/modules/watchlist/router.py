import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.modules.watchlist.schemas import (
    WatchlistItemCreate, WatchlistItemUpdate, WatchlistItemResponse
)
from app.modules.watchlist import service

router = APIRouter()


@router.get("/", response_model=list[WatchlistItemResponse])
def get_watchlist(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return service.get_watchlist(str(current_user.id), db)


@router.post("/", response_model=WatchlistItemResponse, status_code=201)
def add_item(data: WatchlistItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return service.add_to_watchlist(str(current_user.id), data, db)


@router.patch("/{item_id}", response_model=WatchlistItemResponse)
def update_item(
    item_id: uuid.UUID,
    data: WatchlistItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return service.update_watchlist_item(str(item_id), str(current_user.id), data, db)


@router.delete("/{item_id}", status_code=204)
def remove_item(item_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service.remove_from_watchlist(str(item_id), str(current_user.id), db)