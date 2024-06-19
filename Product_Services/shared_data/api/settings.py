
from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")

except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

BOOTSTRAP_SERVER = config("KAFKA_SERVER", cast=str)
KAFKA_INSERT_CONSUMER_GROUP_ID = config(
    "KAFKA_INSERT_CONSUMER_GROUP_ID", cast=str)
KAFKA_UPDATE_CONSUMER_GROUP_ID = config(
    "KAFKA_UPDATE_CONSUMER_GROUP_ID", cast=str)
KAFKA_DELETE_CONSUMER_GROUP_ID = config(
    "KAFKA_DELETE_CONSUMER_GROUP_ID", cast=str)

KAFKA_INSERT_PRODUCT_TOPIC = config("KAFKA_INSERT_PRODUCT_TOPIC", cast=str)
KAFKA_UPDATE_PRODUCT_TOPIC = config("KAFKA_UPDATE_PRODUCT_TOPIC", cast=str)
KAFKA_DELETE_PRODUCT_TOPIC = config("KAFKA_DELETE_PRODUCT_TOPIC", cast=str)
