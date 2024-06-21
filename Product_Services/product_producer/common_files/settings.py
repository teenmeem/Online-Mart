
from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")

except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

BOOTSTRAP_SERVER = config("KAFKA_SERVER", cast=str)

KAFKA_PRODUCT_CONSUMER_GROUP_ID = config(
    "KAFKA_PRODUCT_CONSUMER_GROUP_ID", cast=str)
KAFKA_PRODUCT_CONSUMER_DELETE_GROUP_ID = config(
    "KAFKA_PRODUCT_CONSUMER_DELETE_GROUP_ID", cast=str)

KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
KAFKA_PRODUCT_TOPIC_DELETE = config("KAFKA_PRODUCT_TOPIC_DELETE", cast=str)