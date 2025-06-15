from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from src.schemas.domain_request import DomainRequestCreateSchema, DomainRequestResponseSchema, DomainRequestStatus
from src.schemas.user import User
from src.services.domain_request_service import DomainRequestService
from src.dependencies.dependencies import get_domain_request_service, get_current_user, get_current_admin_or_manager
from src.exceptions.custom_exceptions import UnauthorizedError, DomainRequestNotFoundError, DomainRequestNotAuthorizedError

router = APIRouter(prefix="/api", tags=["Domain Requests"])

@router.post("/domain-requests", response_model=DomainRequestResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_domain_request(
    request_data: DomainRequestCreateSchema,
    current_user: User = Depends(get_current_user),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    """
    Gửi yêu cầu đăng ký domain.
    Tác nhân: Nhà cung cấp dịch vụ.
    Tiền điều kiện: Người dùng đã đăng nhập thành công vào hệ thống với vai trò nhà cung cấp dịch vụ.
    """
    if current_user.role not in ["provider", "admin"]: # Assuming 'provider' is the role for Nhà cung cấp dịch vụ
        raise DomainRequestNotAuthorizedError("Only service providers or admins can submit domain registration requests.")

    return await domain_request_service.create_domain_request(request_data, current_user.id)

@router.get("/domain-requests", response_model=List[DomainRequestResponseSchema])
async def get_all_domain_requests(
    current_user: User = Depends(get_current_admin_or_manager),
    status: Optional[DomainRequestStatus] = None,
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    """
    Xem danh sách tất cả các yêu cầu đăng ký domain.
    Tác nhân: Nhà quản lý dịch vụ hoặc Admin.
    """
    return await domain_request_service.get_all_domain_requests(status=status)

@router.patch("/domain-requests/{request_id}/approve", response_model=DomainRequestResponseSchema)
async def approve_domain_request(
    request_id: str,
    current_user: User = Depends(get_current_admin_or_manager),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    """
    Phê duyệt yêu cầu đăng ký domain.
    Tác nhân: Nhà quản lý dịch vụ hoặc Admin.
    """
    return await domain_request_service.approve_domain_request(request_id, current_user.id)

@router.patch("/domain-requests/{request_id}/reject", response_model=DomainRequestResponseSchema)
async def reject_domain_request(
    request_id: str,
    current_user: User = Depends(get_current_admin_or_manager),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    """
    Từ chối yêu cầu đăng ký domain.
    Tác nhân: Nhà quản lý dịch vụ hoặc Admin.
    """
    return await domain_request_service.reject_domain_request(request_id, current_user.id)
