import asyncio
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from loguru import logger

from src.repositories.website_repository import WebsiteRepository
from src.repositories.violation_repository import ViolationRepository
from src.schemas.website import WebsiteListResponseSchema, WebsiteCreateSchema, WebsiteUpdateSchema, WebsiteResponseSchema, PaginatedWebsiteResponseSchema
from src.schemas.violation import ComplianceAnalysisResponse
from src.models.website import Website
from src.models.user import UserRole
from src.exceptions.custom_exceptions import NotFoundException, BadRequestException

class WebsiteManagementService:
    def __init__(self, website_repo: WebsiteRepository, violation_repo: ViolationRepository):
        self.website_repo = website_repo
        self.violation_repo = violation_repo

    async def get_all_websites(self, user_id: str, user_role: UserRole, search_query: Optional[str] = None, skip: int = 0, limit: int = 100) -> PaginatedWebsiteResponseSchema:
        filters = {}
        if search_query:
            filters["domain"] = {"$regex": search_query, "$options": "i"} # Case-insensitive search

        # Filter by provider_id if the user is a provider
        if user_role == UserRole.PROVIDER:
            filters["provider_id"] = ObjectId(user_id)

        total_count = await self.website_repo.count_websites(filters)
        websites_data = await self.website_repo.get_all_websites(filters, skip=skip, limit=limit)

        response_list = []
        for website_data in websites_data:
            website = Website.model_validate(website_data) # Use model_validate

            policy_status = "unknown"
            if website.is_specific is not None:
                policy_status = "specific" if website.is_specific == 1 else "general"

            # Calculate num_specified_cookies
            num_specified_cookies = len(website.policy_cookies)

            response_list.append(
                WebsiteListResponseSchema(
                    id=website.id,
                    domain=str(website.domain),
                    company_name=website.company_name,
                    policy_status=policy_status,
                    policy_url=website.policy_url,
                    num_specified_cookies=num_specified_cookies,
                    last_checked_at=website.last_checked_at
                )
            )
        return PaginatedWebsiteResponseSchema(
            websites=response_list,
            total_count=total_count,
            page=int(skip / limit) + 1,
            page_size=limit
        )

    async def get_website_by_id(self, website_id: str) -> WebsiteResponseSchema:
        website_data = await self.website_repo.get_website_by_id(website_id)
        if not website_data:
            raise NotFoundException(f"Website with ID {website_id} not found")
        return WebsiteResponseSchema.model_validate(website_data.model_dump())

    async def create_website(self, website_data: WebsiteCreateSchema, user_id: str) -> WebsiteResponseSchema:
        # Check if a website with the same domain already exists for this provider
        existing_website = await self.website_repo.get_by_domain_and_provider(website_data.domain, user_id)
        if existing_website:
            raise BadRequestException(f"Website with domain '{website_data.domain}' already exists for this provider.")

        website_dict = website_data.model_dump()
        website_dict["provider_id"] = ObjectId(user_id) # Assign the current user as the provider
        website_dict["created_at"] = datetime.utcnow()
        website_dict["updated_at"] = datetime.utcnow()

        new_website_id = await self.website_repo.create(website_dict)
        created_website = await self.website_repo.get_website_by_id(new_website_id)
        return WebsiteResponseSchema.model_validate(created_website)

    async def update_website(self, website_id: str, website_data: WebsiteUpdateSchema) -> WebsiteResponseSchema:
        website_dict = website_data.model_dump(exclude_unset=True)
        website_dict["updated_at"] = datetime.utcnow()

        updated_count = await self.website_repo.update(website_id, website_dict)
        if updated_count == 0:
            raise NotFoundException(f"Website with ID {website_id} not found")

        updated_website = await self.website_repo.get_website_by_id(website_id)
        return WebsiteResponseSchema.model_validate(updated_website)

    async def delete_website(self, website_id: str):
        deleted_count = await self.website_repo.delete(website_id)
        if deleted_count == 0:
            raise NotFoundException(f"Website with ID {website_id} not found")

    async def get_website_analytics(self, website_id: str) -> List[ComplianceAnalysisResponse]:
        """
        Retrieves the latest compliance analysis data for a specific website.
        """
        # Get website info
        website = await self.website_repo.get_website_by_id(website_id)
        if not website:
            raise NotFoundException(f"Website with ID {website_id} not found")

        # Lấy danh sách các vi phạm liên quan đến domain của website
        all_violations_data = await self.violation_repo.get_violations_by_website(str(website.domain))
        logger.warning(f"Found {len(all_violations_data)} violations for website {website.domain}")

        if not all_violations_data:
            return [ComplianceAnalysisResponse(
                website_url=str(website.domain),
                analysis_date=datetime.utcnow(),
                total_issues=0,
                compliance_score=100.0,
                issues=[],
                statistics={
                    "by_severity": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
                    "by_category": {"Specific": 0, "General": 0, "Undefined": 0}
                },
                summary={
                    "critical_issues": 0, "high_issues": 0, "undeclared_cookies": [],
                    "declared_cookies": [], "declared_third_parties": [],
                    "third_party_cookies": [], "long_term_cookies": []
                },
                policy_cookies_count=0,
                actual_cookies_count=0,
                details={
                    "declared_cookie_details": [], "undeclared_cookie_details": [],
                    "declared_violating_cookies": [], "declared_compliant_cookies": [],
                    "third_party_domains": {"actual": [], "declared": []},
                    "declared_by_third_party": {}, "expired_cookies_vs_declared": []
                },
                policy_url=website.policy_url or ""
            )]

        # Chuyển từng violation thành ComplianceAnalysisResponse
        results: List[ComplianceAnalysisResponse] = []

        for violation in all_violations_data:
            violation["website_url"] = violation.get("website_url", str(website.domain))
            violation["policy_url"] = str(website.policy_url or "")
            violation["analysis_date"] = violation.get("analyzed_at", datetime.utcnow())
            results.append(ComplianceAnalysisResponse.model_validate(violation))

        return results

    async def trigger_website_analysis(self, payload: dict) -> dict:
        """
        Triggers the analysis process for a website.
        This is a placeholder implementation.
        """
        website_id = payload.get("website_id")
        domain = payload.get("domain")

        if not website_id and not domain:
            raise BadRequestException("Either 'website_id' or 'domain' must be provided in the payload.")

        print(f"Initiating analysis for website_id: {website_id}, domain: {domain}")
        await asyncio.sleep(1)

        return {"status": "Analysis initiated", "website_id": website_id, "domain": domain}
