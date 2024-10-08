import logging
import asyncio
from aiokafka import AIOKafkaConsumer
from common_files.product_pb2 import Proto_Product, Proto_Product_Delete
from common_files import settings
from common_files.json_custom_serialization import custom_json_deserializer
from api.protobuf_to_dict import protobuf_to_dict
from api.db_operations import\
    insert_product_into_db, update_product_in_db, delete_product_from_db, update_product_bal_in_db


logger = logging.getLogger(__name__)


async def consume_insert_update_messages():
    """Asynchronously consume orders from Kafka topic and store them in the database."""
    consumer = await consumer_start(
        settings.KAFKA_PRODUCT_TOPIC, settings.KAFKA_PRODUCT_CONSUMER_GROUP_ID)
    try:
        async for msg in consumer:
            if msg.value:
                try:
                    item_proto = Proto_Product()
                    item_proto.ParseFromString(msg.value)

                    logger.info(
                        f"Received item:  {item_proto}")
                    # Convert item to dictionary
                    item: dict = protobuf_to_dict(item_proto)

                    # Call the service to handle product deletion
                    product_id = item_proto.id
                    if product_id:  # Check for Updation
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
    consumer = await consumer_start(
        settings.KAFKA_PRODUCT_TOPIC_DELETE, settings.KAFKA_PRODUCT_CONSUMER_DELETE_GROUP_ID)

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
# ---------------


async def consumer_start(topic: str, group_id: str):
    MAX_RETRIES = 5
    RETRY_INTERVAL = 10

    retries = 0

    while retries < MAX_RETRIES:
        try:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=settings.BOOTSTRAP_SERVER,
                group_id=group_id
            )

            await consumer.start()
            logger.info("Consumer started successfully.")
            return consumer

        except Exception as e:
            retries += 1
            logger.error(f"Error starting consumer, retry {
                retries}/{MAX_RETRIES}: {e}")
            if retries < MAX_RETRIES:
                await asyncio.sleep(RETRY_INTERVAL)
            else:
                logger.error("Max retries reached. Could not start consumer.")
                return


async def consume_inventory_update_messages():
    """Asynchronously consume inventory from Kafka topic and store them in the database."""
    consumer = await consumer_start(
        settings.KAFKA_PRODUCT_BAL_TOPIC, settings.KAFKA_PRODUCT_BAL_CONSUMER_GROUP_ID)
    try:
        async for msg in consumer:
            if msg.value:
                try:
                    # Deserialize back to original format
                    deserialized_data = custom_json_deserializer(
                        msg.value.decode('utf-8'))
                    logger.info(f"Received message with Deserialized: {
                                deserialized_data}")

                    product_id = deserialized_data.get("product_id")

                    if product_id:  # Check for Updation
                        logger.info(
                            f"Received update request for transaction ID: {
                                product_id}"
                        )
                        try:
                            await update_product_bal_in_db(product_id, deserialized_data)
                        except Exception as e:
                            logger.error(f"Failed to update product: {e}")

                except KeyError as e:
                    logger.error(f"Missing expected key in message: {e}")
            else:
                logger.warning("Received message with no value")
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")
