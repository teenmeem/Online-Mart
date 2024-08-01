async def insert_into_db(order_obj: OrderCreate):
    # Convert into sqlmodel object
    order_create: OrderCreate = OrderCreate.model_validate(order_obj)

    # Convert into dict without order_items
    order_dict: dict = order_create.model_dump(exclude={'order_items'})

    order_table: Order = Order(**order_dict)  # Convert into sqlmodel object
    try:
        with Session(engine) as session:
            session.add(order_table)
            session.commit()
            session.refresh(order_table)

            logger.info(
                f"Order '{order_table}' inserted into the database")

            grand_total: int = 0
            # Create and add OrderItem instances, and calculate grand total
            order_items: list = []
            for item in order_create.order_items:
                item_dict: dict = item.model_dump()
                item_dict['order_id'] = order_table.id
                item_dict['total_price'] = item.unit_price * item.quantity
                order_item_table = OrderItem(**item_dict)
                grand_total += item_dict['total_price']
                order_items.append(order_item_table)

            # Update the order's total_amount
            order_table.total_amount = grand_total
            session.add_all(order_items)
            session.commit()
            session.refresh(order_table)

            logger.info(
                f"Order '{order_items}' inserted into the database")
            return {"ok": True}
    except Exception as e:
        logger.error(f"Failed to create product: {e}")
