import logging
from typing import List, Optional, Tuple
from app.models.schemas import DiseasePrediction, PestDetectionItem, WeatherMetrics

logger = logging.getLogger("cropshield.ml.fusion")


class RiskFusionEngine:
    """
    Combines disease (when available), pest, and weather into an explainable risk score.
    """

    def calculate_risk(
        self,
        crop: str,
        disease: DiseasePrediction,
        pests: List[PestDetectionItem],
        weather: Optional[WeatherMetrics] = None,
    ) -> Tuple[str, int, str]:

        if disease.pathogen_type == "Healthy" and len(pests) == 0:
            return (
                "Healthy",
                12,
                "Crop canopy shows vigorous vegetative growth with no visible foliar lesions or pest clusters.",
            )

        disease_unavailable = (
            disease.inference_mode == "unavailable" or disease.confidence is None
        )

        if disease_unavailable and not pests:
            return "Unknown", 0, "Disease model unavailable; risk not estimated from disease."

        score = 0.0
        explanations: List[str] = []
        conf = float(disease.confidence or 0.0)
        disease_name = disease.disease or disease.display_label or "Unknown"

        if disease_unavailable:
            explanations.append("Disease model unavailable — risk based on pest/weather signals only.")
        elif disease.pathogen_type != "Healthy":
            if disease.pathogen_type == "Fungal":
                score += 40 * conf
                explanations.append(f"{disease_name} detected ({int(conf * 100)}% confidence)")
            elif disease.pathogen_type == "Bacterial":
                score += 42 * conf
                explanations.append(f"Active bacterial pathogen '{disease_name}' identified")
            elif disease.pathogen_type == "Viral":
                score += 45 * conf
                explanations.append(
                    f"Severe viral condition '{disease_name}' with systemic transmission risk"
                )
            else:
                score += 25 * conf
                explanations.append(f"{disease_name} detected")

        if pests:
            pest_names = [p.name for p in pests]
            pest_conf = max(p.confidence for p in pests)
            pest_points = min(35, len(pests) * 18 * pest_conf)
            score += pest_points
            explanations.append(
                f"{len(pests)} pest infestation cluster(s) observed ({', '.join(pest_names)})"
            )

        if weather:
            if weather.relative_humidity > 80:
                score += 15
                explanations.append(
                    f"Elevated relative humidity ({weather.relative_humidity:.0f}%) accelerates spore germination"
                )
            elif weather.relative_humidity > 65:
                score += 8

            if weather.precipitation > 2.0:
                score += 5
                explanations.append("Recent rainfall promotes pathogen splash dispersal")

        final_score = int(min(100, max(5 if not disease_unavailable else 0, score)))
        if disease_unavailable and not pests and not weather:
            final_score = 0

        if final_score >= 80:
            level = "Critical"
        elif final_score >= 65:
            level = "High Risk"
        elif final_score >= 40:
            level = "Moderate Risk"
        elif final_score >= 20:
            level = "Low Risk"
        elif disease_unavailable:
            level = "Unknown"
        else:
            level = "Healthy"

        explanation_summary = ". ".join(explanations) + "." if explanations else "No risk factors scored."
        return level, final_score, explanation_summary


risk_engine = RiskFusionEngine()
