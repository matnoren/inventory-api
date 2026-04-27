from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.crud.product import get_product, update_stock
from app.models.product import Product
from app.schemas.product import StockUpdate


def adjust_stock(db: Session, product_id: int, stock_update: StockUpdate) -> Product:
    product = get_product(db, product_id)
    if not product:
        raise NotFoundException(f"Product with id {product_id} not found")

    new_quantity = product.stock_quantity + stock_update.quantity
    if new_quantity < 0:
        raise BadRequestException(
            f"Insufficient stock. Current: {product.stock_quantity}, "
            f"requested change: {stock_update.quantity}"
        )

    return update_stock(db, product, stock_update.quantity)


def get_low_stock_products(db: Session, skip: int = 0, limit: int = 20):
    from app.crud.product import get_products
    items, total = get_products(db, skip=skip, limit=limit, low_stock_only=True)
    return items, total
