from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone
from fastapi import HTTPException # Import HTTPException

from src.schemas.domain_request import DomainRequestCreateSchema, DomainRequestResponseSchema, DomainRequestStatus
from src.models.domain_request import DomainRequest
from src.repositories.domain_request_repository import DomainRequestRepository
from src.repositories.website_repository import WebsiteRepository
from src.repositories.user_repository import UserRepository # Import UserRepository
from src.exceptions.custom_exceptions import DomainRequestNotFoundError, UnauthorizedError, DomainAlreadyExistsError
from src.schemas.user import UserPublicSchema # Import UserPublicSchema

class DomainRequestService:
    def __init__(self, domain_request_repo: DomainRequestRepository, website_repo: WebsiteRepository, user_repo: UserRepository):
        self.domain_request_repo = domain_request_repo
        self.website_repo = website_repo
        self.user_repo = user_repo # Inject UserRepository

    async def create_domain_request(self, request_data: DomainRequestCreateSchema, requester_id: str) -> DomainRequestResponseSchema:
        # Check for duplicate domains
        for domain in request_data.domains:
            existing_website = await self.website_repo.get_website_by_root_url(domain)
            if existing_website:
                raise DomainAlreadyExistsError(f"Domain '{domain}' is already registered.")

        new_request = DomainRequest(
            requester_id=ObjectId(requester_id),
            company_name=request_data.company_name,
            domains=request_data.domains,
            purpose=request_data.purpose,
            status=DomainRequestStatus.PENDING,
            created_at=datetime.now(timezone.utc)
        )

        # FIX: Loại bỏ _id khỏi dict trước khi insert
        request_dict = new_request.model_dump(by_alias=True, exclude_none=True)
        # Đảm bảo không có _id trong dict
        request_dict.pop('_id', None)
        request_dict.pop('id', None)  # Cũng loại bỏ 'id' nếu có

        inserted_id = await self.domain_request_repo.create_domain_request(request_dict)
        created_request_data = await self.domain_request_repo.get_domain_request_by_id(str(inserted_id))
        return await self._populate_user_info(created_request_data)

    async def _populate_user_info(self, request_data: dict) -> DomainRequestResponseSchema:
        """Helper to populate requester_info and processed_by_info."""
        domain_request_response = DomainRequestResponseSchema.model_validate(request_data)

        if domain_request_response.requester_id:
            requester = await self.user_repo.get_user_by_id(str(domain_request_response.requester_id))
            if requester:
                domain_request_response.requester_info = UserPublicSchema.model_validate(requester)

        if domain_request_response.processed_by:
            processed_by_user = await self.user_repo.get_user_by_id(str(domain_request_response.processed_by))
            if processed_by_user:
                domain_request_response.processed_by_info = UserPublicSchema.model_validate(processed_by_user)

        return domain_request_response

    async def get_all_domain_requests(self, status: Optional[DomainRequestStatus] = None, skip: int = 0, limit: int = 100) -> List[DomainRequestResponseSchema]:
        filters = {}
        if status:
            filters["status"] = status.value
        requests_data = await self.domain_request_repo.get_all_domain_requests(filters, skip=skip, limit=limit)

        populated_requests = []
        for req_data in requests_data:
            populated_requests.append(await self._populate_user_info(req_data.model_dump(by_alias=True)))
        return populated_requests

    async def approve_domain_request(self, request_id: str, approver_id: str) -> DomainRequestResponseSchema:
        request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not request_data:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.model_validate(request_data) # Sử dụng model_validate
        if domain_request.status != DomainRequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request is not in pending status.")

        # Cập nhật trạng thái yêu cầu
        updated_count = await self.domain_request_repo.update_request_status(
            request_id,
            DomainRequestStatus.APPROVED.value,
            processed_by=ObjectId(str(approver_id))
        )
        if updated_count == 0:
            raise HTTPException(status_code=500, detail="Failed to approve domain request.")

        updated_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not updated_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve approved domain request.")
        return await self._populate_user_info(updated_data)

    async def reject_domain_request(self, request_id: str, approver_id: str, feedback: Optional[str] = None) -> DomainRequestResponseSchema:
        request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not request_data:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.model_validate(request_data)
        if domain_request.status != DomainRequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request is not in pending status.")

        if not feedback: # Ensure feedback is not None or empty
            raise HTTPException(status_code=400, detail="Feedback is required to reject a domain request.")

        updated_count = await self.domain_request_repo.update_request_status(
            request_id,
            DomainRequestStatus.REJECTED.value,
            feedback=feedback,
            processed_by=ObjectId(str(approver_id))
        )
        if updated_count == 0:
            raise HTTPException(status_code=500, detail="Failed to reject domain request.")

        updated_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not updated_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve rejected domain request.")
        return await self._populate_user_info(updated_data)
