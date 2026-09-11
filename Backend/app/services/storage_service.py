import os
import uuid
import logging
import io
from pathlib import Path
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

logger = logging.getLogger("cropshield.storage")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "application/octet-stream",  # browsers sometimes omit type; content still verified via PIL
}

# Magic-byte prefixes for common image formats
_MAGIC = (
    (b"\xff\xd8\xff", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"RIFF", "WEBP"),  # WEBP is RIFF....WEBP
)


class StorageService:
    """Local image storage with extension, MIME, magic-byte, and PIL validation."""

    def __init__(self):
        self.upload_dir = os.path.abspath(settings.UPLOAD_DIR)
        os.makedirs(self.upload_dir, exist_ok=True)

    def _looks_like_image(self, content: bytes) -> bool:
        if content.startswith(b"\xff\xd8\xff"):
            return True
        if content.startswith(b"\x89PNG\r\n\x1a\n"):
            return True
        if content.startswith(b"RIFF") and b"WEBP" in content[:16]:
            return True
        return False

    async def save_image(self, file: UploadFile) -> tuple[str, bytes]:
        raw_name = file.filename or "upload.jpg"
        # Strip any path components (path traversal / absolute paths)
        filename = Path(raw_name).name
        if not filename or filename in {".", ".."} or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename.",
            )

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format '{ext}'. Please upload JPG, JPEG, PNG, or WebP.",
            )

        declared = (file.content_type or "").lower().strip()
        if declared and declared not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported Content-Type '{declared}'. Image uploads only.",
            )

        content = await file.read()
        max_bytes = settings.MAX_UPLOAD_BYTES
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image exceeds maximum size limit of {max_bytes // (1024 * 1024)}MB.",
            )
        if len(content) < 32:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file is empty or invalid.",
            )

        # Reject obvious executables / scripts disguised by extension
        if content[:2] in (b"MZ", b"#!") or content[:4] == b"\x7fELF":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content is not a valid image.",
            )
        if not self._looks_like_image(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File magic bytes do not match an allowed image format.",
            )

        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
            with Image.open(io.BytesIO(content)) as img:
                if img.format not in ALLOWED_FORMATS:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Decoded image format '{img.format}' is not allowed.",
                    )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or malformed image content.",
            )

        file_id = f"{uuid.uuid4().hex}{ext}"
        target_path = os.path.abspath(os.path.join(self.upload_dir, file_id))
        # Ensure resolved path stays inside upload directory
        if not target_path.startswith(self.upload_dir + os.sep) and target_path != self.upload_dir:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid storage path.",
            )

        try:
            with open(target_path, "wb") as f:
                f.write(content)
            return f"/uploads/{file_id}", content
        except Exception as e:
            logger.error("Failed to persist uploaded image: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store uploaded image.",
            )


storage_service = StorageService()
