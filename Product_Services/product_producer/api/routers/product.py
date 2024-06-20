from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from aiokafka import AIOKafkaProducer
from common_files.product_pb2 import Proto_Product_Delete
from common_files.product_model import Product, ProductCreate, ProductUpdate, ProductResponse
from common_files import settings
from common_files.database import get_session
from api.kafka_services import kafka_producer
from api.dict_to_protopub import dict_to_protobuf
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/create_product')
async def create_product(
    item: ProductCreate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    try:
        # Convert item to protobuf message
        logger.info(f"Converting dictionary to protobuf: {item}")
        product_proto = dict_to_protobuf(item.model_dump())
        logger.info(f"Creating product: {product_proto}")

        # Serialize protobuf message
        serialized_item = product_proto.SerializeToString()

        # Send message to Kafka
        await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, serialized_item)
        logger.info(f"Product '{item.name}' '{item.description}' sent to Kafka topic '{
                    settings.KAFKA_PRODUCT_TOPIC}'")

        return item
    except Exception as e:
        logger.error(f"Failed to create product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")


@router.patch('/update_product/{product_id}', response_model=ProductResponse)
async def update_product(
    product_id: int,
    item: ProductUpdate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # convert sqlmodel to dict
            item_dict = item.model_dump(exclude_unset=True)
            item_dict["id"] = product_id

            # Convert item to protobuf message
            logger.info(
                f"Converted dictionary to protobuf:{item_dict}")
            product_proto = dict_to_protobuf(item_dict)
            logger.info(f"Updating product: {product_proto}")

            # Serialize protobuf message
            serialized_item = product_proto.SerializeToString()

            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, serialized_item)
            logger.info(f"Product '{item}' with ID '{product_id}' sent to Kafka topic '{
                        settings.KAFKA_PRODUCT_TOPIC}'")

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


@ router.delete('/delete_product/{product_id}')
async def delete_product(
    product_id: int,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # Convert product ID to protobuf message
            item_proto = Proto_Product_Delete(id=product_id)
            logger.info(f"Deleting product with ID: {product_id}")

            # Serialize protobuf message
            serialized_item = item_proto.SerializeToString()

            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC_DELETE, serialized_item)
            logger.info(f"Product with ID '{product_id}' sent to Kafka topic '{
                        settings.KAFKA_PRODUCT_TOPIC_DELETE}' for deletion")

            return {"message": f"Product with ID '{product_id}' has been requested for deletion"}
        except Exception as e:
            logger.error(f"Failed to send product delete message with ID '{
                         product_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to send deletion message")
