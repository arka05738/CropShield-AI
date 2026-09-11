"""
Pest-focused advisory grounding.

Matches curated ICAR-style records by pest label (and optional crop).
Never fabricates pesticide names or dosages when no verified match exists.
"""
from __future__ import annotations

import logging
import re
from typing import List, Optional

from app.models.schemas import (
    PestAdvisoryBrief,
    PesticideRecommendation,
    SourceReference,
)
from app.rag.advisory_engine import UNAVAILABLE_PESTICIDE
from app.rag.chroma_service import chroma_service
from app.rag.icar_knowledge import ICAR_POP_RECORDS

logger = logging.getLogger("cropshield.rag.pest_advisory")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _pest_tokens(label: str) -> set:
    stop = {"the", "a", "an", "of", "and", "or"}
    return {t for t in _norm(label).split() if t and t not in stop}


def match_pest_record(pest_label: str, crop_hint: Optional[str] = None) -> Optional[dict]:
    """
    Prefer same-crop + pest name overlap; else pest-only overlap across crops.
    Requires meaningful token overlap — no chemical inventing.
    """
    pest_toks = _pest_tokens(pest_label)
    if not pest_toks:
        return None
    crop_l = _norm(crop_hint or "")

    best = None
    best_score = 0.0
    for rec in ICAR_POP_RECORDS:
        rec_pest = _pest_tokens(str(rec.get("pest") or ""))
        if not rec_pest:
            continue
        overlap = len(pest_toks & rec_pest) / max(1, len(pest_toks))
        if overlap < 0.5:
            continue
        score = overlap
        if crop_l and _norm(str(rec.get("crop") or "")) == crop_l:
            score += 0.35
        if score > best_score:
            best_score = score
            best = rec
    return best


def generate_pest_advisory(
    *,
    pest_labels: List[str],
    crop_hint: Optional[str],
    count: int,
    severity: str,
) -> PestAdvisoryBrief:
    primary = pest_labels[0] if pest_labels else None
    if not primary:
        return PestAdvisoryBrief(
            condition_summary=(
                "No pest objects were detected above the configured confidence threshold. "
                "Absence of detections is not proof that the crop is without pests."
            ),
            guidance_available=False,
            immediate_action=(
                "Continue routine scouting. Re-photograph closer to suspected insects if present."
            ),
            pesticide_recommendation=UNAVAILABLE_PESTICIDE.model_copy(
                update={
                    "unavailable_reason": "No pest detections to ground advisory on.",
                }
            ),
        )

    try:
        chroma_service.query_knowledge(crop_hint or "", disease="", pest=primary)
    except Exception as e:
        logger.warning("Chroma pest query failed: %s", e)

    matched = match_pest_record(primary, crop_hint)
    if not matched:
        return PestAdvisoryBrief(
            condition_summary=(
                f"Detected pest signal '{primary}' (n={count}, preliminary severity={severity}), "
                "but verified guidance is unavailable for this exact label in the curated knowledge base."
            ),
            guidance_available=False,
            immediate_action=(
                "Seek local agriculture officer / KVK confirmation before applying any chemical. "
                "Do not invent dosages from the detection alone."
            ),
            pesticide_recommendation=UNAVAILABLE_PESTICIDE.model_copy(
                update={
                    "unavailable_reason": (
                        f"No curated pest match for label '{primary}'"
                        + (f" / crop '{crop_hint}'" if crop_hint else "")
                    ),
                }
            ),
        )

    pest_rec = matched.get("pesticide") or {}
    sources = []
    for src in matched.get("sources") or []:
        if isinstance(src, dict):
            sources.append(
                SourceReference(
                    title=src.get("title") or "Curated agricultural reference",
                    authority=src.get("authority") or "ICAR/POP curated",
                    document_type=src.get("document_type") or "POP",
                    page_number=src.get("page_number"),
                    url=src.get("url"),
                )
            )
    if not sources:
        sources = [
            SourceReference(
                title=matched.get("id", "icar_record"),
                authority="Curated ICAR-style POP record",
                document_type="POP",
            )
        ]

    ipm = matched.get("ipm") if isinstance(matched.get("ipm"), dict) else {}
    chemical_steps = list(ipm.get("chemical") or [])
    immediate = (
        matched.get("immediate_action")
        or (chemical_steps[0] if chemical_steps else None)
        or "Follow curated IPM steps for the matched record; confirm in field."
    )

    return PestAdvisoryBrief(
        condition_summary=(
            f"{matched.get('condition_summary') or matched.get('pest')} "
            f"(model label '{primary}', count={count}, preliminary severity={severity})."
        ),
        guidance_available=True,
        immediate_action=str(immediate),
        pesticide_recommendation=PesticideRecommendation(
            active_ingredient=str(pest_rec.get("active_ingredient") or "Not specified"),
            chemical_name=str(pest_rec.get("chemical_name") or "Verified chemical guidance"),
            exact_dose_per_liter=str(pest_rec.get("exact_dose_per_liter") or ""),
            withholding_period_days=int(pest_rec.get("withholding_period_days") or 0),
            application_method=str(
                pest_rec.get("application_method")
                or "Consult local agriculture officer / KVK before applying any chemical."
            ),
            safety_warnings=list(pest_rec.get("safety_warnings") or [
                "Follow product label and local regulations.",
            ]),
            guidance_available=True,
            unavailable_reason=None,
        ),
        sources=sources,
    )
