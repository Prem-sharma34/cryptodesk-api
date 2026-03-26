from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.users.schemas import UpdateUserRequest
from app.utils.logger import users_logger  # ← added


def get_user_profile(user: User) -> User:
    users_logger.info(
        "Profile fetched",
        extra={"user_id": str(user.id), "email": user.email}
    )
    return user


def update_user_profile(user: User, data: UpdateUserRequest, db: Session) -> User:
    if data.email:
        existing = db.query(User).filter(
            User.email == data.email.lower(), User.id != user.id
        ).first()
        if existing:
            users_logger.warning(
                "Email update conflict",
                extra={"user_id": str(user.id), "requested_email": data.email}
            )
            raise HTTPException(status_code=409, detail="Email already in use")
        user.email = data.email.lower()

    if data.username:
        existing = db.query(User).filter(
            User.username == data.username, User.id != user.id
        ).first()
        if existing:
            users_logger.warning(
                "Username update conflict",
                extra={"user_id": str(user.id), "requested_username": data.username}
            )
            raise HTTPException(status_code=409, detail="Username already taken")
        user.username = data.username

    db.commit()
    db.refresh(user)

    users_logger.info(
        "Profile updated",
        extra={"user_id": str(user.id), "email": user.email}
    )

    return user


def delete_user_account(user: User, db: Session) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id
    ).update({"is_revoked": True})

    db.delete(user)
    db.commit()

    users_logger.info(
        "User account deleted",
        extra={"user_id": str(user.id), "email": user.email}
    )


def list_all_users(db: Session, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    users = db.query(User).offset(offset).limit(limit).all()

    users_logger.info(
        "Admin listed users",
        extra={"page": page, "limit": limit, "returned": len(users)}
    )

    return users


def get_user_by_id(user_id: str, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        users_logger.warning(
            "User not found",
            extra={"user_id": user_id}
        )
        raise HTTPException(status_code=404, detail="User not found")
    return user


def deactivate_user(user_id: str, db: Session) -> User:
    user = get_user_by_id(user_id, db)
    user.is_active = False
    db.commit()
    db.refresh(user)

    users_logger.info(
        "User deactivated",
        extra={"user_id": str(user.id), "email": user.email}
    )

    return user