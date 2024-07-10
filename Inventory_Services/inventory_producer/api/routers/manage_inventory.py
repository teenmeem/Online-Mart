from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from aiokafka import AIOKafkaProducer
# from common_files.inventory_trans_pb2 import Proto_Inventory, Proto_Inventory_Delete
from common_files.inventory_trans_model import InventoryTransaction, InventoryTransCreate, InventoryTransUpdate, InventoryTransResponse
from common_files import settings
from common_files.database import get_session
from api.kafka_services import kafka_producer
from api.dict_to_json import custom_json_serializer
import logging
import json

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


@router.patch('/update/{product_id}', response_model=InventoryTransResponse)
async def update(
    product_id: int,
    item: InventoryTransUpdate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):

    with get_session() as session:
        product: InventoryTransaction = session.get(
            InventoryTransaction, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # convert sqlmodel to dict
            item_dict: dict = item.model_dump(exclude_unset=True)
            item_dict["id"] = product_id

            # Convert item to protobuf message
            logger.info(
                f"Converted dictionary to protobuf:{item_dict}")
            inventory_proto: Proto_Inventory = dict_to_protobuf(item_dict)
            logger.info(f"Updating product: {inventory_proto}")

            # Serialize protobuf message
            serialized_item = inventory_proto.SerializeToString()

            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, serialized_item)
            logger.info(f"Product '{item}' with ID '{product_id}' sent to Kafka topic '{
                        settings.KAFKA_INVENTORY_TOPIC}'")

            # Update product values, only for response purpose
            for key, value in item_dict.items():
                # set new values according to key
                setattr(product, key, value)

            return product
        except Exception as e:
            logger.error(f"Failed to update product with ID '{
                         product_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update product")


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
            # Convert product ID to protobuf message
            # item_proto: Proto_Inventory_Delete = Proto_Inventory_Delete(id=product_id)
            item_dict = {id: inventory_id}
            logger.info(f"Deleting transaction with ID: {inventory_id}")

            # Serialize protobuf message
            # serialized_item = item_proto.SerializeToString()
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
