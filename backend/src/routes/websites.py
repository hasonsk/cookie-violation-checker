from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from src.schemas.website import WebsiteResponseSchema, WebsiteListResponseSchema, WebsiteCreateSchema, WebsiteUpdateSchema, PaginatedWebsiteResponseSchema
from src.schemas.user import User
from src.schemas.violation import ComplianceAnalysisResponse
from src.services.website_management_service.website_management_service import WebsiteManagementService
from src.dependencies.dependencies import get_website_management_service, get_current_user, get_current_admin_or_manager
from src.models.user import UserRole
from src.exceptions.custom_exceptions import NotFoundException, BadRequestException, UnauthorizedError, InternalServerError

router = APIRouter(prefix="/api", tags=["Websites"])

@router.get("/websites", response_model=PaginatedWebsiteResponseSchema)
async def get_all_websites(
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search keyword for domain name"),
    is_approved: Optional[bool] = Query(None, description="Filter by approval status (for admins/managers)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    return await website_management_service.get_all_websites(
        user_id=str(current_user.id),
        user_role=current_user.role,
        is_approved=is_approved,
        search_query=search,
        skip=skip,
        limit=limit
    )

@router.get("/websites/{website_id}", response_model=WebsiteResponseSchema)
async def get_website_by_id(
    website_id: str,
    current_user: User = Depends(get_current_user),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    """
    Lấy thông tin chi tiết của một website bằng ID.
    """
    try:
        return await website_management_service.get_website_by_id(website_id)
    except NotFoundException as e:
        raise NotFoundException(str(e))

@router.get("/websites/{website_id}/analytics", response_model=List[ComplianceAnalysisResponse])
async def get_website_analytics(
    website_id: str,
    current_user: User = Depends(get_current_user),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    try:
        analytics_data = await website_management_service.get_website_analytics(website_id)
        return analytics_data
    except NotFoundException as e:
        raise NotFoundException(str(e))
    except Exception as e:
        raise InternalServerError(f"An error occurred: {str(e)}")
