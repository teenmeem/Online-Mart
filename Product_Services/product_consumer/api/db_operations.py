from sqlmodel import Session
from fastapi import HTTPException
from common_files.database import engine
from common_files.product_model import Product, ProductCreate, ProductUpdate
import logging

logger = logging.getLogger(__name__)


async def insert_product_into_db(product: ProductCreate):
    """
    Asynchronously inserts a product into the database.

    Args:
        product (ProductCreate): The product to be inserted.

    Returns:
        dict: A dictionary with a single key "ok" set to True if the insertion was successful.

    Raises:
        Exception: If the insertion fails for any reason.
    """
    item: Product = Product.model_validate(product)
    try:
        with Session(engine) as session:
            session.add(item)
            session.commit()

            logger.info(f"Product '{item}' inserted into the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to create product: {e}")


async def update_product_in_db(id: int, product: ProductUpdate):
    """
    Asynchronously updates a product in the database.

    Args:
        id (int): The ID of the product to be updated.
        product (ProductUpdate): A dictionary containing the updated values of the product.

    Returns:
        dict: A dictionary with a single key "ok" set to True if the update was successful.

    Raises:
        HTTPException: If the product with the given ID is not found in the database.
        Exception: If there is an error during the update process.
    """
    try:
        with Session(engine) as session:
            item: Product = session.get(Product, id)
            if not item:
                raise HTTPException(
                    status_code=404, detail="Product not found")

            for key, value in product.items():  # product received dict object just ignore red line
                # set new values according to key
                setattr(item, key, value)
            session.commit()

            logger.info(f"Product with ID '{
                        item.id}' updated from the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to update product: {e}")


async def delete_product_from_db(item_id: int):
    """
    Deletes a product from the database based on the provided item ID.

    Parameters:
        item_id (int): The ID of the product to be deleted.

    Returns:
        dict: A dictionary with a single key "ok" set to True if the deletion was successful.

    Raises:
        HTTPException: If the product with the given ID is not found in the database.
        Exception: If there is an error during the deletion process.
    """
    try:
        with Session(engine) as session:
            item: Product = session.get(Product, item_id)
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
