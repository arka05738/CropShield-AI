import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger("cropshield.db")


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    is_connected: bool = False


db = Database()

# In-memory storage fallback if MongoDB connection fails
memory_store: Dict[str, List[Dict[str, Any]]] = {
    "users": [],
    "farms": [],
    "analyses": [],
    "pest_analyses": [],
    "validations": [],
    "knowledge": [],
    "hotspots": [],
}


async def connect_to_mongo():
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGO_URI}...")
        db.client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
        await db.client.admin.command("ping")
        db.db = db.client[settings.MONGO_DB_NAME]
        db.is_connected = True
        logger.info(f"Successfully connected to MongoDB: {settings.MONGO_DB_NAME}")
        await setup_indexes()
        await hydrate_memory_from_mongo()
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Using in-memory store (non-durable).")
        db.is_connected = False


async def close_mongo_connection():
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed.")


async def setup_indexes():
    if not db.is_connected:
        return
    try:
        await db.db.analyses.create_index([("user_id", 1)])
        await db.db.analyses.create_index([("created_at", -1)])
        await db.db.analyses.create_index([("crop", 1)])
        await db.db.analyses.create_index([("validation_status", 1)])
        await db.db.analyses.create_index([("location.coordinates", "2dsphere")])
        await db.db.pest_analyses.create_index([("user_id", 1)])
        await db.db.pest_analyses.create_index([("created_at", -1)])
        await db.db.pest_analyses.create_index([("crop", 1)])
        await db.db.pest_analyses.create_index([("primary_pest", 1)])
        await db.db.users.create_index([("email", 1)], unique=True)
        await db.db.validations.create_index([("status", 1)])
        await db.db.hotspots.create_index([("district", 1), ("state", 1)])
        logger.info("Database indexes successfully configured.")
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")


async def hydrate_memory_from_mongo():
    """Mirror Mongo collections into memory_store for unified read path."""
    if not db.is_connected:
        return
    try:
        users = await db.db.users.find({}, {"_id": 0}).to_list(5000)
        analyses = await db.db.analyses.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
        pest_analyses = await db.db.pest_analyses.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
        validations = await db.db.validations.find({}, {"_id": 0}).to_list(2000)
        hotspots = await db.db.hotspots.find({}, {"_id": 0}).to_list(2000)
        if users:
            memory_store["users"] = users
        if analyses:
            memory_store["analyses"] = analyses
        if pest_analyses:
            memory_store["pest_analyses"] = pest_analyses
        if validations:
            memory_store["validations"] = validations
        if hotspots:
            memory_store["hotspots"] = hotspots
        logger.info(
            "Hydrated memory store from Mongo: "
            f"{len(memory_store['users'])} users, {len(memory_store['analyses'])} analyses, "
            f"{len(memory_store['pest_analyses'])} pest_analyses"
        )
    except Exception as e:
        logger.warning(f"Mongo hydrate skipped: {e}")


def get_database():
    return db.db if db.is_connected else None


def persistence_mode() -> str:
    return "mongodb" if db.is_connected else "memory"


async def persist_user(user: Dict[str, Any]) -> None:
    memory_store["users"].append(user)
    if db.is_connected:
        try:
            doc = {**user}
            if isinstance(doc.get("created_at"), datetime):
                pass
            await db.db.users.update_one({"id": user["id"]}, {"$set": doc}, upsert=True)
        except Exception as e:
            logger.error(f"Failed to persist user to Mongo: {e}")


async def persist_analysis(record: Dict[str, Any]) -> None:
    memory_store["analyses"].insert(0, record)
    if db.is_connected:
        try:
            await db.db.analyses.update_one({"id": record["id"]}, {"$set": record}, upsert=True)
        except Exception as e:
            logger.error(f"Failed to persist analysis to Mongo: {e}")


async def persist_pest_analysis(record: Dict[str, Any]) -> None:
    """Persist pest OD records separately from disease analyses."""
    memory_store.setdefault("pest_analyses", []).insert(0, record)
    if db.is_connected:
        try:
            await db.db.pest_analyses.update_one({"id": record["id"]}, {"$set": record}, upsert=True)
        except Exception as e:
            logger.error(f"Failed to persist pest analysis to Mongo: {e}")


async def persist_validation(record: Dict[str, Any], upsert: bool = True) -> None:
    existing = next((v for v in memory_store["validations"] if v["id"] == record["id"]), None)
    if existing:
        existing.update(record)
    else:
        memory_store["validations"].insert(0, record)
    if db.is_connected:
        try:
            await db.db.validations.update_one({"id": record["id"]}, {"$set": record}, upsert=upsert)
        except Exception as e:
            logger.error(f"Failed to persist validation to Mongo: {e}")


async def update_analysis_fields(analysis_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    record = next((a for a in memory_store["analyses"] if a["id"] == analysis_id), None)
    if not record:
        return None
    record.update(fields)
    if db.is_connected:
        try:
            await db.db.analyses.update_one({"id": analysis_id}, {"$set": fields})
        except Exception as e:
            logger.error(f"Failed to update analysis in Mongo: {e}")
    return record
