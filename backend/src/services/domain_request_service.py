from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime
from fastapi import HTTPException # Import HTTPException

from src.schemas.domain_request import DomainRequestCreateSchema, DomainRequestResponseSchema, DomainRequestStatus
from src.models.domain_request import DomainRequest
from src.repositories.domain_request_repository import DomainRequestRepository
from src.repositories.website_repository import WebsiteRepository
from src.exceptions.custom_exceptions import DomainRequestNotFoundError, UnauthorizedError, DomainAlreadyExistsError

class DomainRequestService:
    def __init__(self, domain_request_repo: DomainRequestRepository, website_repo: WebsiteRepository):
        self.domain_request_repo = domain_request_repo
        self.website_repo = website_repo

    async def create_domain_request(self, request_data: DomainRequestCreateSchema, user_id: str) -> DomainRequestResponseSchema:
        # Check for duplicate domains
        for domain in request_data.domains:
            existing_website = await self.website_repo.get_website_by_root_url(domain)
            if existing_website:
                raise DomainAlreadyExistsError(f"Domain '{domain}' is already registered.")

        new_request = DomainRequest(
            user_id=ObjectId(user_id),
            company_name=request_data.company_name,
            domains=request_data.domains,
            purpose=request_data.purpose,
            status=DomainRequestStatus.PENDING,
            created_at=datetime.utcnow()
        )

        # FIX: Loại bỏ _id khỏi dict trước khi insert
        request_dict = new_request.dict(by_alias=True, exclude_none=True)
        # Đảm bảo không có _id trong dict
        request_dict.pop('_id', None)
        request_dict.pop('id', None)  # Cũng loại bỏ 'id' nếu có

        inserted_id = await self.domain_request_repo.create_domain_request(request_dict)
        created_request = await self.domain_request_repo.get_domain_request_by_id(str(inserted_id))
        return DomainRequestResponseSchema.parse_obj(created_request)

    async def get_all_domain_requests(self, status: Optional[DomainRequestStatus] = None, skip: int = 0, limit: int = 100) -> List[DomainRequestResponseSchema]:
        filters = {}
        if status:
            filters["status"] = status.value
        requests_data = await self.domain_request_repo.get_all_domain_requests(filters, skip=skip, limit=limit)
        return [DomainRequestResponseSchema.model_validate(req) for req in requests_data]

    async def approve_domain_request(self, request_id: str, approver_id: str) -> DomainRequestResponseSchema:
        request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not request_data:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.model_validate(request_data) # Sử dụng model_validate
        if domain_request.status != DomainRequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request is not in pending status.")

        # === LOGIC CỐT LÕI CẦN THÊM ===
        # Lặp qua các domain và tạo website mới
        for domain_url in domain_request.domains:
            existing_website = await self.website_repo.get_website_by_root_url(domain_url)
            if not existing_website:
                new_website_data = {
                    "domain": domain_url,
                    "provider_id": domain_request.user_id, # Gán cho provider đã yêu cầu
                    "last_checked_at": datetime.utcnow() # Changed from last_scanned_at to last_checked_at
                    # Các trường khác có thể để giá trị mặc định
                }
                await self.website_repo.create_website(new_website_data)
        # =================================

        # Cập nhật trạng thái yêu cầu
        updated_data = await self.domain_request_repo.update_domain_request(
            request_id,
            {
                "status": DomainRequestStatus.APPROVED.value,
                "approved_by": ObjectId(approver_id),
                "approved_at": datetime.utcnow()
            }
        )
        if not updated_data:
            raise HTTPException(status_code=500, detail="Failed to approve domain request.")
        return DomainRequestResponseSchema.model_validate(updated_data)

    async def reject_domain_request(self, request_id: str, approver_id: str, feedback: Optional[str] = None) -> DomainRequestResponseSchema:
        request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not request_data:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.parse_obj(request_data)
        if domain_request.status != DomainRequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request is not in pending status.")

        updated_data = await self.domain_request_repo.update_domain_request(
            request_id,
            {
                "status": DomainRequestStatus.REJECTED.value,
                "approved_by": ObjectId(approver_id),
                "approved_at": datetime.utcnow(),
                "feedback": feedback
            }
        )
        if not updated_data:
            raise HTTPException(status_code=500, detail="Failed to reject domain request.")
        return DomainRequestResponseSchema.parse_obj(updated_data)
