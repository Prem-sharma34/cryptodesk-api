import uuid
from fastapi import APIRouter , Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db , get_current_user , get_current_admin
from app.modules.users.schemas import UserResponse , UpdateUserRequest
from app.modules.users import service


router = APIRouter()



@router.get("/me" , response_model=UserResponse)
def get_my_profile(current_user=Depends(get_current_user)):
    return service.get_user_profile(current_user)



@router.put("/me",response_model=UserResponse)
def update_my_profile(
    data: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return service.update_user_profile(current_user,data,db)



@router.delete("/me", status_code=204)
def delete_my_account(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service.delete_user_account(current_user, db)


# --- Admin routes ---



@router.get("/", response_model=list[UserResponse])
def list_users(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    return service.list_all_users(db, page, limit)




@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return service.get_user_by_id(str(user_id), db)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return service.deactivate_user(str(user_id), db)