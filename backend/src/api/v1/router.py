from fastapi import APIRouter

from src.apps.auth.routes import router as auth_router
from src.apps.ingestion.routes import router as ingestion_router
from src.apps.notifications.routes import router as notifications_router
from src.apps.qa.routes import router as qa_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(ingestion_router, tags=["ingestion"])
router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
router.include_router(qa_router, prefix="/qa", tags=["qa"])
