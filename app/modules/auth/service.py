import hashlib
import secrets
from datetime import datetime, timedelta , timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.modules.users.models import User, UserRole
from app.modules.auth.models import RefreshToken
from app.modules.auth.schemas import RegisterRequest , LoginRequest
from app.utils.security import hash_password, verify_password, create_access_token


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def _hash_refresh_token(token:str)->str:
    return hashlib.sha256(token.encode()).hexdigest()


def register_user(db: Session, email: str, username: str, password: str) -> User:
    user = User(
        email=email.lower(),
        username=username,
        hashed_password=hash_password(password),
        role=UserRole.user
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email.lower())
    if not user or not verify_password(password, user.hashed_password):
        return None, None

    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})

    raw_refresh_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()

    return access_token, raw_refresh_token


def refresh_tokens(db: Session, raw_refresh_token: str):
    token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

    if not db_token:
        return None, None

    # rotate — revoke old, issue new
    db_token.is_revoked = True

    new_access_token = create_access_token({
        "sub": str(db_token.user_id),
        "role": db_token.user.role.value
    })
    new_raw_token = secrets.token_urlsafe(32)
    new_hash = hashlib.sha256(new_raw_token.encode()).hexdigest()

    new_db_token = RefreshToken(
        user_id=db_token.user_id,
        token_hash=new_hash,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_db_token)
    db.commit()

    return new_access_token, new_raw_token


def logout_user(db: Session, raw_refresh_token: str) -> bool:
    token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if not db_token:
        return False

    db_token.is_revoked = True
    db.commit()
    return True


def _create_and_store_refresh_token(user_id, db: Session) -> str:
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    return raw_token