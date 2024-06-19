from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from aiokafka import AIOKafkaProducer
from api.kafka_utils import kafka_producer
from shared_data.api import product_pb2, product_model
from api import settings
from shared_data.api.database import get_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

Product = product_model.Product
ProductCreate = product_model.ProductCreate
ProductUpdate = product_model.ProductUpdate
ProductResponse = product_model.ProductResponse


@router.post('/create_product', response_model=ProductUpdate)
async def create_product(
    item: ProductCreate,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    try:
        # Convert item to protobuf message
        item_proto = product_pb2.Product(
            name=item.name,
            description=item.description,
            price=item.price,
            stock=item.stock,
            location=item.location,
            user_id=item.user_id
        )
        logger.info(f"Creating product: {item}")

        # Serialize protobuf message
        serialized_item = item_proto.SerializeToString()

        # Send message to Kafka
        await producer.send_and_wait(settings.KAFKA_INSERT_PRODUCT_TOPIC, serialized_item)
        logger.info(f"Product '{item.name}' sent to Kafka topic '{
                    settings.KAFKA_INSERT_PRODUCT_TOPIC}'")

        return item
    except Exception as e:
        logger.error(f"Failed to create product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")


@router.put('/update_product/{product_id}', response_model=ProductUpdate)
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
            # Convert item to protobuf message
            item_proto = product_pb2.Product(
                id=product_id,
                name=item.name,
                description=item.description,
                price=item.price,
                stock=item.stock,
                location=item.location,
                user_id=item.user_id
            )

            logger.info(f"Updating product: {item}")

            # Serialize protobuf message
            serialized_item = item_proto.SerializeToString()

            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_UPDATE_PRODUCT_TOPIC, serialized_item)
            logger.info(f"Product '{item}' with ID '{product_id}' sent to Kafka topic '{
                        settings.KAFKA_UPDATE_PRODUCT_TOPIC}'")

            return item
        except Exception as e:
            logger.error(f"Failed to update product with ID '{
                         product_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update product")


@router.delete('/delete_product/{product_id}')
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
            item_proto = product_pb2.Product(id=product_id)
            logger.info(f"Deleting product with ID: {product_id}")

            # Serialize protobuf message
            serialized_item = item_proto.SerializeToString()

            # Send message to Kafka
            await producer.send_and_wait(settings.KAFKA_DELETE_PRODUCT_TOPIC, serialized_item)
            logger.info(f"Product with ID '{product_id}' sent to Kafka topic '{
                        settings.KAFKA_DELETE_PRODUCT_TOPIC}'")

            return {"message": f"Product with ID '{product_id}' has been requested for deletion"}
        except Exception as e:
            logger.error(f"Failed to delete product with ID '{
                         product_id}': {e}")
            raise HTTPException(
                status_code=500, detail="Failed to delete product")


@router.delete('/delete_product/{product_id}')
async def delete_product(
    product_id: int,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

    delete_proto = product_pb2.DeleteProduct(id=product_id)
    serialized_item = delete_proto.SerializeToString()

    try:
        await producer.send_and_wait(settings.KAFKA_DELETE_PRODUCT_TOPIC, serialized_item)
        logger.info(
            f"Sent product delete message for product id: {product_id}")
        return {"message": "Product delete message sent successfully"}
    except Exception as e:
        logger.error(f"Failed to send product delete message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")
