"""Image helpers for Hugging Face disease classifiers."""
from __future__ import annotations

import io
from PIL import Image


def bytes_to_rgb_pil(image_bytes: bytes) -> Image.Image:
    """Open upload bytes as RGB PIL image (no DenseNet-specific transforms)."""
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")
