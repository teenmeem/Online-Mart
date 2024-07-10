from common_files.inventory_trans_pb2 import Proto_Inventory
import logging

logger = logging.getLogger(__name__)


def dict_to_protobuf(dict_obj: dict) -> Proto_Inventory:
    proto_obj = Proto_Inventory()

    for field, value in dict_obj.items():
        # Check if the key matches a field in the message
        if hasattr(proto_obj, field):
            setattr(proto_obj, field, value)
    return proto_obj
