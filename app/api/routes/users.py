from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.crud.user import get_user, get_users, update_user, update_user_role, deactivate_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserRoleUpdate
from app.services.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[User]:
    """List all users. Admin only."""
    return get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Get a user by ID. Users can only view their own profile; admins can view anyone."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise ForbiddenException("You can only view your own profile")

    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Update a user profile. Users can only update their own profile; admins can update anyone."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise ForbiddenException("You can only update your own profile")

    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    return update_user(db, user, user_in)


@router.patch("/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    role_in: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> User:
    """Update a user's role. Admin only."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    if user.id == current_user.id:
        raise ForbiddenException("You cannot change your own role")
    return update_user_role(db, user, role_in.role)


@router.delete("/{user_id}", status_code=204)
def deactivate(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> None:
    """Deactivate a user account. Admin only."""
    user = get_user(db, user_id)
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    if user.id == current_user.id:
        raise ForbiddenException("You cannot deactivate your own account")
    deactivate_user(db, user)
