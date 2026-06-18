from fastapi import APIRouter

from app.api.v1 import auth, cameras, alerts

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(cameras.router)
router.include_router(alerts.router)
