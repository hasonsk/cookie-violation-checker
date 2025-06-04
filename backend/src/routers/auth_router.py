from fastapi import APIRouter, Header, Depends
from schemas.auth_schema import RegisterSchema, LoginSchema, LoginResponseSchema
from services.auth_service.auth_service import AuthService
from dependencies import get_auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register")
async def register(
    data: RegisterSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(data)

@router.post("/login", response_model=LoginResponseSchema)
async def login(
    data: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login_user(data)

@router.get("/verify")
async def verify(
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service)
):
    token = authorization.replace("Bearer ", "")
    return await auth_service.get_current_user(token)
