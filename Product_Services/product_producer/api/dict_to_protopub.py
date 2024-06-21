from common_files.product_pb2 import Proto_Product
import logging

logger = logging.getLogger(__name__)


def dict_to_protobuf(item_dict: dict) -> Proto_Product:
    """
    Convert a dictionary to a Protobuf message.

    Args:
        item_dict (dict): The dictionary containing the fields and values to be converted.

    Returns:
        Proto_Product: A Protobuf message constructed from the dictionary.

    """
    product_proto = Proto_Product()

    for field, value in item_dict.items():
        # Check if the key matches a field in the message
        if hasattr(product_proto, field):
            setattr(product_proto, field, value)
    return product_proto
