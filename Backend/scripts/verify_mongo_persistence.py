"""
MongoDB durable persistence verification.

Connects using configured settings (does not print secrets).
If Mongo is unreachable → exit 2 (BLOCKED).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure Backend on path
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

OUT = Path(__file__).resolve().parents[2] / "docs" / "_mongo_persistence_result.json"


async def main() -> int:
    # Prefer real Mongo; do not enable mock AI
    os.environ.setdefault("USE_MOCK_AI", "false")
    os.environ.setdefault("SEED_DEMO_DATA", "false")

    from app.core.config import settings
    from app.core.database import connect_to_mongo, close_mongo_connection, db, persist_analysis, persistence_mode

    result = {
        "mongo_uri_configured": bool((settings.MONGO_URI or "").strip()),
        "mongo_db_name_set": bool((settings.MONGO_DB_NAME or "").strip()),
        "host_hint": "localhost" if "localhost" in (settings.MONGO_URI or "") else "remote-or-custom",
        "connected": False,
        "persistence_mode": None,
        "write_ok": False,
        "read_ok": False,
        "cleanup_ok": False,
        "status": "BLOCKED",
        "error": None,
    }

    try:
        await connect_to_mongo()
    except Exception as e:
        result["error"] = f"connect_exception:{type(e).__name__}"
        OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 2

    result["connected"] = bool(db.is_connected)
    result["persistence_mode"] = persistence_mode()

    if not db.is_connected:
        result["status"] = "BLOCKED"
        result["error"] = "MongoDB connection failed; backend would use memory fallback"
        OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        await close_mongo_connection()
        return 2

    test_id = f"an_mongo_verify_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    record = {
        "id": test_id,
        "user_id": "usr_mongo_verify_farmer",
        "status": "completed",
        "crop": "Tomato",
        "crop_confidence": 0.99,
        "disease": {
            "disease": "Early Blight",
            "confidence": 0.9,
            "inference_mode": "huggingface_trained",
            "raw_label": "Tomato___Early_blight",
            "display_label": "Early Blight",
            "model_provider": "huggingface",
            "model_name": "kimcomehome/plantvillage-vit-leaf-disease",
            "model_architecture": "ViTForImageClassification",
        },
        "model": {
            "provider": "huggingface",
            "model_id": "kimcomehome/plantvillage-vit-leaf-disease",
            "architecture": "ViTForImageClassification",
            "status": "huggingface_trained",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verification_marker": "mongo_persistence_e2e",
    }

    try:
        await persist_analysis(record)
        result["write_ok"] = True
        found = await db.db.analyses.find_one({"id": test_id})
        result["read_ok"] = bool(found) and found.get("verification_marker") == "mongo_persistence_e2e"
        result["analysis_id"] = test_id
        # cleanup test data
        del_res = await db.db.analyses.delete_one({"id": test_id})
        result["cleanup_ok"] = del_res.deleted_count == 1
        result["status"] = "PASS" if result["write_ok"] and result["read_ok"] else "FAIL"
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = f"{type(e).__name__}"
    finally:
        await close_mongo_connection()

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else (2 if result["status"] == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
