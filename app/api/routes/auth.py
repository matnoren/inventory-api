from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import login_user, get_current_user
from app.crud.user import create_user, get_user_by_email, get_user_by_username, count_users
from app.core.exceptions import ConflictException
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user. The first registered user automatically becomes admin."""
    if get_user_by_email(db, user_in.email):
        raise ConflictException("Email already registered")
    if get_user_by_username(db, user_in.username):
        raise ConflictException("Username already taken")

    # First user gets admin role automatically
    role = "admin" if count_users(db) == 0 else "user"
    return create_user(db, user_in, role=role)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate and receive a JWT access token."""
    return login_user(db, login_data.username, login_data.password)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Get the currently authenticated user's profile."""
    return current_user
