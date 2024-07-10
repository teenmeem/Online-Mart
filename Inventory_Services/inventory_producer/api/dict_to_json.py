from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


def custom_json_serializer(obj: dict) -> bytes:
    try:
        return json.dumps(obj, cls=CustomJSONEncoder).encode('utf-8')
    except Exception as e:
        logger.error(f"Error serializing object: {e}")
        raise


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        return super().default(obj)
