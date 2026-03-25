from sqlalchemy.orm import Session
from fastapi import HTTPException


from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.users.schemas import UpdateUserRequest



def get_user_profile(user: User)->User:
    return user



def update_user_profile(user: User, data: UpdateUserRequest, db: Session) -> User:
    if data.email:
        existing = db.query(User).filter(User.email == data.email.lower(), User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = data.email.lower()

    if data.username:
        existing = db.query(User).filter(User.username == data.username, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = data.username

    db.commit()
    db.refresh(user)
    return user

def delete_user_account(user: User, db: Session) -> None:
    # Revoke all refresh tokens first
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update({"is_revoked": True})
    db.delete(user)
    db.commit()


def list_all_users(db: Session, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    return db.query(User).offset(offset).limit(limit).all()


def get_user_by_id(user_id: str, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def deactivate_user(user_id: str, db: Session) -> User:
    user = get_user_by_id(user_id, db)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user