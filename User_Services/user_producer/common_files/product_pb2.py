# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: product.proto
# Protobuf Python Version: 5.27.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    0,
    '',
    'product.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rproduct.proto\"\xb2\x01\n\rProto_Product\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x10\n\x08\x63\x61tegory\x18\x04 \x01(\t\x12\r\n\x05\x62rand\x18\x05 \x01(\t\x12\r\n\x05price\x18\x06 \x01(\x02\x12\x10\n\x08\x63urrency\x18\x07 \x01(\t\x12\r\n\x05stock\x18\x08 \x01(\x05\x12\x10\n\x08location\x18\t \x01(\t\x12\x0f\n\x07user_id\x18\n \x01(\x05\"\"\n\x14Proto_Product_Delete\x12\n\n\x02id\x18\x01 \x01(\x05\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'product_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PROTO_PRODUCT']._serialized_start=18
  _globals['_PROTO_PRODUCT']._serialized_end=196
  _globals['_PROTO_PRODUCT_DELETE']._serialized_start=198
  _globals['_PROTO_PRODUCT_DELETE']._serialized_end=232
# @@protoc_insertion_point(module_scope)
