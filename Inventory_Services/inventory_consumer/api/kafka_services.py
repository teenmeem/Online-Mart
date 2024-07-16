from aiokafka import AIOKafkaConsumer
from common_files import settings
from common_files.json_custom_serialization import custom_json_deserializer
from api.db_operations import insert_into_db, update_into_db_nused, delete_from_db
from typing import Any
import asyncio
import logging

logger = logging.getLogger(__name__)


async def consume_insert_update_messages():
    """Asynchronously consume orders from Kafka topic and store them in the database."""
    consumer = await consumer_start(
        settings.KAFKA_INVENTORY_TOPIC, settings.KAFKA_INVENTORY_CONSUMER_GROUP_ID)
    try:
        async for msg in consumer:
            if msg.value:
                try:
                    # Deserialize back to original format
                    deserialized_data = custom_json_deserializer(
                        msg.value.decode('utf-8'))
                    logger.info(f"Received message with Deserialized: {
                                deserialized_data}")

                    trans_id = deserialized_data.get("id")
                    if trans_id:  # Check for Updation
                        logger.info(
                            f"Received update request for transaction ID: {
                                trans_id}"
                        )
                        try:
                            await update_into_db_nused(trans_id, deserialized_data)
                        except Exception as e:
                            logger.error(f"Failed to update transaction: {e}")

                    else:
                        logger.info(
                            f"Received insert request of transaction : {deserialized_data}")

                        try:
                            await insert_into_db(deserialized_data)
                        except Exception as e:
                            logger.error(f"Failed to insert transaction: {e}")

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
        settings.KAFKA_INVENTORY_TOPIC_DELETE, settings.KAFKA_INVENTORY_CONSUMER_DELETE_GROUP_ID)

    try:
        async for msg in consumer:
            try:

                deserialized_data = custom_json_deserializer(
                    msg.value.decode('utf-8'))
                logger.info(f"Received message with Deserialized: {
                            deserialized_data}")
                trans_id = deserialized_data.get("id")

                logger.info(
                    f"Received delete request for transaction ID: {trans_id}")

                try:
                    await delete_from_db(trans_id)
                except Exception as e:
                    logger.error(f"Failed to delete product: {e}")

            except Exception as e:
                logger.error(f"Failed to process message: {e}")
    finally:
        await consumer.stop()


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
