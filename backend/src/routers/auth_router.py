from fastapi import APIRouter
from controllers import auth_controller

router = APIRouter(prefix="/api/auth", tags=["Auth"])

router.include_router(auth_controller.router)
