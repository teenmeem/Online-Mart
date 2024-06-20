from common_files.product_pb2 import Proto_Product
import logging

logger = logging.getLogger(__name__)


def dict_to_protobuf(item_dict: dict) -> Proto_Product:
    """
    Convert a dictionary to a Protobuf object.

    Args:
        proto_obj (GeneratedProtocolMessageType): The Protobuf object to populate.
        values_dict (dict): The dictionary containing the values.

    Returns:
        proto_obj: The populated Protobuf object.
    """
    product_proto = Proto_Product()
    # item_dict = values_dict.model_dump()

    for field, value in item_dict.items():
        # Check if the key matches a field in the message
        if hasattr(product_proto, field):
            setattr(product_proto, field, value)
    return product_proto
