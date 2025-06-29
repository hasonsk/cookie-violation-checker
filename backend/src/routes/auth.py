from fastapi import APIRouter, Header, Depends, Path
from src.schemas.auth import (
    RegisterSchema,
    RegisterResponseSchema,
    LoginSchema,
    LoginResponseSchema,
    ForgotPasswordRequestSchema,
    ResetPasswordRequestSchema,
    MessageResponseSchema
)
from src.schemas.user import User
from typing import List
from src.models.domain_request import DomainRequest
from src.services.auth_service.auth_service import AuthService
from src.dependencies.dependencies import get_auth_service, get_current_user, get_current_admin_or_manager

router = APIRouter(prefix="/api", tags=["Users"])

@router.post("/auth/register")
async def register(
    data: RegisterSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(data)

@router.post("/auth/login", response_model=LoginResponseSchema)
async def login(
    data: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login_user(data)

@router.get("/auth/verify", response_model=User)
async def verify(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.post("/auth/forgot-password", response_model=MessageResponseSchema)
async def forgot_password(
    data: ForgotPasswordRequestSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.request_password_reset(data.email)

@router.post("/auth/reset-password", response_model=MessageResponseSchema)
async def reset_password(
    data: ResetPasswordRequestSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.reset_password(data.token, data.new_password)

@router.patch("/users/{user_id}/approve", response_model=User)
async def approve_account(
    user_id: str = Path(...),
    current_user: User = Depends(get_current_admin_or_manager),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.approve_account(user_id, current_user)
