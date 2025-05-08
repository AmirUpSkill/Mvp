from fastapi import APIRouter

from app.api.v1.endpoints import documents
from app.api.v1.endpoints import tickets

api_v1_router = APIRouter()

api_v1_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

api_v1_router.include_router(
    tickets.router,
    prefix="/tickets",
    tags=["Tickets"]
)
