from datetime import datetime
from typing import Any
import json
import logging

logger = logging.getLogger(__name__)


def custom_json_deserializer(data: str) -> dict[str, Any]:
    try:
        return json.loads(data, object_hook=custom_object_hook)
    except Exception as e:
        logger.error(f"Error deserializing object: {e}")
        raise


def custom_object_hook(dct: dict[str, Any]) -> dict[str, Any]:
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                dct[key] = datetime.fromisoformat(value)
            except ValueError:
                pass  # Keep the original value if it's not a date string
    return dct
