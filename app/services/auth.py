from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_access_token, verify_password
from app.crud.user import get_user, get_user_by_username
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.core.security import create_access_token

bearer_scheme = HTTPBearer()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login_user(db: Session, username: str, password: str) -> Token:
    user = authenticate_user(db, username, password)
    if not user:
        raise UnauthorizedException("Incorrect username or password")
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")

    access_token = create_access_token(subject=user.id, role=user.role)
    return Token(access_token=access_token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    user_id: int = int(payload.get("sub"))
    user = get_user(db, user_id)

    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise ForbiddenException("Admin access required")
    return current_user
