from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from common_files import settings
import logging

logger = logging.getLogger(__name__)


async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.BOOTSTRAP_SERVER)

    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


async def create_topic():
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=settings.BOOTSTRAP_SERVER)

    await admin_client.start()
    topic_list = [NewTopic(name=settings.KAFKA_PRODUCT_TOPIC,
                           num_partitions=2, replication_factor=1),
                  NewTopic(name=settings.KAFKA_PRODUCT_TOPIC_DELETE,
                           num_partitions=2, replication_factor=1)]

    try:
        await admin_client.create_topics(new_topics=topic_list, validate_only=False)
        logger.info(
            f"Topics created successfully")
    except Exception as e:
        logger.error(f"Failed to create topics : {e}")
    finally:
        await admin_client.close()
