from common_files.product_pb2 import Proto_Product

def protobuf_to_dict(proto_obj: Proto_Product) -> dict:
    """
    Convert a Protobuf object to a dictionary.
    """
    result = {}
    for field in proto_obj.DESCRIPTOR.fields:
        value = getattr(proto_obj, field.name)
        if value is not None and value != field.default_value:
            result[field.name] = value
    return result
