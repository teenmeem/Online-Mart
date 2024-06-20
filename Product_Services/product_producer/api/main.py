from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.kafka_services import create_topic
from api.routers.product import router as product_router
import logging

logging.basicConfig(level=logging.INFO)  # Set logging level
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    return {"message": "Welcome to the Product Microservice"}

app.include_router(product_router, prefix="/product", tags=["Products"])
