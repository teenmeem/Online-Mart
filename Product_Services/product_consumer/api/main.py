import logging
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from common_files.database import create_db_and_tables
from api.kafka_services import\
    consume_insert_update_messages, consume_delete_messages, consume_inventory_update_messages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    An asynchronous context manager that sets up the database tables and starts the Kafka consumer tasks.

    Args:
        app (FastAPI): The FastAPI application.

    Yields:
        None: Yields nothing.

    Raises:
        Exception: If an error occurs during the setup.
    """
    try:
        logger.info('Starting database setup...')
        create_db_and_tables()
        logger.info("Database tables created successfully.")

        # Start Kafka consumer tasks
        consumer_task_insert_update = asyncio.create_task(
            consume_insert_update_messages())

        consumer_task_delete = asyncio.create_task(consume_delete_messages())

        consume_task_inventory_update = asyncio.create_task(
            consume_inventory_update_messages())
        yield

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

    finally:
        logger.info('Shutting down Kafka consumer tasks...')
        consumer_task_insert_update.cancel()
        consumer_task_delete.cancel()
        consume_task_inventory_update.cancel()

        await asyncio.gather(consumer_task_insert_update, consumer_task_delete, consume_task_inventory_update,
                             return_exceptions=True)
        logger.info('Kafka consumer tasks stopped.')

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="PostgreSQL DB Service",
    version='1.0.0'
)
