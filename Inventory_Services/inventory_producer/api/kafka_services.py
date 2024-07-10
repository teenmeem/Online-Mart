from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaConnectionError
from common_files import settings
import asyncio
import logging

logger = logging.getLogger(__name__)


async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)

    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


MAX_RETRIES = 5
RETRY_INTERVAL = 10


async def create_topic():
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=settings.BOOTSTRAP_SERVER)

    retries = 0

    while retries < MAX_RETRIES:
        try:
            await admin_client.start()
            topic_list = [NewTopic(name=settings.KAFKA_INVENTORY_TOPIC,
                                   num_partitions=2, replication_factor=1),
                          NewTopic(name=settings.KAFKA_INVENTORY_TOPIC_DELETE,
                                   num_partitions=2, replication_factor=1)]

            try:
                await admin_client.create_topics(new_topics=topic_list, validate_only=False)
                logger.info(
                    f"Topics created successfully")
            except Exception as e:
                logger.error(f"Failed to create topics : {e}")
            finally:
                await admin_client.close()
                return

        except KafkaConnectionError:
            retries += 1
            print(f"Kafka connection failed. Retrying {
                  retries}/{MAX_RETRIES}...")
            await asyncio.sleep(RETRY_INTERVAL)

    raise Exception("Failed to connect to kafka broker after several retries")
