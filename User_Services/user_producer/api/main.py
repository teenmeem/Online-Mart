from contextlib import asynccontextmanager
from fastapi import FastAPI
# from user_service import auth
from common_files.database import create_db_and_tables
# from api.user_model import Register_User, Token, User
from api.routers import user
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
    logger.info("Tables Created")
    yield

app = FastAPI(
    lifespan=lifespan,
    title="FastAPI User Service",
    version='1.0.0'
)


@app.get('/')
async def root():
    """
    A function that handles the root endpoint of the User Microservice.

    This function is an asynchronous handler for the root endpoint of the User Microservice. It returns a JSON response containing a welcome message.

    Returns:
        dict: A dictionary with a single key "message" containing the welcome message.
    """
    return {"message": "Welcome to the User Microservice"}

app.include_router(user.router, prefix="/user", tags=["Manage Users"])
