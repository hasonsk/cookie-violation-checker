from fastapi import APIRouter, Header, Depends, Path
from schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    LoginResponseSchema,
    UserInfo,
    RequestRoleChangeSchema, # Keep for now if other parts of the code still use it
    ApproveAccountSchema,
    UserRole,
    RequestRoleChangePayloadSchema,
    RoleChangeRequestInDB,
    UserWithRoleRequests
)
from typing import List
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

@router.post("/users/request-role", response_model=RoleChangeRequestInDB)
async def request_role_change(
    requested_role_data: RequestRoleChangePayloadSchema,
    current_user: UserInfo = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    print("ID: ", current_user.id)
    return await auth_service.request_role_change(
        user_id=str(current_user.id),
        current_user_email=current_user.email,
        current_user_role=current_user.role,
        requested_role_data=requested_role_data
    )

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

@router.get("/admin/users", response_model=List[UserWithRoleRequests])
async def get_all_users(
    current_user: UserInfo = Depends(get_current_admin_or_manager),
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.get_all_users()
