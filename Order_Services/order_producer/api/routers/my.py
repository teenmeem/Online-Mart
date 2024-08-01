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
