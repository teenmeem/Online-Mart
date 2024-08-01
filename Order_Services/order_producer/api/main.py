from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.kafka_services import create_topic
from api.routers.manage_order import router as manage_order
from common_files.database import create_db_and_tables
# from api.routers.read_inventory import router as read_inventory
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    An asynchronous context manager that sets up the lifespan of the FastAPI app.

    Args:
        app (FastAPI): The FastAPI application.

    Yields:
        None: Yields nothing.
    """
    logger.info("FastAPI app started...")
    create_db_and_tables()
    await create_topic()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="FastAPI Producer Service",
    version='1.0.0'
)


@app.get('/')
async def root():
    return {"message": "Welcome to the Order Microservice"}

app.include_router(manage_order, prefix="/order",
                   tags=["Order Management"])
# app.include_router(read_inventory, prefix="/inventory",
#                    tags=["Read Inventory"])
