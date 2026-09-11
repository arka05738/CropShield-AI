"""Pest image preprocessing helpers."""
from __future__ import annotations

import io
from typing import Tuple

from PIL import Image


def bytes_to_rgb_pil(image_bytes: bytes) -> Image.Image:
    """Decode upload bytes to RGB PIL image."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def image_size(image_bytes: bytes) -> Tuple[int, int]:
    img = bytes_to_rgb_pil(image_bytes)
    return int(img.width), int(img.height)
