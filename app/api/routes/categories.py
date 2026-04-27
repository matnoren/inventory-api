from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.crud.category import (
    get_category, get_category_by_name, get_categories,
    create_category, update_category, delete_category, count_categories,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all product categories."""
    return get_categories(db, skip=skip, limit=limit)


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_new_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Create a new category. Admin only."""
    if get_category_by_name(db, category_in.name):
        raise ConflictException(f"Category '{category_in.name}' already exists")
    return create_category(db, category_in)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_single_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a single category by ID."""
    category = get_category(db, category_id)
    if not category:
        raise NotFoundException(f"Category with id {category_id} not found")
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Update a category. Admin only."""
    category = get_category(db, category_id)
    if not category:
        raise NotFoundException(f"Category with id {category_id} not found")

    if category_in.name and category_in.name != category.name:
        if get_category_by_name(db, category_in.name):
            raise ConflictException(f"Category '{category_in.name}' already exists")

    return update_category(db, category, category_in)


@router.delete("/{category_id}", status_code=204)
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Delete a category. Admin only. Products in this category will be uncategorized."""
    category = get_category(db, category_id)
    if not category:
        raise NotFoundException(f"Category with id {category_id} not found")
    delete_category(db, category)
