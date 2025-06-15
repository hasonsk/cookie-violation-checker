from fastapi import APIRouter, Depends, Query
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from src.schemas.website import WebsiteResponseSchema, WebsiteListResponseSchema, WebsiteCreateSchema, WebsiteUpdateSchema
from src.schemas.user import User
from src.services.website_management_service.website_management_service import WebsiteManagementService
from src.dependencies.dependencies import get_website_management_service, get_current_user
from src.models.user import UserRole
from src.exceptions.custom_exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/api", tags=["Websites"])

@router.get("/websites", response_model=List[WebsiteListResponseSchema])
async def get_all_websites(
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search keyword for domain name"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    """
    Xem danh sách tất cả các website được kiểm tra.
    Tác nhân: Nhà quản lý dịch vụ hoặc Nhà cung cấp.
    Tiền điều kiện: Người dùng đã đăng nhập thành công vào hệ thống.
    """
    return await website_management_service.get_all_websites(
        user_id=str(current_user.id),
        user_role=current_user.role,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/websites/{website_id}/analytics", response_model=dict) # Adjust response model as needed
async def get_website_analytics(
    website_id: str,
    current_user: User = Depends(get_current_user),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    """
    Lấy dữ liệu phân tích cho một website.
    """
    try:
        # This method needs to be implemented in WebsiteManagementService
        analytics_data = await website_management_service.get_website_analytics(website_id)
        return analytics_data
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.post("/websites", response_model=WebsiteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_website(
    website: WebsiteCreateSchema,
    current_user: User = Depends(get_current_user),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    """
    Tạo một website mới.
    """
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only providers can create websites."
        )
    try:
        return await website_management_service.create_website(website, str(current_user.id))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/websites/{website_id}", response_model=WebsiteResponseSchema)
async def update_website(
    website_id: str,
    website: WebsiteUpdateSchema,
    current_user: User = Depends(get_current_user),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    """
    Cập nhật thông tin của một website hiện có.
    """
    try:
        return await website_management_service.update_website(website_id, website)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/websites/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(
    website_id: str,
    current_user: User = Depends(get_current_user),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    """
    Xóa một website.
    """
    try:
        await website_management_service.delete_website(website_id)
        return {"message": "Website deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/analyze", response_model=dict, status_code=status.HTTP_202_ACCEPTED) # Adjust response model as needed
async def analyze_website(
    payload: dict, # Define a proper schema for payload if needed
    current_user: User = Depends(get_current_user),
    website_management_service: WebsiteManagementService = Depends(get_website_management_service)
):
    """
    Kích hoạt phân tích một website.
    """
    try:
        # This method needs to be implemented in WebsiteManagementService
        analysis_result = await website_management_service.trigger_website_analysis(payload)
        return {"message": "Website analysis initiated successfully", "result": analysis_result}
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
