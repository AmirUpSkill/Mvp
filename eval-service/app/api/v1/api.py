# eval-service/app/api/v1/api.py

from fastapi import APIRouter
from app.api.v1.endpoints import evaluation # Import remains the same

api_v1_router = APIRouter()

api_v1_router.include_router(
    evaluation.router,
    prefix="/evaluate",  # <<< CHANGED from "/evaluation" to "/evaluate"
    tags=["Evaluation"],  # <<< CHANGED tag to match prefix logically
)

# Add other v1 routers here if needed in the future