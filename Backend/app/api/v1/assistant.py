import logging
from fastapi import APIRouter, Depends
from app.models.schemas import AssistantChatRequest, AssistantChatResponse, SourceReference
from app.core.config import settings
from app.core.security import get_current_user
from app.core.database import memory_store
from app.rag.chroma_service import chroma_service
from groq import Groq

logger = logging.getLogger("cropshield.assistant")
router = APIRouter(prefix="/assistant", tags=["Agricultural AI Assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(
    req: AssistantChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Conversational assistant grounded in retrieved knowledge when available.
    Does not default crop context to an arbitrary crop (e.g. Sugarcane/Tomato).
    """
    crop = (req.crop_context or "").strip() or None

    # Prefer analysis context when analysis_id provided
    if req.analysis_id:
        analysis = next((a for a in memory_store["analyses"] if a["id"] == req.analysis_id), None)
        if analysis and analysis.get("crop"):
            crop = analysis["crop"]

    if not crop:
        return AssistantChatResponse(
            reply=(
                "Please tell me which crop you are asking about "
                "(for example Tomato, Rice, Wheat, Cotton, Potato, or Maize), "
                "or open this assistant from a completed analysis so I can use that crop context."
            ),
            sources=[],
            language=req.language or "en",
        )

    retrieved = []
    try:
        retrieved = chroma_service.query_knowledge(crop, req.message[:80] or "General Health", n_results=2)
    except Exception as e:
        logger.warning(f"Assistant retrieval failed: {e}")

    if settings.GROQ_API_KEY and not settings.USE_MOCK_AI:
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            context_text = "\n".join([doc.get("content", "") for doc in retrieved]) or "No retrieved passages."
            system_prompt = (
                "You are CropShield AI Agronomic Copilot for Indian farmers. "
                "Use only the retrieved context for chemical dosages. "
                "If context is insufficient, say verified guidance is unavailable and recommend expert/KVK validation. "
                "Never invent pesticide dosages. Respond in the requested language when possible."
            )
            user_msg = f"""
            Active Crop: {crop}
            Retrieved Context:
            {context_text}

            Farmer Question:
            {req.message}

            Language: {req.language or 'en'}
            """
            candidate_models = list(dict.fromkeys([
                settings.GROQ_MODEL,
                "qwen/qwen3.8-27b",
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
            ]))
            resp = None
            for model_name in candidate_models:
                try:
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg},
                        ],
                        max_tokens=600,
                        temperature=0.2,
                    )
                    break
                except Exception as model_err:
                    logger.warning("Assistant model %s failed: %s", model_name, model_err)
                    continue

            if resp is not None:
                reply_text = resp.choices[0].message.content
                return AssistantChatResponse(
                    reply=reply_text,
                    sources=[
                        SourceReference(
                            title=doc.get("metadata", {}).get("document_title", "Curated POP record"),
                            authority=doc.get("metadata", {}).get("authority", "Curated knowledge"),
                            document_type="Package of Practices",
                        )
                        for doc in retrieved
                    ],
                    language=req.language or "en",
                )
        except Exception as e:
            logger.warning(f"Groq assistant call error: {e}")

    # Deterministic fallback — no fabricated chemical doses
    if not retrieved:
        reply = (
            f"I could not retrieve sufficiently relevant verified guidance for {crop} on this question. "
            "Please rephrase, provide more crop/disease detail, or request expert validation. "
            "I will not invent pesticide dosages."
        )
        return AssistantChatResponse(reply=reply, sources=[], language=req.language or "en")

    msg_lower = req.message.lower()
    if "irrigate" in msg_lower or "water" in msg_lower:
        reply = (
            f"For {crop}, prefer early-morning irrigation and avoid prolonged leaf wetness when humidity is high. "
            "Exact scheduling depends on growth stage and local advisory — confirm with your KVK if unsure."
        )
    elif "dose" in msg_lower or "pesticide" in msg_lower or "spray" in msg_lower:
        reply = (
            f"For chemical spray questions on {crop}: use only dosages from a matched curated POP record "
            "or product label. If your analysis report shows 'Verified chemical guidance unavailable', "
            "do not spray based on AI guesswork — request expert validation."
        )
    else:
        snippet = retrieved[0].get("content", "")[:400]
        reply = (
            f"Based on retrieved knowledge for {crop}:\n{snippet}\n\n"
            "This is decision-support information. Confirm against current local guidance before acting."
        )

    return AssistantChatResponse(
        reply=reply,
        sources=[
            SourceReference(
                title=doc.get("metadata", {}).get("document_title", "Curated POP record"),
                authority=doc.get("metadata", {}).get("authority", "Curated knowledge"),
                document_type="Package of Practices",
            )
            for doc in retrieved
        ],
        language=req.language or "en",
    )
