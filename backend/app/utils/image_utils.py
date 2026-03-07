import base64
from typing import Tuple

import cv2
import numpy as np
from fastapi import HTTPException


def strip_data_uri_prefix(data: str) -> str:
    if "," in data and data.split(",", 1)[0].startswith("data:"):
        return data.split(",", 1)[1]
    return data


def decode_base64_image(image_base64: str) -> np.ndarray:
    """Decode a base64 image string into an OpenCV-compatible ndarray."""

    try:
        image_bytes = base64.b64decode(strip_data_uri_prefix(image_base64), validate=True)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid base64 image payload") from exc

    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None or image.size == 0:
        raise HTTPException(status_code=400, detail="Unable to decode image data")

    return image


def image_shape(image: np.ndarray) -> Tuple[int, int, int]:
    return image.shape
