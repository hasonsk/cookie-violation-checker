import re
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone
from src.schemas.domain_request import DomainRequestCreateSchema, DomainRequestResponseSchema, DomainRequestStatus, DomainRequestUpdateSchema
from src.models.domain_request import DomainRequest
from src.repositories.domain_request_repository import DomainRequestRepository
from src.services.website_management_service.website_management_service import WebsiteManagementService
from src.repositories.website_repository import WebsiteRepository
from src.repositories.user_repository import UserRepository
from src.exceptions.custom_exceptions import DomainRequestNotFoundError, UnauthorizedError, DomainAlreadyExistsError, BadRequestException, InternalServerError
from src.schemas.user import UserPublicSchema, UserRole
from src.utils.validation_utils import DOMAIN_REGEX

class DomainRequestService:
    def __init__(self, domain_request_repo: DomainRequestRepository, website_repo: WebsiteRepository, user_repo: UserRepository):
        self.domain_request_repo = domain_request_repo
        self.website_repo = website_repo
        self.user_repo = user_repo

    async def _validate_domains(self, domains: List[str], exclude_request_id: Optional[str] = None) -> List[str]:
        invalid_domains = []
        existing_domains = []

        # for domain in domains:
        #     if not re.match(DOMAIN_REGEX, domain):
        #         invalid_domains.append(domain)
        #         continue

        #     # Check if domain exists in websites collection
        #     existing_website = await self.website_repo.get_website_by_root_url(domain)
        #     if existing_website:
        #         existing_domains.append(domain)
        #         continue

        #     existing_domain_request = await self.domain_request_repo.get_domain_request_by_domain_and_status(
        #         domain, [DomainRequestStatus.PENDING, DomainRequestStatus.APPROVED], exclude_request_id
        #     )
        #     if existing_domain_request:
        #         existing_domains.append(domain)

        # if invalid_domains or existing_domains:
        #     error_detail = []
        #     if invalid_domains:
        #         error_detail.append(f"Các domain sau không hợp lệ: {', '.join(invalid_domains)}")
        #     if existing_domains:
        #         error_detail.append(f"Các domain sau đã tồn tại hoặc đang chờ duyệt: {', '.join(existing_domains)}")
        #     raise BadRequestException(". ".join(error_detail))
        # return domains

    async def create_domain_request(self, request_data: DomainRequestCreateSchema, requester_id: str, requester_username: str, requester_email: str) -> DomainRequestResponseSchema:
        await self._validate_domains(request_data.domains)

        new_request = DomainRequest(
            requester_id=ObjectId(requester_id),
            requester_username=requester_username,
            requester_email=requester_email,
            domains=request_data.domains,
            purpose=request_data.purpose,
            status=DomainRequestStatus.PENDING,
            # created_at and updated_at are handled by default_factory in BaseMongoDBModel
            # but we ensure they are explicitly included in the dict for insertion
        )

        request_dict = new_request.model_dump(by_alias=True, exclude_none=False) # Do not exclude_none here
        request_dict['created_at'] = datetime.now(timezone.utc)
        request_dict['updated_at'] = datetime.now(timezone.utc)
        request_dict.pop('_id', None) # Remove _id if present from model_dump
        request_dict.pop('id', None) # Remove id if present from model_dump

        inserted_id = await self.domain_request_repo.create_domain_request(request_dict)
        created_request_data = await self.domain_request_repo.get_domain_request_by_id(str(inserted_id))
        return await self._populate_user_info(created_request_data)

    async def update_domain_request(self, request_id: str, request_data: DomainRequestUpdateSchema, requester_id: str) -> DomainRequestResponseSchema:
        existing_request = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not existing_request:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.model_validate(existing_request)
        if str(domain_request.requester_id) != requester_id:
            raise UnauthorizedError("You are not authorized to update this domain request.")
        if domain_request.status != DomainRequestStatus.PENDING:
            raise BadRequestException("Only pending domain requests can be updated.")

        update_data = request_data.model_dump(exclude_unset=True)

        if "domains" in update_data and update_data["domains"]:
            await self._validate_domains(update_data["domains"], exclude_request_id=request_id)

        update_data["updated_at"] = datetime.now(timezone.utc) # Ensure updated_at is set on update

        updated_count = await self.domain_request_repo.update_domain_request(request_id, update_data)
        if updated_count == 0:
            raise InternalServerError("Failed to update domain request.")

        updated_request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        return await self._populate_user_info(updated_request_data)

    async def get_latest_domain_request_by_user(self, user_id: str) -> Optional[DomainRequestResponseSchema]:
        request_data = await self.domain_request_repo.get_latest_domain_request_by_user(user_id)
        if request_data:
            return await self._populate_user_info(request_data)
        return None

    async def _populate_user_info(self, request_data: dict) -> DomainRequestResponseSchema:
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

    async def get_all_domain_requests(self, status: Optional[DomainRequestStatus] = None, requester_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[DomainRequestResponseSchema]:
        filters = {}
        if status:
            filters["status"] = status.value
        if requester_id:
            filters["requester_id"] = ObjectId(requester_id)
        requests_data = await self.domain_request_repo.get_all_domain_requests(filters, skip=skip, limit=limit)

        populated_requests = []
        for req_data in requests_data:
            populated_requests.append(await self._populate_user_info(req_data.model_dump(by_alias=True)))
        return populated_requests

    async def approve_domain_request(self, request_id: str, approver_id: str, website_management_service: WebsiteManagementService) -> DomainRequestResponseSchema:
        request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not request_data:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.model_validate(request_data)
        if domain_request.status != DomainRequestStatus.PENDING:
            raise BadRequestException("Request is not in pending status.")

        from src.schemas.website import WebsiteCreateSchema
        # website_management_service will be passed as an argument to this method
        # This avoids circular dependency issues.

        # for domain in domain_request.domains:
        #     website_create_schema = WebsiteCreateSchema(domain=domain, is_approved=True, original_content="N/A", is_specific=0) # Add required fields
        #     await website_management_service.create_website(website_create_schema, str(domain_request.requester_id))

        # Update domain request status
        updated_count = await self.domain_request_repo.update_request_status(
            request_id,
            DomainRequestStatus.APPROVED.value,
            processed_by=ObjectId(str(approver_id))
        )
        if updated_count == 0:
            raise InternalServerError("Failed to approve domain request.")

        # Update provider's approved_by_admin status
        await self.user_repo.update_user(str(domain_request.requester_id), {"approved_by_admin": True})

        updated_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not updated_data:
            raise InternalServerError("Failed to retrieve approved domain request.")
        return await self._populate_user_info(updated_data)

    async def delete_domain_request(self, request_id: str, current_user: UserPublicSchema) -> None:
        request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not request_data:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.model_validate(request_data)

        # Only admin, manager, provider, or the requester can delete requests
        if current_user.role.value not in [UserRole.ADMIN.value, UserRole.MANAGER.value, UserRole.PROVIDER.value] and \
           str(domain_request.requester_id) != current_user.id:
            raise UnauthorizedError("You are not authorized to delete this domain request.")

        deleted_count = await self.domain_request_repo.delete_domain_request(request_id)
        if deleted_count == 0:
            raise InternalServerError("Failed to delete domain request.")

    async def reject_domain_request(self, request_id: str, approver_id: str, feedback: Optional[str] = None) -> DomainRequestResponseSchema:
        request_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not request_data:
            raise DomainRequestNotFoundError()

        domain_request = DomainRequest.model_validate(request_data)
        if domain_request.status != DomainRequestStatus.PENDING:
            raise BadRequestException("Request is not in pending status.")

        if not feedback:
            raise BadRequestException("Feedback is required to reject a domain request.")

        updated_count = await self.domain_request_repo.update_request_status(
            request_id,
            DomainRequestStatus.REJECTED.value,
            feedback=feedback,
            processed_by=ObjectId(str(approver_id))
        )
        if updated_count == 0:
            raise InternalServerError("Failed to reject domain request.")

        updated_data = await self.domain_request_repo.get_domain_request_by_id(request_id)
        if not updated_data:
            raise InternalServerError("Failed to retrieve rejected domain request.")
        return await self._populate_user_info(updated_data)
