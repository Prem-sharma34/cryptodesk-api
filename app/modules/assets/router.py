import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, get_current_admin
from app.modules.assets.schemas import AssetCreate, AssetUpdate, AssetResponse
from app.modules.assets import service

router = APIRouter()


@router.get("/", response_model=list[AssetResponse])
def list_assets(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return service.list_assets(db)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return service.get_asset(str(asset_id), db)


@router.post("/", response_model=AssetResponse, status_code=201)
def create_asset(data: AssetCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return service.create_asset(data, db)


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: uuid.UUID, data: AssetUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return service.update_asset(str(asset_id), data, db)


@router.delete("/{asset_id}", response_model=AssetResponse)
def delete_asset(asset_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return service.delete_asset(str(asset_id), db)