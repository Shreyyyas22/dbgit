from fastapi import APIRouter

from .health import router as health_router
from .databases import router as databases_router
from .commits import router as commits_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(databases_router, prefix="/databases", tags=["databases"])
api_router.include_router(commits_router, prefix="/databases/{db_id}/commits", tags=["commits"])
