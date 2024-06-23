from fastapi import APIRouter, HTTPException
from sqlmodel import select, func
from common_files.product_model import Product, ProductResponse
from common_files.database import get_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
def read_products():
    """
    Retrieves all products from the database and returns them as a list of `ProductResponse` objects.

    :return: A list of `ProductResponse` objects representing all products in the database.
    :raises HTTPException: If no products are found in the database.
    """
    with get_session() as session:
        products: list[Product] = session.exec(select(Product)).all()
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        return products


@router.get("/item/{product_id}", response_model=ProductResponse)
def read_product_by_id(product_id: int):
    """
    Retrieves a product from the database by its ID.

    Parameters:
        product_id (int): The ID of the product to retrieve.

    Returns:
        ProductResponse: The product with the specified ID.

    Raises:
        HTTPException: If the product with the specified ID is not found.
    """
    with get_session() as session:
        product: Product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product


@router.get("/user/{user_id}", response_model=list[ProductResponse])
def read_product_by_user(user_id: int):
    """
    Retrieves products from the database based on the provided user_id.

    Parameters:
        user_id (int): The ID of the user whose products are being retrieved.

    Returns:
        list[Product]: A list of products associated with the specified user.

    Raises:
        HTTPException: If no products are found for the user.
    """
    with get_session() as session:
        products: list[Product] = session.exec(select(Product).where(
            Product.user_id == user_id)).all()

        logger.info(f"Found {len(products)} products for user {user_id}")
        if not products:
            raise HTTPException(status_code=404, detail="Product not found")
        return products


@router.get("/category/{category}", response_model=list[ProductResponse])
def read_product_by_category(category: str):
    """
    Retrieves a list of products from the database based on the provided category.

    Parameters:
        category (str): The category of products to retrieve.

    Returns:
        list[ProductResponse]: A list of ProductResponse objects representing the products
        matching the provided category.

    Raises:
        HTTPException: If no products are found for the specified category.
    """
    with get_session() as session:
        products: list[Product] = session.exec(select(Product).where(
            func.upper(Product.category) == category.upper())).all()

        logger.info(f"Found {len(products)} products for {category}")
        if not products:
            raise HTTPException(status_code=404, detail="Product not found")
        return products
