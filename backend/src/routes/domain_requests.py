from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from src.schemas.domain_request import DomainRequestCreateSchema, DomainRequestResponseSchema, DomainRequestStatus, DomainRequestUpdateSchema
from src.schemas.user import User
from src.services.domain_request_service import DomainRequestService
from src.dependencies.dependencies import get_domain_request_service, get_current_user, get_current_admin_or_manager, get_website_management_service
from src.exceptions.custom_exceptions import UnauthorizedError, DomainRequestNotFoundError, DomainRequestNotAuthorizedError
from src.services.website_management_service.website_management_service import WebsiteManagementService

class RejectRequestSchema(BaseModel):
    feedback: str = Field(..., min_length=10, max_length=1000)

router = APIRouter(prefix="/api", tags=["Domain Requests"])

@router.post("/domain-requests", response_model=DomainRequestResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_domain_request(
    request_data: DomainRequestCreateSchema,
    current_user: User = Depends(get_current_user),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    if current_user.role not in ["provider", "admin"]:
        raise DomainRequestNotAuthorizedError("Only service providers or admins can submit domain registration requests.")

    return await domain_request_service.create_domain_request(request_data, current_user.id, current_user.name, current_user.email)

@router.put("/domain-requests/{request_id}", response_model=DomainRequestResponseSchema)
async def update_domain_request(
    request_id: str,
    request_data: DomainRequestUpdateSchema,
    current_user: User = Depends(get_current_user),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    if current_user.role not in ["provider", "admin"]:
        raise DomainRequestNotAuthorizedError("Only service providers or admins can update domain registration requests.")
    return await domain_request_service.update_domain_request(request_id, request_data, current_user.id)

@router.get("/domain-requests/me", response_model=Optional[DomainRequestResponseSchema])
async def get_my_latest_domain_request(
    current_user: User = Depends(get_current_user),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    return await domain_request_service.get_latest_domain_request_by_user(current_user.id)

@router.get("/domain-requests", response_model=List[DomainRequestResponseSchema])
async def get_all_domain_requests(
    current_user: User = Depends(get_current_user), # Changed dependency
    status: Optional[DomainRequestStatus] = None,
    requester_id: Optional[str] = Query(None), # New parameter
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    """
    Xem danh sách tất cả các yêu cầu đăng ký domain.
    Tác nhân: Nhà quản lý dịch vụ, Admin, hoặc Nhà cung cấp dịch vụ (chỉ xem yêu cầu của mình).
    """
    if current_user.role == "provider":
        if requester_id and requester_id != current_user.id:
            raise UnauthorizedError("Providers can only view their own domain requests.")
        requester_id = current_user.id # Ensure providers only see their own requests
    elif current_user.role not in ["admin", "manager"]:
        raise UnauthorizedError("Only admins, managers, or providers can view domain requests.")

    return await domain_request_service.get_all_domain_requests(status=status, requester_id=requester_id) # Pass requester_id

@router.patch("/domain-requests/{request_id}/approve", response_model=DomainRequestResponseSchema)
async def approve_domain_request(
    request_id: str,
    current_user: User = Depends(get_current_admin_or_manager),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service) # Inject WebsiteManagementService
):
    return await domain_request_service.approve_domain_request(request_id, current_user.id, website_management_service)

@router.patch("/domain-requests/{request_id}/reject", response_model=DomainRequestResponseSchema)
async def reject_domain_request(
    request_id: str,
    reject_data: RejectRequestSchema,
    current_user: User = Depends(get_current_admin_or_manager),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    return await domain_request_service.reject_domain_request(request_id, current_user.id, reject_data.feedback)

@router.delete("/domain-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain_request(
    request_id: str,
    current_user: User = Depends(get_current_user),
    domain_request_service: DomainRequestService = Depends(get_domain_request_service)
):
    """
    Xoá một yêu cầu đăng ký domain. Chỉ Admin, Manager, Provider hoặc người tạo yêu cầu mới có quyền.
    """
    await domain_request_service.delete_domain_request(request_id, current_user)
    return {"message": "Domain request deleted successfully."}
