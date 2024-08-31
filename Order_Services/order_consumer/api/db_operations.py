from sqlmodel import Session
from fastapi import HTTPException
from common_files.database import engine
from common_files.order_trans_model import Order, OrderCreate, OrderItem

import logging

logger = logging.getLogger(__name__)

# session.flush()  # Ensures that order_instance.id is available


async def insert_into_db(order_obj: OrderCreate) -> dict:
    """
    Inserts a new order into the database, including the order items and calculating the grand total.

    Args:
        order_obj (OrderCreate): The order object to be inserted into the database.

    Returns:
        dict: A dictionary containing the success status and the ID of the inserted order.

    Raises:
        HTTPException: If there is an error inserting the order into the database.
    """
    try:
        order_create: OrderCreate = OrderCreate.model_validate(order_obj)

        order_dict: dict = order_create.model_dump(exclude={'order_items'})

        with Session(engine) as session:
            grand_total: int = 0
            order_items_list = []

            for item in order_create.order_items:
                item_total = item.unit_price * item.quantity
                grand_total += round(item_total)

                # Create OrderItem instance
                order_item = OrderItem(
                    **item.model_dump(), total_price=item_total)
                order_items_list.append(order_item)

            # Create Order instance and add the order items
            order_table = Order(
                **order_dict, total_amount=grand_total, order_items=order_items_list)

            session.add(order_table)
            session.commit()
            session.refresh(order_table)

            logger.info(f"Order items for Order ID {
                        order_table.id} inserted into the database")

            return {"success": True, "order_id": order_table.id}

    except Exception as e:
        logger.error(f"Failed to insert order into database: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def update_into_db_nused(id: int, transaction):
    # : InventoryTransUpdate):
    try:
        with Session(engine) as session:
            item: Order = session.get(Order, id)
            if not item:
                raise HTTPException(
                    status_code=404, detail="Transaction not found")

            for key, value in transaction.items():  # transaction received dict object just ignore red line
                # set new values according to key
                setattr(item, key, value)
            session.commit()

            logger.info(f"Transaction with ID '{
                        item.id}' updated from the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to update transaction: {e}")


async def delete_from_db(order_id: int):
    try:
        with Session(engine) as session:
            orders: Order = session.get(Order, order_id)
            if not orders:
                raise HTTPException(
                    status_code=404, detail="Transaction not found")

            session.delete(orders)
            session.commit()

            logger.info(f"Transaction with ID '{
                        orders.id}' deleted from the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to delete transaction: {e}")
