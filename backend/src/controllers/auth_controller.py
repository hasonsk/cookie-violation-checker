from fastapi import APIRouter, Depends, Header
from schemas.auth_schema import RegisterSchema, LoginSchema, TokenResponse
from services.auth_service import auth_service

router = APIRouter()

@router.post("/register")
async def register(data: RegisterSchema):
    return await auth_service.register_user(data)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginSchema):
    return await auth_service.login_user(data)

@router.get("/verify")
async def verify(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    return await auth_service.verify_user(token)

@router.post("/logout")
async def logout():
    return {"msg": "Đăng xuất thành công (xử lý phía client)"}
