from sqlmodel import Session, IntegrityError, DatabaseError
from fastapi import HTTPException
from common_files.database import engine
from common_files.order_trans_model import Order, OrderCreate, OrderItem

import logging

# Define the logger
logger = logging.getLogger(__name__)


async def insert_into_db(order_obj: OrderCreate) -> dict:
    """
    Insert an order and its items into the database.

    Args:
        order_obj (OrderCreate): The order object containing order details and items.

    Returns:
        dict: A dictionary indicating the success of the operation.
    """

    try:
        # Validate and convert order_obj into a SQLModel object
        order_create: OrderCreate = OrderCreate.model_validate(order_obj)

        # Convert order_create into a dictionary excluding 'order_items'
        order_dict: dict = order_create.model_dump(exclude={'order_items'})

        # Create an Order instance from the dictionary
        order_table: Order = Order(**order_dict)

  #  try:
        with Session(engine) as session:
            # Add the order to the session and commit
            session.add(order_table)
            session.commit()
            session.refresh(order_table)

            logger.info(f"Order '{order_table}' inserted into the database")

            # Initialize grand total
            grand_total: int = 0
            # List to store order item instances
            order_items: list[OrderItem] = []

            # Process each order item
            for item in order_create.order_items:
                # Convert item to dictionary
                item_dict: dict = item.model_dump()
                # Add order ID and calculate total price
                item_dict['order_id'] = order_table.id
                item_dict['total_price'] = item.unit_price * item.quantity
                # Create an OrderItem instance from the dictionary
                order_item_table: OrderItem = OrderItem(**item_dict)
                # Add to grand total
                grand_total += item_dict['total_price']
                # Append to the list of order items
                order_items.append(order_item_table)

            # Update the order's total amount
            order_table.total_amount = grand_total
            # Add all order items to the session and commit
            session.add_all(order_items)
            session.commit()
            session.refresh(order_table)

            logger.info(f"Order items '{
                        order_items}' inserted into the database")

            return {"ok": True}

    except IntegrityError as e:
        logger.error(f"Integrity error occurred: {e}")
        raise HTTPException(status_code=400, detail="Data integrity error.")
    except DatabaseError as e:
        logger.error(f"Database error occurred: {e}")
        raise HTTPException(status_code=500, detail="Database error.")
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid input data")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create order: {e}")
        raise HTTPException(status_code=500, detail=str(e))