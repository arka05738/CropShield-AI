from fastapi import APIRouter
from app.api.v1 import auth, analysis, gis, validation, admin, knowledge, assistant, weather, health, pests

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(analysis.router)
api_router.include_router(pests.router)
api_router.include_router(gis.router)
api_router.include_router(validation.router)
api_router.include_router(admin.router)
api_router.include_router(knowledge.router)
api_router.include_router(assistant.router)
api_router.include_router(weather.router)
