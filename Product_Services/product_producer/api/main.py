from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.kafka_services import create_topic
from api.routers.manage_products import router as manage_products
from api.routers.read_products import router as read_products
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
    await create_topic()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="FastAPI Producer Service",
    version='1.0.0'
)


@app.get('/')
async def root():
    """
    A function that handles the root endpoint of the Product Microservice.

    This function is an asynchronous handler for the root endpoint of the Product Microservice. It returns a JSON response containing a welcome message.

    Returns:
        dict: A dictionary with a single key "message" containing the welcome message.
    """
    return {"message": "Welcome to the Product Microservice"}

app.include_router(manage_products, prefix="/product",
                   tags=["Manage Products"])
app.include_router(read_products, prefix="/product", tags=["Read Products"])
