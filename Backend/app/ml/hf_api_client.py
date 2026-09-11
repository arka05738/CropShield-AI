"""
Hugging Face Serverless Inference Router API Client.

Directly queries Hugging Face's router (https://router.huggingface.co/hf-inference/models/{model_id})
via lightweight HTTP requests. This eliminates the need to load 350MB+ PyTorch Vision Transformers
locally inside low-memory containers (e.g., Render 512MB RAM cap), eliminating OOM crashes and 502s.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger("cropshield.ml.hf_client")

DEFAULT_ROUTER_URL = "https://router.huggingface.co/hf-inference/models"


class HuggingFaceAPIClient:
    """HTTP client for Hugging Face Serverless Inference API."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or getattr(settings, "HF_INFERENCE_ROUTER_URL", None) or DEFAULT_ROUTER_URL).rstrip("/")

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/octet-stream",
            "x-wait-for-model": "true",
            "x-use-cache": "true",
        }
        token = (getattr(settings, "HF_TOKEN", "") or "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def query_classification(
        self,
        model_id: str,
        image_bytes: bytes,
        timeout: float = 25.0,
        max_retries: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Send image bytes to a Hugging Face image classification model.
        Returns: [{"label": str, "score": float}, ...]
        Raises RuntimeError on fatal errors, or returns [] if model fails.
        """
        url = f"{self.base_url}/{model_id}"
        headers = self._get_headers()

        retries = 0
        while retries <= max_retries:
            try:
                t0 = time.time()
                with httpx.Client(timeout=timeout) as client:
                    resp = client.post(url, headers=headers, content=image_bytes)

                elapsed = round(time.time() - t0, 3)

                # HTTP 200: Successful classification
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list):
                        logger.info("HF API inference success model=%s items=%d elapsed=%ss", model_id, len(data), elapsed)
                        return data
                    elif isinstance(data, dict) and "error" in data:
                        logger.warning("HF API error response: %s", data["error"])
                        return []
                    return []

                # HTTP 503: Model is loading on Hugging Face infrastructure
                if resp.status_code == 503 and retries < max_retries:
                    try:
                        info = resp.json()
                        wait_sec = min(float(info.get("estimated_time", 5.0)), 10.0)
                    except Exception:
                        wait_sec = 5.0
                    logger.info("HF model %s is warming up; waiting %.1fs (retry %d/%d)...", model_id, wait_sec, retries + 1, max_retries)
                    time.sleep(wait_sec)
                    retries += 1
                    continue

                # HTTP 401: Unauthorized (token missing or invalid)
                if resp.status_code == 401:
                    logger.warning("HF API authentication failed (401) for %s. Set HF_TOKEN in environment.", model_id)
                    return []

                # Other HTTP status
                logger.warning("HF API non-200 status for %s: %d %s", model_id, resp.status_code, resp.text[:200])
                return []

            except httpx.TimeoutException:
                logger.warning("HF API timeout (%ss) querying model %s", timeout, model_id)
                return []
            except Exception as e:
                logger.warning("HF API request failed for %s: %s", model_id, e)
                return []

        return []


hf_api_client = HuggingFaceAPIClient()
