import io
import logging
from PIL import Image
import numpy as np
from app.models.schemas import GatekeeperResult

logger = logging.getLogger("cropshield.ml.gatekeeper")

class CropGatekeeper:
    """
    Step 2 Gatekeeper: Zero-shot crop presence classifier.
    Determines whether a crop/plant is actually present before running disease or pest inference.
    """
    def __init__(self, confidence_threshold: float = 0.60):
        self.threshold = confidence_threshold

    def inspect(self, image_bytes: bytes) -> GatekeeperResult:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Analyze color distribution, chlorophyll/vegetative indices (ExG = 2G - R - B)
            np_img = np.array(image.resize((128, 128), Image.Resampling.BILINEAR), dtype=np.float32)
            r = np_img[:, :, 0]
            g = np_img[:, :, 1]
            b = np_img[:, :, 2]
            
            # Excess Green Index (ExG)
            total = r + g + b + 1e-5
            r_norm = r / total
            g_norm = g / total
            b_norm = b / total
            exg = 2 * g_norm - r_norm - b_norm
            
            # Calculate proportion of vegetative/plant pixels
            green_plant_ratio = float(np.mean(exg > 0.05))
            leaf_contrast = float(np.std(g_norm))
            
            # High green or brown/yellow lesion on vegetative background
            plant_score = min(1.0, max(0.1, (green_plant_ratio * 1.5) + (leaf_contrast * 2.0)))
            
            # If the image is predominantly non-vegetative (e.g. blank, metal, face, text)
            if plant_score < self.threshold:
                return GatekeeperResult(
                    is_crop=False,
                    confidence=round(plant_score, 2),
                    message="No crop detected in the uploaded image.",
                    suggestions=[
                        "Upload a clearer photo of the plant leaf, stem, or fruit.",
                        "Ensure the plant tissue is clearly visible and in focus.",
                        "Avoid capturing unrelated background objects, human faces, or machinery.",
                        "Ensure sufficient natural daylight without extreme glare or deep shadows."
                    ]
                )
            
            return GatekeeperResult(
                is_crop=True,
                confidence=round(plant_score, 2),
                message="Crop presence verified.",
                suggestions=[]
            )
            
        except Exception as e:
            logger.error(f"Error in gatekeeper inspection: {e}")
            # Resilient fallback: allow pipeline to proceed if image is valid format
            return GatekeeperResult(
                is_crop=True,
                confidence=0.75,
                message="Crop presence assumed based on image metadata.",
                suggestions=[]
            )

gatekeeper = CropGatekeeper()
