import json
import logging
import re
from typing import Optional, List
from groq import Groq
from app.core.config import settings
from app.models.schemas import (
    AdvisoryReport, PesticideRecommendation, FertilizerAdjustment,
    IPMStrategy, MonitoringPlan, SourceReference, WeatherMetrics,
    DiseasePrediction, PestDetectionItem
)
from app.rag.chroma_service import chroma_service
from app.rag.icar_knowledge import ICAR_POP_RECORDS

logger = logging.getLogger("cropshield.rag.advisory")

UNAVAILABLE_PESTICIDE = PesticideRecommendation(
    active_ingredient="Not specified",
    chemical_name="Verified chemical guidance unavailable",
    exact_dose_per_liter="",
    withholding_period_days=0,
    application_method="Consult local agriculture officer / KVK before applying any chemical.",
    safety_warnings=[
        "Do not apply unverified pesticide dosages.",
        "Expert validation recommended.",
    ],
    guidance_available=False,
    unavailable_reason="No sufficiently relevant curated knowledge match for this crop/disease.",
)


class AdvisoryEngine:
    """
    Agricultural RAG advisory engine.
    Recommendations must be grounded in matched curated ICAR-style records.
    If no relevant match: return expert-validation guidance — never fabricate dosages.
    """

    def __init__(self):
        self.groq_client = None
        if settings.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

    def _match_record(self, crop: str, disease: str, pathogen_type: str = "") -> Optional[dict]:
        """Require crop match (or alias); match disease with intelligent token overlap and fallback."""
        if not crop:
            return None

        def norm(text: str) -> str:
            return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

        crop_norm = norm(crop)
        disease_norm = norm(disease)
        pathogen_norm = norm(pathogen_type)

        CROP_SYNONYMS = {
            "corn": "maize",
            "maize": "corn",
            "pepper": "chilli",
            "chilli": "pepper",
            "capsicum": "pepper",
            "paddy": "rice",
            "rice": "paddy",
            "grape": "grapes",
            "grapes": "grape",
            "groundnut": "peanut",
            "peanut": "groundnut",
        }

        # Filter candidate records for this crop
        crop_recs = []
        for rec in ICAR_POP_RECORDS:
            rc_norm = norm(rec.get("crop", ""))
            if rc_norm == crop_norm or CROP_SYNONYMS.get(rc_norm) == crop_norm or CROP_SYNONYMS.get(crop_norm) == rc_norm:
                crop_recs.append(rec)

        if not crop_recs:
            return None

        # 1. Healthy check
        if "healthy" in disease_norm or "healthy" in pathogen_norm:
            for rec in crop_recs:
                if "healthy" in norm(rec.get("disease", "")):
                    return rec
            return None

        # Clean disease string (strip crop name if prefixed like "tomato septoria leaf spot")
        clean_d = disease_norm
        for c in [crop_norm, CROP_SYNONYMS.get(crop_norm, "")]:
            if c and clean_d.startswith(c):
                clean_d = clean_d[len(c):].strip()

        # 2. Exact substring match
        for rec in crop_recs:
            rec_d = norm(rec.get("disease", ""))
            if clean_d and (clean_d in rec_d or rec_d in clean_d):
                return rec

        # 3. Key disease keyword matching
        KEYWORD_MAPPINGS = {
            "septoria": ["septoria"],
            "bacterial": ["bacterial"],
            "late blight": ["late blight"],
            "early blight": ["early blight"],
            "blight": ["blight"],
            "leaf mold": ["leaf mold", "mold"],
            "target spot": ["target spot"],
            "curl": ["curl", "geminivirus", "tylcv"],
            "mosaic": ["mosaic", "tomv"],
            "mite": ["mite", "spider"],
            "rust": ["rust"],
            "blast": ["blast"],
            "anthracnose": ["anthracnose", "dieback", "fruit rot"],
            "scab": ["scab"],
            "mildew": ["mildew"],
            "rot": ["rot"],
            "spot": ["spot"],
        }

        best_rec = None
        best_score = 0

        d_words = set(clean_d.split()) - {"leaf", "spot", "plant", "crop", "disease"}
        for rec in crop_recs:
            rec_d = norm(rec.get("disease", ""))
            rec_words = set(rec_d.split()) - {"leaf", "spot", "plant", "crop", "disease"}
            for kw, aliases in KEYWORD_MAPPINGS.items():
                if any(a in clean_d for a in aliases) and any(a in rec_d for a in aliases):
                    return rec
            overlap = len(d_words & rec_words)
            if overlap > best_score:
                best_score = overlap
                best_rec = rec

        if best_rec and best_score >= 1:
            return best_rec

        # 4. Pathogen-type based grounding within the same crop family
        if "bacterial" in pathogen_norm or "bacterial" in clean_d:
            for rec in crop_recs:
                if "bacterial" in norm(rec.get("disease", "")):
                    return rec

        if "viral" in pathogen_norm or any(v in clean_d for v in ["virus", "curl", "mosaic"]):
            for rec in crop_recs:
                if any(v in norm(rec.get("disease", "")) for v in ["virus", "curl", "mosaic"]):
                    return rec

        if "fungal" in pathogen_norm or not best_rec:
            for rec in crop_recs:
                if "healthy" not in norm(rec.get("disease", "")):
                    return rec

        return crop_recs[0] if crop_recs else None

    def generate_advisory(
        self,
        crop: str,
        disease: DiseasePrediction,
        pests: List[PestDetectionItem],
        risk_level: str,
        risk_score: int,
        risk_explanation: str,
        weather: Optional[WeatherMetrics] = None,
        language: str = "en",
    ) -> AdvisoryReport:
        primary_pest = pests[0].name if pests else None
        disease_name = disease.disease or disease.display_label or ""
        try:
            chroma_service.query_knowledge(crop, disease_name, primary_pest)
        except Exception as e:
            logger.warning(f"Chroma query failed: {e}")

        matched_rec = self._match_record(crop, disease_name, disease.pathogen_type) if disease_name else None
        is_healthy = disease.pathogen_type.lower() == "healthy" or (
            bool(disease_name) and "healthy" in disease_name.lower()
        )

        if is_healthy and not pests:
            return self._healthy_advisory(crop, disease, risk_level, risk_score, risk_explanation, weather)

        if not matched_rec:
            return self._unavailable_advisory(
                crop, disease, pests, risk_level, risk_score, risk_explanation, weather
            )

        if self.groq_client and not settings.USE_MOCK_AI:
            try:
                llm_advisory = self._call_groq_llm(
                    crop=crop,
                    disease=disease,
                    pests=pests,
                    risk_level=risk_level,
                    risk_score=risk_score,
                    risk_explanation=risk_explanation,
                    weather=weather,
                    matched_rec=matched_rec,
                    language=language,
                )
                if llm_advisory:
                    return llm_advisory
            except Exception as e:
                logger.warning(f"Groq generation failed, using grounded record: {e}")

        return self._build_grounded_icar_advisory(
            crop=crop,
            disease=disease,
            pests=pests,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            weather=weather,
            matched_rec=matched_rec,
        )

    def _healthy_advisory(
        self,
        crop: str,
        disease: DiseasePrediction,
        risk_level: str,
        risk_score: int,
        risk_explanation: str,
        weather: Optional[WeatherMetrics],
    ) -> AdvisoryReport:
        weather_advisory = (
            f"Current conditions: {weather.temperature:.1f}°C, RH {weather.relative_humidity:.0f}%."
            if weather and not weather.is_unavailable
            else "Weather context unavailable."
        )
        return AdvisoryReport(
            condition_summary=f"{crop} foliage appears healthy based on image-level assessment. Continue routine monitoring.",
            overall_risk=risk_level,
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            immediate_action="No chemical spray indicated from this image. Maintain sanitation and scout weekly.",
            pesticide_recommendation=PesticideRecommendation(
                active_ingredient="None",
                chemical_name="None required",
                exact_dose_per_liter="N/A",
                withholding_period_days=0,
                application_method="Not applicable",
                safety_warnings=["Do not apply pesticides prophylactically without confirmed pest/disease pressure."],
                guidance_available=True,
            ),
            fertilizer_adjustments=FertilizerAdjustment(
                n_ratio="Maintain schedule",
                p_ratio="Maintain schedule",
                k_ratio="Maintain schedule",
                micronutrients=[],
                instructions="Follow your local POP fertilizer calendar for the crop stage.",
            ),
            ipm=IPMStrategy(
                cultural=["Remove weeds around field borders.", "Avoid excess nitrogen that softens tissue."],
                biological=["Conserve natural enemies; avoid broad-spectrum sprays."],
                mechanical=["Scout traps if insect pressure is historically high."],
                chemical=["None required based on this image assessment."],
            ),
            monitoring=MonitoringPlan(
                day_1="Walk 5 spots per acre; note any new spots or insects.",
                day_3="Re-check lower canopy for early lesions.",
                day_7="Compare vigor with last week; photograph any new symptoms.",
                day_14="If symptoms appear, re-run analysis and request expert validation.",
            ),
            weather_impact_advisory=weather_advisory,
            sources=[],
            disclaimer=(
                "Image-level healthy result does not guarantee field-wide absence of disease or pests. "
                "Verify against field conditions and local agricultural guidance."
            ),
        )

    def _unavailable_advisory(
        self,
        crop: str,
        disease: DiseasePrediction,
        pests: List[PestDetectionItem],
        risk_level: str,
        risk_score: int,
        risk_explanation: str,
        weather: Optional[WeatherMetrics],
    ) -> AdvisoryReport:
        pest_note = f" Possible pests flagged (may be mock): {', '.join(p.name for p in pests)}." if pests else ""
        disease_label = disease.disease or disease.display_label or "unavailable"
        return AdvisoryReport(
            condition_summary=(
                f"Detected signal for {crop} / {disease_label}, but verified guidance is unavailable "
                f"for this exact crop–disease pair in the curated knowledge base.{pest_note}"
            ),
            overall_risk=risk_level,
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            immediate_action=(
                "Do not apply unverified chemicals. Isolate affected plants if practical, "
                "photograph progression, and request expert / KVK validation."
            ),
            pesticide_recommendation=UNAVAILABLE_PESTICIDE,
            fertilizer_adjustments=FertilizerAdjustment(
                n_ratio="Unverified",
                p_ratio="Unverified",
                k_ratio="Unverified",
                micronutrients=[],
                instructions="Fertilizer adjustment withheld pending verified guidance.",
            ),
            ipm=IPMStrategy(
                cultural=["Improve field sanitation; remove severely affected leaves where appropriate."],
                biological=["Await expert confirmation before introducing biocontrol agents."],
                mechanical=["Scout and mark symptomatic patches."],
                chemical=["Verified chemical guidance unavailable — expert validation recommended."],
            ),
            monitoring=MonitoringPlan(
                day_1="Submit for expert validation via the app.",
                day_3="Monitor spread to adjacent plants.",
                day_7="Follow expert instructions once received.",
                day_14="Reassess after any recommended intervention.",
            ),
            weather_impact_advisory=(
                weather.risk_factor if weather and not getattr(weather, "is_unavailable", False) else "Weather unavailable."
            ),
            sources=[],
            disclaimer=(
                "Verified agricultural guidance unavailable for this case. "
                "No pesticide dosage has been fabricated. Seek expert validation."
            ),
        )

    def _call_groq_llm(
        self,
        crop: str,
        disease: DiseasePrediction,
        pests: List[PestDetectionItem],
        risk_level: str,
        risk_score: int,
        risk_explanation: str,
        weather: Optional[WeatherMetrics],
        matched_rec: dict,
        language: str,
    ) -> Optional[AdvisoryReport]:
        system_prompt = (
            "You are CropShield AI, an agricultural advisor. "
            "ONLY use the provided grounded ICAR reference fields for pesticide names and dosages. "
            "NEVER invent or alter exact_dose_per_liter. "
            "If unsure, say expert validation is required. Output valid JSON only."
        )
        weather_info = (
            f"Temp: {weather.temperature}°C, RH: {weather.relative_humidity}%, Rain: {weather.precipitation}mm"
            if weather and not getattr(weather, "is_unavailable", False)
            else "Weather unavailable"
        )
        user_prompt = f"""
        Grounded diagnosis:
        - Crop: {crop}
        - Disease: {disease.disease or disease.display_label} ({disease.pathogen_type}, Confidence: {(disease.confidence or 0)*100:.0f}%)
        - Pests: {', '.join([p.name for p in pests]) if pests else 'None'}
        - Risk: {risk_level} ({risk_score}/100) — {risk_explanation}
        - Weather: {weather_info}
        - Grounded document: {matched_rec['document_title']} ({matched_rec['authority']})
        - MUST use pesticide: {matched_rec['pesticide']['active_ingredient']} @ {matched_rec['pesticide']['exact_dose_per_liter']}
        - Language: {language}

        Return JSON with keys: condition_summary, immediate_action, pesticide_recommendation,
        fertilizer_adjustments, ipm, monitoring, weather_impact_advisory.
        pesticide_recommendation must use the exact dose string from the grounded document.
        """
        candidate_models = list(dict.fromkeys([
            settings.GROQ_MODEL,
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
        ]))

        data = None
        for model_name in candidate_models:
            try:
                response = self.groq_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                    max_tokens=1400,
                )
                content = response.choices[0].message.content
                data = json.loads(content)
                break
            except Exception as model_err:
                logger.warning("Groq model %s unavailable: %s", model_name, model_err)
                continue

        if not data:
            return self._build_grounded_icar_advisory(
                crop=crop,
                disease=disease,
                pests=pests,
                risk_level=risk_level,
                risk_score=risk_score,
                risk_explanation=risk_explanation,
                weather=weather,
                matched_rec=matched_rec,
            )

        # Force grounded pesticide fields — never trust LLM for dosage invention
        pest_rec = dict(matched_rec["pesticide"])
        pest_rec["guidance_available"] = True

        return AdvisoryReport(
            condition_summary=data.get("condition_summary", matched_rec.get("condition_summary", "")),
            overall_risk=risk_level,
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            immediate_action=data.get("immediate_action", "Follow grounded spray guidance if disease is confirmed in field."),
            pesticide_recommendation=PesticideRecommendation(**pest_rec),
            fertilizer_adjustments=FertilizerAdjustment(**matched_rec["fertilizer"]),
            ipm=IPMStrategy(**matched_rec["ipm"]),
            monitoring=MonitoringPlan(**matched_rec["monitoring"]),
            weather_impact_advisory=data.get("weather_impact_advisory", weather_info),
            sources=[
                SourceReference(
                    title=matched_rec["document_title"],
                    authority=matched_rec["authority"],
                    document_type="Curated ICAR-style Package of Practices",
                    page_number=matched_rec.get("page_number"),
                )
            ],
        )

    def _build_grounded_icar_advisory(
        self,
        crop: str,
        disease: DiseasePrediction,
        pests: List[PestDetectionItem],
        risk_level: str,
        risk_score: int,
        risk_explanation: str,
        weather: Optional[WeatherMetrics],
        matched_rec: dict,
    ) -> AdvisoryReport:
        weather_advisory = (
            f"Relative humidity at {weather.relative_humidity:.0f}% with temperature {weather.temperature:.1f}°C. "
            f"Consider disease-favourable microclimate when scouting."
            if weather and not getattr(weather, "is_unavailable", False)
            else "Weather context unavailable."
        )
        pest_data = dict(matched_rec["pesticide"])
        pest_data["guidance_available"] = True
        return AdvisoryReport(
            condition_summary=matched_rec.get(
                "condition_summary",
                f"{crop}: {disease.disease or disease.display_label}",
            ),
            overall_risk=risk_level,
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            immediate_action=(
                f"If field symptoms match, apply {pest_data['chemical_name']} "
                f"({pest_data['active_ingredient']}) @ {pest_data['exact_dose_per_liter']} "
                f"per grounded guidance — verify label and local regulations."
            ),
            pesticide_recommendation=PesticideRecommendation(**pest_data),
            fertilizer_adjustments=FertilizerAdjustment(**matched_rec["fertilizer"]),
            ipm=IPMStrategy(**matched_rec["ipm"]),
            monitoring=MonitoringPlan(**matched_rec["monitoring"]),
            weather_impact_advisory=weather_advisory,
            sources=[
                SourceReference(
                    title=matched_rec["document_title"],
                    authority=matched_rec["authority"],
                    document_type="Curated ICAR-style Package of Practices",
                    page_number=matched_rec.get("page_number"),
                )
            ],
        )


advisory_engine = AdvisoryEngine()
