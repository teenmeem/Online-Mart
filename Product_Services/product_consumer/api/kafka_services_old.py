from aiokafka import AIOKafkaConsumer
from common_files.product_pb2 import Proto_Product, Proto_Product_Delete
from common_files import settings
from api.protobuf_to_dict import protobuf_to_dict
from api.db_operations import insert_product_into_db, update_product_in_db, delete_product_from_db
import asyncio
import logging

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
RETRY_INTERVAL = 10


async def consume_insert_update_messages():
    """Asynchronously consume orders from Kafka topic and store them in the database."""
    retries = 0

    while retries < MAX_RETRIES:
        try:
            consumer = AIOKafkaConsumer(
                settings.KAFKA_PRODUCT_TOPIC,
                bootstrap_servers=settings.BOOTSTRAP_SERVER,
                group_id=settings.KAFKA_PRODUCT_CONSUMER_GROUP_ID
            )

            await consumer.start()
            logger.info("Consumer started successfully.")
            break
        except Exception as e:
            retries += 1
            logger.error(f"Error starting consumer, retry {
                         retries}/{MAX_RETRIES}: {e}")
            if retries < MAX_RETRIES:
                await asyncio.sleep(RETRY_INTERVAL)
            else:
                logger.error("Max retries reached. Could not start consumer.")
                return
# ---------------

    try:
        async for msg in consumer:
            if msg.value:
                try:
                    item_proto = Proto_Product()
                    item_proto.ParseFromString(msg.value)

                    logger.info(f"Received item:  {item_proto}")
                    # Convert item to dictionary
                    item: dict = protobuf_to_dict(item_proto)
                    # Call the service to handle product deletion

                    if item_proto.id:  # Check for Updation
                        product_id = item_proto.id
                        logger.info(
                            f"Received update request for product ID: {
                                product_id}"
                        )
                        try:
                            await update_product_in_db(product_id, item)
                        except Exception as e:
                            logger.error(f"Failed to update product: {e}")

                    else:
                        logger.info(
                            f"Received insert request of product : {item}")

                        try:
                            await insert_product_into_db(item)
                        except Exception as e:
                            logger.error(f"Failed to insert product: {e}")

                except KeyError as e:
                    logger.error(f"Missing expected key in message: {e}")
            else:
                logger.warning("Received message with no value")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


async def consume_delete_messages():
    """	Asynchronously consumes delete messages from Kafka topic and handles product deletion."""
    retries = 0

    while retries < MAX_RETRIES:
        try:
            consumer = AIOKafkaConsumer(
                settings.KAFKA_PRODUCT_TOPIC_DELETE,
                bootstrap_servers=settings.BOOTSTRAP_SERVER,
                group_id=settings.KAFKA_PRODUCT_CONSUMER_DELETE_GROUP_ID
            )

            await consumer.start()
            logger.info("Consumer started successfully.")
            break
        except Exception as e:
            retries += 1
            logger.error(f"Error starting consumer, retry {
                         retries}/{MAX_RETRIES}: {e}")
            if retries < MAX_RETRIES:
                await asyncio.sleep(RETRY_INTERVAL)
            else:
                logger.error("Max retries reached. Could not start consumer.")
                return
# ---------------

    try:
        async for msg in consumer:
            try:
                item_proto = Proto_Product_Delete()
                item_proto.ParseFromString(msg.value)

                product_id: int = item_proto.id
                logger.info(
                    f"Received delete request for product ID: {product_id}")

                # Call the service to handle product deletion
                try:
                    await delete_product_from_db(product_id)
                except Exception as e:
                    logger.error(f"Failed to delete product: {e}")

            except Exception as e:
                logger.error(f"Failed to process message: {e}")
    finally:
        await consumer.stop()
