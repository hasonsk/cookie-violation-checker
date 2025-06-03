# controllers/auth_controller.py
from fastapi import APIRouter, Header
from schemas.auth_schema import RegisterSchema, LoginSchema, LoginResponseSchema
from repositories.user_repository import UserRepository
from services.auth_service.auth_service import AuthService
from configs.database import get_db

router = APIRouter()
user_repo = UserRepository(get_db()["users"])
auth_service = AuthService(user_repo)

@router.post("/register")
async def register(data: RegisterSchema):
    return await auth_service.register_user(data)

@router.post("/login", response_model=LoginResponseSchema)
async def login(data: LoginSchema):
    return await auth_service.login_user(data)

@router.get("/verify")
async def verify(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    return await auth_service.get_current_user(token)
