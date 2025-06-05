from fastapi import APIRouter, Header, Depends, Path
from schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    LoginResponseSchema,
    UserInfo,
    RequestRoleChangeSchema,
    ApproveAccountSchema,
    UserRole
)
from services.auth_service.auth_service import AuthService
from dependencies import get_auth_service, get_current_user, get_current_admin_or_manager

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

@router.get("/auth/verify", response_model=UserInfo)
async def verify(
    current_user: UserInfo = Depends(get_current_user)
):
    return current_user

@router.post("/users/request-role", response_model=UserInfo)
async def request_role_change(
    requested_role_data: RequestRoleChangeSchema,
    current_user: UserInfo = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.request_role_change(str(current_user.email), requested_role_data) # Assuming user ID is stored in email for now, will need to adjust if using ObjectId

@router.patch("/users/{user_id}/approve", response_model=UserInfo)
async def approve_account(
    user_id: str = Path(...),
    current_user: UserInfo = Depends(get_current_admin_or_manager),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.approve_account(user_id, current_user)

@router.patch("/users/{user_id}/approve-role", response_model=UserInfo)
async def approve_role_change(
    user_id: str = Path(...),
    current_user: UserInfo = Depends(get_current_admin_or_manager),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.approve_role_change(user_id, current_user)
