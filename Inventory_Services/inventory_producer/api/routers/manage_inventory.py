from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from aiokafka import AIOKafkaProducer
from common_files.inventory_trans_model import InventoryTransaction, InventoryTransCreate, InventoryTransUpdate, InventoryTransResponse
from common_files import settings
from common_files.database import get_session
from api.kafka_services import kafka_producer
from common_files.json_custom_serialization import custom_json_serializer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/create')
async def create(
    inventory: InventoryTransCreate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):

    # with get_session() as session:
    # inventory: Inventory = session.exec(select(Inventory).where(
    # Inventory.product_id == item.product_id and
    # func.upper(Inventory.warehouse_location) == item.warehouse_location.upper())).one_or_none()

    # if inventory:
    #     raise HTTPException(
    #         status_code=409, detail="Product already exists")

    try:

        # Convert item to json serialized message
        logger.info(f"Converting dictionary to json serialized: {inventory}")

        item_dict = inventory.model_dump()
        logger.info(f"Creating transaction: {item_dict}")

        # Serialize json message
        serialized_item = custom_json_serializer(item_dict)

        # Send message to Kafka
        await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, serialized_item)
        logger.info(f"Transaction '{inventory}' sent to Kafka topic '{
                    settings.KAFKA_INVENTORY_TOPIC}'")

        # Flush the producer to ensure all messages are sent
        await producer.flush()

        # Close the producer to release resources
        await producer.stop()

        return inventory
    except Exception as e:
        logger.error(f"Failed to create transaction: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create transaction")


@router.patch('/update/{inventory_id}', response_model=InventoryTransResponse)
async def update(
    inventory_id: int,
    inventory: InventoryTransUpdate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):

    with get_session() as session:
        trans: InventoryTransaction = session.get(
            InventoryTransaction, inventory_id)
        if not trans:
            raise HTTPException(
                status_code=404, detail="Transaction not found")

        try:
            # convert sqlmodel to dict
            item_dict: dict = inventory.model_dump(exclude_unset=True)
            item_dict["id"] = inventory_id

            # Convert item to json serialized message
            logger.info(
                f"Converting dictionary to json serialized: {inventory}")

            item_dict = inventory.model_dump()
            logger.info(f"Updating transaction: {item_dict}")

            # Serialize json message
            serialized_item = custom_json_serializer(item_dict)

            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, serialized_item)
            logger.info(f"Transaction '{inventory}' with ID '{inventory_id}' sent to Kafka topic '{
                        settings.KAFKA_INVENTORY_TOPIC}'")

            # Update product values, only for response purpose
            for key, value in item_dict.items():
                # set new values according to key
                setattr(inventory, key, value)

            return inventory
        except Exception as e:
            logger.error(f"Failed to update transaction with ID '{
                inventory_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update transaction")


@router.delete('/delete/{inventory_id}')
async def delete(
    inventory_id: int,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    with get_session() as session:
        inventory: InventoryTransaction = session.get(
            InventoryTransaction, inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=404, detail="Transaction not found")

        try:
            # Convert product ID to json message
            item_dict: dict = {"id": inventory_id}
            logger.info(f"Deleting transaction with ID: {item_dict.get('id')}")

            # Serialize json message
            serialized_item = custom_json_serializer(item_dict)
            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC_DELETE, serialized_item)
            logger.info(f"Transaction ID '{inventory_id}' sent to Kafka topic '{
                        settings.KAFKA_INVENTORY_TOPIC_DELETE}' for deletion")

            return {"message": f"Transaction ID '{inventory_id}' has been requested for deletion"}
        except Exception as e:
            logger.error(f"Failed to send transaction delete message with ID '{
                         inventory_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to send deletion message")
