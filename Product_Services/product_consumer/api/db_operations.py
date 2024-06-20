from sqlmodel import Session
from fastapi import HTTPException
from common_files.database import engine
from common_files.product_model import Product, ProductCreate, ProductUpdate
import logging
import asyncio

logger = logging.getLogger(__name__)


async def insert_product_into_db(product: ProductCreate):
    item = Product.model_validate(product)
    try:
        with Session(engine) as session:
            session.add(item)
            session.commit()
#            session.refresh(item)

            logger.info(f"Product '{item}' inserted into the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to create product: {e}")


async def update_product_in_db(id: int, product: ProductUpdate):
    """Update product in the database."""
    try:
        with Session(engine) as session:
            item = session.get(Product, id)
            if not item:
                raise HTTPException(
                    status_code=404, detail="Product not found")

            for key, value in product.items():  # product received dict object
                # set new values according to key
                setattr(item, key, value)

            session.commit()
 #           session.refresh(item)
            logger.info(f"Product with ID '{
                        item.id}' updated from the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to update product: {e}")


async def delete_product_from_db(item_id: int):
    try:
        with Session(engine) as session:
            item = session.get(Product, item_id)
            if not item:
                raise HTTPException(
                    status_code=404, detail="Product not found")

            session.delete(item)
            session.commit()
            logger.info(f"Product with ID '{
                        item.id}' deleted from the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to delete product: {e}")
