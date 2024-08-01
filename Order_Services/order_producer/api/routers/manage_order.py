from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from aiokafka import AIOKafkaProducer
from common_files.order_trans_model import OrderCreate
from common_files import settings
from api.kafka_services import kafka_producer
from common_files.json_custom_serialization import custom_json_serializer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/create')
async def create(
    order: OrderCreate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):

    try:
        logger.info(f"Converting dictionary to json serialized: {order}")
        item_dict = order.model_dump()
        logger.info(f"Creating transaction: {item_dict}")

        # Serialize json message
        serialized_item = custom_json_serializer(item_dict)

        # Send message to Kafka topics
        await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, serialized_item)
        logger.info(f"Transaction '{order}' sent to Kafka topic '{
                    settings.KAFKA_ORDER_TOPIC}'")

        # -------- Order items balance --------
        for item in order.order_items:
            # Convert item to json serialized message
            logger.info(f"Converting dictionary to json serialized: {
                        order.order_items}")

            item_bal_dict: dict
            item_bal_dict = {'transaction_type': order.transaction_type,
                             'product_id': item.product_id,
                             'quantity': item.quantity}

            logger.info(f"Creating transaction: {item_bal_dict}")

            serialized_item_bal = custom_json_serializer(item_bal_dict)
            await producer.send_and_wait(settings.KAFKA_PRODUCT_BAL_TOPIC, serialized_item_bal)

            logger.info(f"Transaction '{order.order_items}' sent to Kafka topic '{
                        settings.KAFKA_PRODUCT_BAL_TOPIC}'")

# -----

        # Flush the producer to ensure all messages are sent
        await producer.flush()

        return order
    except Exception as e:
        logger.error(f"Failed to create transaction: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create transaction")
    finally:
        # Close the producer to release resources
        await producer.stop()

""" 
@router.patch('/update/{order_id}', response_model=InventoryTransResponse)
async def update(
    order_id: int,
    order: InventoryTransUpdate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    with get_session() as session:
        trans: InventoryTransaction = session.get(
            InventoryTransaction, order_id)
        if not trans:
            raise HTTPException(
                status_code=404, detail="Transaction not found")

        try:
            # Convert InventoryTransUpdate model to dictionary, excluding unset values
            item_dict: dict = order.model_dump(exclude_unset=True)
            item_dict["id"] = order_id

            logger.info(f"Updating transaction with ID '{
                        order_id}': {item_dict}")

            # Serialize the item_dict to JSON format
            serialized_item = custom_json_serializer(item_dict)

            # Send the serialized item to Kafka
            await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, serialized_item)
            logger.info(f"Transaction with ID '{order_id}' sent to Kafka topic '{
                        settings.KAFKA_ORDER_TOPIC}'")

            # Flush the producer to ensure all messages are sent
            await producer.flush()

            # Update the transaction in the session
            for key, value in item_dict.items():
                setattr(trans, key, value)

            return trans

        except Exception as e:
            logger.error(f"Failed to update transaction with ID '{
                         order_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update transaction")
        finally:
            # Close the producer to release resources
            await producer.stop()


@router.delete('/delete/{order_id}', response_model=InventoryTransResponse)
async def delete(
    order_id: int,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    with get_session() as session:
        order: InventoryTransaction = session.get(
            InventoryTransaction, order_id)
        if not order:
            raise HTTPException(
                status_code=404, detail="Transaction not found")

        try:

            # Convert product ID to JSON message
            item_dict = order.model_dump()
            item_dict["transaction_type"] = "OUT"

            logger.info(f"Deleting transaction with ID: {order_id}")

            # Serialize JSON message
            serialized_item = custom_json_serializer(item_dict)

            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC_DELETE, serialized_item)
            await producer.send_and_wait(settings.KAFKA_PRODUCT_BAL_TOPIC, serialized_item)
            logger.info(f"Transaction ID '{order_id}' sent to Kafka topics '{
                        settings.KAFKA_ORDER_TOPIC_DELETE}' and '{settings.KAFKA_PRODUCT_BAL_TOPIC}' for deletion")

            # Flush the producer to ensure all messages are sent
            await producer.flush()

            # return {"message": f"Transaction ID '{order_id}' has been requested for deletion"}
            return order

        except Exception as e:
            logger.error(f"Failed to send transaction delete message with ID '{
                         order_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to send deletion message")
        finally:
            # Close the producer to release resources
            await producer.stop()
 """
