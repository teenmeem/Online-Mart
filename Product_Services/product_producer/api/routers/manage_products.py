from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func
from typing import Annotated
from aiokafka import AIOKafkaProducer
from common_files.product_pb2 import Proto_Product, Proto_Product_Delete
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
    """
    Create a new product by sending a message to Kafka.

    Args:
        item (ProductCreate): The product to be created.
        producer (AIOKafkaProducer): The Kafka producer used to send the message.

    Raises:
        HTTPException: If a product with the same product code already exists.
        HTTPException: If an error occurs during the creation process.

    Returns:
        ProductCreate: The created product.
    """
    with get_session() as session:
        product: Product = session.exec(select(Product).where(
            func.upper(Product.prod_code) == item.prod_code.upper())).first()
    if product:
        raise HTTPException(
            status_code=409, detail="Product already exists")

    try:

        # Convert item to protobuf message
        logger.info(f"Converting dictionary to protobuf: {item}")

        product_proto: Proto_Product = dict_to_protobuf(item.model_dump())
        logger.info(f"Creating product: {product_proto}")

        # Serialize protobuf message
        serialized_item = product_proto.SerializeToString()

        # Send message to Kafka
        await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, serialized_item)
        logger.info(f"Product '{item}' sent to Kafka topic '{
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
    """
    Updates a product with the given product ID by converting the input item to a protobuf message,
    serializing it, and sending it to a Kafka topic. The function takes in the following parameters:

    - `product_id` (int): The ID of the product to be updated.
    - `item` (ProductUpdate): The updated information for the product.
    - `producer` (Annotated[AIOKafkaProducer, Depends(kafka_producer)]): The Kafka producer used to
      send the serialized product to the Kafka topic.

    Returns:
    - `ProductResponse`: The updated product.

    Raises:
    - `HTTPException` with status code 404 if the product with the given ID is not found.
    - `HTTPException` with status code 500 if an error occurs during the update process.
    """
    with get_session() as session:
        product: Product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # convert sqlmodel to dict
            item_dict: dict = item.model_dump(exclude_unset=True)
            item_dict["id"] = product_id

            # Convert item to protobuf message
            logger.info(
                f"Converted dictionary to protobuf:{item_dict}")
            product_proto: Proto_Product = dict_to_protobuf(item_dict)
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
    """
    Deletes a product based on the provided product ID by converting the ID to a protobuf message,
    serializing it, and sending it to a Kafka topic for deletion. The function takes in the following parameters:

    - `product_id` (int): The ID of the product to be deleted.
    - `producer` (Annotated[AIOKafkaProducer, Depends(kafka_producer)]): The Kafka producer used for sending the deletion message.

    Returns:
    - A dictionary containing a message confirming the deletion request.

    Raises:
    - HTTPException with status code 404 if the product with the given ID is not found.
    - HTTPException with status code 500 if an error occurs during the deletion process.
    """
    with get_session() as session:
        product: Product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # Convert product ID to protobuf message
            item_proto: Proto_Product_Delete = Proto_Product_Delete(
                id=product_id)
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
