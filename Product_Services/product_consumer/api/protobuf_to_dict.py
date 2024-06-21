from common_files.product_pb2 import Proto_Product


def protobuf_to_dict(proto_obj: Proto_Product) -> dict:
    """
    Convert a Protobuf object to a dictionary.

    Args:
        proto_obj (Proto_Product): The Protobuf object to convert.

    Returns:
        dict: A dictionary representation of the Protobuf object. The keys are the field names and the values are the field values.
            Only fields with non-default values are included in the dictionary.

    """
    result: dict = {}
    for field in proto_obj.DESCRIPTOR.fields:
        value = getattr(proto_obj, field.name)
        if value is not None and value != field.default_value:
            result[field.name] = value
    return result
