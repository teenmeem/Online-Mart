from sqlmodel import Session
from fastapi import HTTPException
from common_files.database import engine
from common_files.inventory_trans_model import InventoryTransaction, InventoryTransCreate, InventoryTransUpdate
import logging

logger = logging.getLogger(__name__)


async def insert_into_db(transaction: InventoryTransCreate):
    trans: InventoryTransaction = InventoryTransaction.model_validate(
        transaction)
    try:
        with Session(engine) as session:
            session.add(trans)
            session.commit()

            logger.info(f"Transaction '{trans}' inserted into the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to create product: {e}")


async def update_in_db_nused(id: int, product: InventoryTransUpdate):
    try:
        with Session(engine) as session:
            item: InventoryTransaction = session.get(InventoryTransaction, id)
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


async def delete_from_db(trans_id: int):
    try:
        with Session(engine) as session:
            trans: InventoryTransaction = session.get(
                InventoryTransaction, trans_id)
            if not trans:
                raise HTTPException(
                    status_code=404, detail="Transaction not found")

            session.delete(trans)
            session.commit()

            logger.info(f"Transaction with ID '{
                        trans.id}' deleted from the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to delete transaction: {e}")
