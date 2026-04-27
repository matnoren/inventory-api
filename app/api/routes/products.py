import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.crud.product import (
    get_product, get_product_by_sku, get_products,
    create_product, update_product, delete_product,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductListResponse, StockUpdate,
)
from app.services.auth import get_current_user, get_current_admin
from app.services.inventory import adjust_stock

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=ProductListResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = Query(default=None, max_length=100),
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ProductListResponse:
    """List products with pagination, search, and filtering."""
    skip = (page - 1) * size
    items, total = get_products(
        db,
        skip=skip,
        limit=size,
        category_id=category_id,
        search=search,
        low_stock_only=low_stock_only,
    )
    return ProductListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 0,
    )


@router.post("/", response_model=ProductResponse, status_code=201)
def create_new_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Create a new product. Admin only."""
    if get_product_by_sku(db, product_in.sku):
        raise ConflictException(f"Product with SKU '{product_in.sku}' already exists")
    return create_product(db, product_in)


@router.get("/low-stock", response_model=list[ProductResponse])
def list_low_stock_products(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get all products that are at or below their low-stock threshold."""
    from app.services.inventory import get_low_stock_products
    items, _ = get_low_stock_products(db, skip=skip, limit=limit)
    return items


@router.get("/{product_id}", response_model=ProductResponse)
def get_single_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a single product by ID."""
    product = get_product(db, product_id)
    if not product:
        raise NotFoundException(f"Product with id {product_id} not found")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_existing_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Update product details. Admin only."""
    product = get_product(db, product_id)
    if not product:
        raise NotFoundException(f"Product with id {product_id} not found")
    return update_product(db, product, product_in)


@router.delete("/{product_id}", status_code=204)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Delete a product. Admin only."""
    product = get_product(db, product_id)
    if not product:
        raise NotFoundException(f"Product with id {product_id} not found")
    delete_product(db, product)


@router.post("/{product_id}/stock", response_model=ProductResponse)
def update_product_stock(
    product_id: int,
    stock_update: StockUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """
    Adjust product stock quantity. Admin only.
    Use positive values to add stock, negative to remove.
    Will reject if the resulting quantity would go below 0.
    """
    return adjust_stock(db, product_id, stock_update)
